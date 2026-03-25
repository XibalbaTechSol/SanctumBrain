import os
import time
import json
import hashlib
from typing import List, Any, Dict
from redis import Redis
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_postgres import PGVector
from .utils import log_event

# Load .env file
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sanctum:sanctum_pass@127.0.0.1:5432/sanctum_db")
if DATABASE_URL.startswith("postgres://"):
    CONNECTION = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    CONNECTION = DATABASE_URL
COLLECTION_NAME = "sanctum_memory"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis for caching
try:
    redis_client = Redis.from_url(REDIS_URL)
    log_event("SYSTEM", "Knowledge Engine: Redis Cache Connected")
except Exception as e:
    print(f"[*] Failed to connect Redis for RAG cache: {e}")
    redis_client = None

# Initialize embeddings
try:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("No API Key")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    log_event("SYSTEM", "Knowledge Engine: Vector Embeddings Ready")
except Exception:
    log_event("SYSTEM", "Knowledge Engine: MOCK EMBEDDINGS (No API Key)")
    class MockEmbeddings:
        def embed_query(self, text): return [0.1] * 1536
        def embed_documents(self, texts): return [[0.1] * 1536 for _ in texts]
    embeddings = MockEmbeddings()

def get_vector_store():
    """Initializes and returns the PGVector store."""
    try:
        # Use simple langchain-postgres implementation
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=CONNECTION,
            use_jsonb=True,
        )
        return vector_store
    except Exception as e:
        print(f"[!] Vector Store Connection Error: {e}")
        log_event("ERROR", f"PGVector Connection failed: {e}")
        return None

def ingest_document(file_path: str):
    """Loads and embeds a document into PGVector."""
    print(f"[*] Ingesting document: {file_path}")
    try:
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        vector_store = get_vector_store()
        if vector_store:
            vector_store.add_documents(splits)
            log_event("SYSTEM", f"Ingested {len(splits)} chunks into PGVector")
        else:
            print("[!] Failed to ingest: Vector Store unavailable.")
    except Exception as e:
        print(f"[!] Ingestion Error: {e}")

def ingest_text(content: str, metadata: Dict[str, Any] = None):
    """Directly ingests a text string into PGVector."""
    if not content: return
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.create_documents([content], metadatas=[metadata or {}])
        vector_store = get_vector_store()
        if vector_store:
            vector_store.add_documents(docs)
            log_event("SYSTEM", f"Ingested text content into PGVector")
    except Exception as e:
        print(f"[!] Ingestion Error: {e}")

def retrieve_context(query: str, k: int = 3) -> dict:
    """Retrieves relevant context from PGVector."""
    if redis_client:
        query_hash = hashlib.md5(f"{query}_{k}".encode()).hexdigest()
        cache_key = f"rag_cache:{query_hash}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

    start_time = time.time()
    vector_store = get_vector_store()
    results = []
    scores = []
    
    if vector_store:
        try:
            results_with_scores = vector_store.similarity_search_with_score(query, k=k)
            results = [doc for doc, score in results_with_scores]
            scores = [score for doc, score in results_with_scores]
        except Exception as e:
            print(f"[!] RAG Retrieval Error: {e}")

    if not results:
        results = [Document(page_content="System: No external context found in Sanctum Memory.")]
        scores = [0.0]

    latency_ms = int((time.time() - start_time) * 1000)
    visualization_data = {
        "query": query,
        "retrieved_nodes": [
            {
                "id": f"chunk_{i}",
                "content": doc.page_content[:100] + "...",
                "similarity": 1.0 - float(scores[i]) if i < len(scores) else 0.0,
                "metadata": getattr(doc, 'metadata', {})
            } for i, doc in enumerate(results)
        ],
        "latency_ms": latency_ms
    }
    
    final_result = {
        "context_strings": [doc.page_content for doc in results],
        "visualization": visualization_data
    }

    if redis_client:
        redis_client.setex(cache_key, 3600, json.dumps(final_result))

    return final_result
