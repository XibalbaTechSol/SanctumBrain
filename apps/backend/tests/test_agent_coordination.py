import asyncio
import os
import sys
from langchain_core.messages import HumanMessage

# Add app directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.join(current_dir, "..")
sys.path.append(backend_root)

# Mock some env vars for stability
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["OLLAMA_HOST"] = "http://localhost:11434"
os.environ["GOOGLE_API_VERSION"] = "v1"

from app.graph import sanctum_app
from app.db.models import Project, Area
from tortoise import Tortoise

# Mock RAG to avoid quota/connection issues during coordination test
import app.rag
app.rag.retrieve_context = lambda x: {
    "context_strings": ["Mock context for testing"],
    "visualization": {"query": x, "retrieved_nodes": [], "latency_ms": 10}
}

async def init_db():
    await Tortoise.init(
        db_url='sqlite://:memory:',
        modules={'models': ['app.db.models']}
    )
    await Tortoise.generate_schemas()

async def test_pii_redaction():
    print("\n--- 🛡️ Testing PII Redaction (SLM-based) ---")
    state = {
        "messages": [HumanMessage(content="My secret email is john.doe@example.com and my name is John Doe.")],
        "context": {"security_level": "PRIVACY_FIRST", "device_id": "test-device"},
        "reasoning_steps": []
    }
    
    # Run the graph
    config = {"configurable": {"thread_id": "test-pii"}}
    result = await sanctum_app.ainvoke(state, config)
    
    last_msg = result["messages"][-1].content
    print(f"Original Input: {state['messages'][0].content}")
    print(f"Redacted Output (in state): {result['messages'][0].content}")
    
    if "john.doe@example.com" not in result['messages'][0].content:
        print("[✓] Email Redacted successfully.")
    else:
        print("[✗] Email NOT Redacted.")

async def test_para_crud():
    print("\n--- 🏗️ Testing PARA CRUD Operations ---")
    
    # 1. Create Project
    # We use a very explicit prompt to ensure the real SLM/LLM understands the intent
    print("[*] Testing Create Project...")
    state = {
        "messages": [HumanMessage(content="Action: Create. Type: Project. Title: 'Sanctum Phase 4'. Goal: 'Implement multi-agent coordination'.")],
        "context": {"security_level": "BALANCED", "device_id": "test-device"},
        "reasoning_steps": []
    }
    
    config = {"configurable": {"thread_id": "test-para-1"}}
    result = await sanctum_app.ainvoke(state, config)
    
    projects = await Project.all()
    print(f"Found {len(projects)} projects in DB.")
    for p in projects:
        print(f" - Project: {p.title} (ID: {p.id})")
        
    if any("Sanctum Phase 4" in p.title for p in projects):
        print("[✓] Project created successfully.")
    else:
        print("[✗] Project creation FAILED.")

    # 2. Update Project
    if projects:
        proj_id = projects[0].id
        print(f"[*] Testing Update Project (ID: {proj_id})...")
        state = {
            "messages": [HumanMessage(content=f"Update project {proj_id} status to COMPLETED.")],
            "context": {"security_level": "BALANCED", "device_id": "test-device"},
            "reasoning_steps": []
        }
        
        result = await sanctum_app.ainvoke(state, config)
        updated_proj = await Project.get(id=proj_id)
        print(f" - Updated Status: {updated_proj.status}")
        
        if updated_proj.status == "COMPLETED":
            print("[✓] Project status updated successfully.")
        else:
            print("[✗] Project status update FAILED.")

async def main():
    await init_db()
    try:
        await test_pii_redaction()
        await test_para_crud()
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
