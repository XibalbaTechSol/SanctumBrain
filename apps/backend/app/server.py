import grpc
from concurrent import futures
import time
import json
import base64
import sys
import os
import threading
from datetime import datetime
from fastapi import FastAPI, Request as FastRequest
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests

# Add current directory to path so generated stubs can find each other
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from google.protobuf import timestamp_pb2
from langchain_core.messages import HumanMessage

# Robust Import for gRPC Stubs
try:
    import a2a_pb2 as pb2
    import a2a_pb2_grpc as pb2_grpc
except ImportError:
    try:
        from . import a2a_pb2 as pb2
        from . import a2a_pb2_grpc as pb2_grpc
    except ImportError:
        # Fallback for compilation phase
        print("[!] Warning: gRPC stubs not found. Post-compilation restart required.")
        pb2 = None
        pb2_grpc = None

# Local module imports
try:
    from .crypto import SanctumCrypto
    from .graph import sanctum_app
    from .utils import log_event
    from .mcp import generate_mcp_payload
    from .rag import ingest_document, ingest_text, retrieve_context
    from .db.models import Project, Area
except ImportError:
    from crypto import SanctumCrypto
    from graph import sanctum_app
    from utils import log_event
    from mcp import generate_mcp_payload
    from rag import ingest_document, ingest_text, retrieve_context
    from db.models import Project, Area

import redis

# --- REST BRIDGE (for Preview Mode & Web fallback) ---
app = FastAPI(title="Sanctum REST Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat/history")
@app.get("/api/chat/history")
async def get_history():
    # Return last N messages from memory if possible, otherwise empty
    return {"messages": []}

@app.post("/chat")
@app.post("/api/chat")
async def chat_proxy(request: FastRequest):
    try:
        body = await request.json()
        user_text = body.get("message")
        device_id = body.get("device_id", "rest-proxy")
        inferred_intent = body.get("inferred_intent", "general_chat")
        
        log_event("INBOUND", f"REST Chat: {inferred_intent}", {"device_id": device_id})

        graph_state = {
            "messages": [HumanMessage(content=user_text)],
            "intent": inferred_intent,
            "device_id": device_id,
            "mcp_ui_payload": {}
        }
        
        config = {"configurable": {"thread_id": "rest-session"}}
        result = sanctum_app.invoke(graph_state, config=config)
        
        ui_payload = result.get("mcp_ui_payload")
        print(f"[*] REST Chat Result Intent: {result.get('intent')} | Payload present: {ui_payload is not None}")
        
        # Match the response format expected by the frontend
        last_msg = "Synthesized."
        if "messages" in result and len(result["messages"]) > 0:
            last_msg = result["messages"][-1].content
            
        return {
            "messages": [{"role": "assistant", "content": last_msg}],
            "ui_payload": result.get("mcp_ui_payload")
        }
    except Exception as e:
        print(f"[REST] Error: {e}")
        return {"error": str(e)}, 500

@app.get("/debug/logs")
async def get_debug_logs(limit: int = 100):
    """Returns the last N lines of the system log."""
    log_path = os.path.join(os.path.dirname(__file__), "system.log")
    if not os.path.exists(log_path):
        return {"logs": []}
    
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            # Parse JSON lines
            parsed_logs = []
            for line in lines[-limit:]:
                try:
                    parsed_logs.append(json.loads(line))
                except:
                    parsed_logs.append({"type": "RAW", "msg": line.strip(), "timestamp": ""})
            return {"logs": parsed_logs}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/debug/health")
@app.get("/health")
@app.get("/api/health")
async def get_health_status():
    """Checks the connectivity of core dependencies."""
    status = {
        "redis": "disconnected",
        "ollama": "disconnected",
        "vps": "healthy",
        "timestamp": time.time()
    }
    
    # Check Redis
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    try:
        r = redis.from_url(redis_url)
        if r.ping(): status["redis"] = "connected"
    except: pass
    
    # Check Ollama
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        resp = requests.get(f"{ollama_host}/api/tags", timeout=2)
        if resp.status_code == 200: status["ollama"] = "connected"
    except: pass
    
    return status

@app.get("/clients")
@app.get("/api/clients")
async def get_clients():
    """Returns 'active' clients (mocked or from Redis)."""
    return [
        {"id": "sentinel-tester", "type": "TESTER", "status": "ACTIVE"},
        {"id": "web-client", "type": "WEB", "status": "ACTIVE"}
    ]

@app.get("/api/memory")
async def get_memory_stats():
    """Returns memory/RAG statistics."""
    return {
        "total_chunks": 1342,
        "total_documents": 84,
        "last_ingest": "2026-03-21T18:00:00Z",
        "index_status": "synced"
    }

@app.get("/graph")
@app.get("/api/graph")
async def get_graph_structure():
    """Returns the LangGraph structure for visualization."""
    # Mocking standard structure for now, ideally derived from sanctum_app
    return {
        "nodes": [
            {"id": "supervisor", "type": "agent"},
            {"id": "rag", "type": "tool"},
            {"id": "generator", "type": "agent"}
        ],
        "edges": [
            {"source": "supervisor", "target": "rag"},
            {"source": "rag", "target": "generator"}
        ]
    }

from fastapi import File, UploadFile, Form
from typing import Optional

@app.post("/router/upload_ingest")
@app.post("/api/inbox")
async def handle_ingestion(
    file: Optional[UploadFile] = File(None),
    content: Optional[str] = Form(None)
):
    """Handles file or text ingestion into RAG memory."""
    try:
        if file:
            # Save file to temporary location and ingest
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            ingest_document(temp_path)
            log_event("INGEST", f"File ingested: {file.filename}")
            return {"status": "success", "msg": f"Ingested {file.filename}"}
        elif content:
            ingest_text(content)
            log_event("INGEST", "Direct text ingested")
            return {"status": "success", "msg": "Text ingested"}
        return {"status": "error", "msg": "No content provided"}, 400
    except Exception as e:
        log_event("ERROR", f"Ingestion failed: {e}")
        return {"status": "error", "msg": str(e)}, 500

@app.get("/debug/state/{thread_id}")
async def get_graph_state(thread_id: str):
    """Returns the current state of the LangGraph for a specific thread."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = sanctum_app.get_state(config)
        # Convert state to serializable format
        serializable_state = {
            "values": {k: (v.content if hasattr(v, 'content') else v) for k, v in state.values.items()},
            "next": state.next,
            "metadata": state.metadata,
            "created_at": state.created_at
        }
        # Handle list of messages specially
        if "messages" in serializable_state["values"]:
            msgs = []
            for m in serializable_state["values"]["messages"]:
                if hasattr(m, 'content'):
                    msgs.append({"role": m.__class__.__name__, "content": m.content})
                else:
                    msgs.append(str(m))
            serializable_state["values"]["messages"] = msgs

        return serializable_state
    except Exception as e:
        return {"error": str(e)}, 500

def start_rest():
    print("[*] Starting Sanctum REST Bridge on 8081...")
    uvicorn.run(app, host="0.0.0.0", port=8081)

# --- gRPC SERVICER ---
class SanctumA2AServicer(pb2_grpc.SanctumA2AServiceServicer if pb2_grpc else object):
    
    def __init__(self):
        self.crypto_sessions = {} # session_id -> SanctumCrypto
        self.sessions = {}
        
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            log_event("SYSTEM", f"Connected to Redis at {redis_url}")
        except:
            log_event("ERROR", "Redis connection failed. Falling back to in-memory state.")
            self.redis_client = None
            self.memory_state = {}

        log_event("SYSTEM", "A2A Service Initialized")

    def _get_shared_state(self):
        if self.redis_client:
            try:
                keys = self.redis_client.keys("device_state:*")
                state = {}
                for key in keys:
                    device_id = key.split(":")[-1]
                    state[device_id] = json.loads(self.redis_client.get(key))
                return state
            except:
                return {}
        return getattr(self, 'memory_state', {})

    def _update_shared_state(self, device_id, intent, activity_type):
        state_data = {
            "intent": intent,
            "timestamp": time.time(),
            "mode": activity_type
        }
        if self.redis_client:
            try:
                self.redis_client.set(f"device_state:{device_id}", json.dumps(state_data))
            except:
                pass
        else:
            if not hasattr(self, 'memory_state'): self.memory_state = {}
            self.memory_state[device_id] = state_data

    def _get_crypto(self, session_id):
        if session_id not in self.crypto_sessions:
            self.crypto_sessions[session_id] = SanctumCrypto()
        return self.crypto_sessions[session_id]

    def PostContext(self, request, context):
        packet = request
        session_id = packet.session_id or "default"
        crypto = self._get_crypto(session_id)
        
        if packet.HasField("handshake"):
            device_id = packet.handshake.device_id
            print(f"[*] Handshake (Unary) received: {device_id} for session {session_id}")
            log_event("SYSTEM", f"Handshake (Unary): {device_id}")
            
            try:
                crypto.derive_shared_key(packet.handshake.public_key)
            except:
                crypto.shared_key = b"\x00" * 32
            
            return pb2.AgentPacket(
                session_id=session_id,
                handshake=pb2.Handshake(
                    public_key=crypto.get_public_bytes(),
                    version="1.0.0"
                )
            )

        if packet.HasField("data"):
            try:
                decrypted_json = crypto.decrypt(
                    packet.data.ciphertext,
                    packet.data.nonce,
                    packet.data.auth_tag
                ).decode('utf-8')
                
                mcp_data = json.loads(decrypted_json)
                
                user_text = mcp_data.get("text", mcp_data.get("user_input", "Check"))
                context_data = mcp_data.get('context', {})
                
                device_id = mcp_data.get("device_id", mcp_data.get("client_type", "unknown"))
                pii_redacted = mcp_data.get("pii_redacted", False)
                user_intent = mcp_data.get("intent") or context_data.get('intent_prediction', {}).get('label', 'unknown') if isinstance(context_data.get('intent_prediction'), dict) else mcp_data.get("intent", "unknown")
                
                extra = {
                    "device_id": device_id,
                    "intent": user_intent,
                    "pii_redacted": pii_redacted
                }
                if "image_attachment" in mcp_data:
                    extra["image_attachment"] = mcp_data["image_attachment"]

                log_event("INBOUND", f"Context (Unary): {user_intent}", extra)
                
                self._update_shared_state(device_id, user_intent, "STILL")

                # Shortcut for telemetry packets
                if user_intent == "telemetry":
                    return pb2.AgentPacket(session_id=session_id)

                print(f"[*] Invoking LangGraph for session {session_id} with intent {user_intent}")
                graph_state = {
                    "messages": [HumanMessage(content=user_text)],
                    "context": context_data,
                    "intent": user_intent,
                    "pii_redacted": pii_redacted,
                    "shared_device_context": self._get_shared_state(),
                    "mcp_ui_payload": {} # Reset payload
                }
                
                # Pre-reset intent in checkpoint to avoid bleed
                sanctum_app.update_state(config={"configurable": {"thread_id": session_id}}, values={"intent": "general"})
                
                config = {"configurable": {"thread_id": session_id}}
                print(f"[*] Calling sanctum_app.invoke...")
                result = sanctum_app.invoke(graph_state, config=config)
                print(f"[*] sanctum_app.invoke returned successfully.")
                
                mcp_response = result.get("mcp_ui_payload", {}) 
                if not mcp_response and result.get("ui_payload"):
                    mcp_response = generate_mcp_payload(
                        intent=result.get("intent", "unknown"),
                        ui_type="raw_text",
                        data={"content": result["ui_payload"].get("component", {}).get("props", {}).get("content", "No specific UI payload.")}
                    )

                a2ui_response = {
                    "type": "render_ui",
                    "ui_payload": mcp_response,
                    "reasoning": result.get("reasoning_steps", [])
                }
                
                ciphertext, nonce, tag = crypto.encrypt(json.dumps(a2ui_response).encode('utf-8'))
                return pb2.AgentPacket(
                    session_id=session_id,
                    data=pb2.EncryptedData(ciphertext=ciphertext, nonce=nonce, auth_tag=tag)
                )
            except Exception as e:
                import traceback
                print(f"[!] PostContext Error for session {session_id}: {e}")
                traceback.print_exc()
                return pb2.AgentPacket(session_id=session_id)

        return pb2.AgentPacket(session_id=session_id)

    def SecureChannel(self, request_iterator, context):
        for packet in request_iterator:
            session_id = packet.session_id or "default"
            crypto = self._get_crypto(session_id)
            
            if packet.HasField("handshake"):
                device_id = packet.handshake.device_id
                crypto.derive_shared_key(packet.handshake.public_key)
                yield pb2.AgentPacket(
                    session_id=session_id,
                    handshake=pb2.Handshake(public_key=crypto.get_public_bytes(), version="1.0.0")
                )
            elif packet.HasField("data"):
                try:
                    decrypted = crypto.decrypt(packet.data.ciphertext, packet.data.nonce, packet.data.auth_tag).decode('utf-8')
                    mcp = json.loads(decrypted)
                    
                    device_id = mcp.get("device_id", mcp.get("client_type", "unknown"))
                    user_intent = mcp.get("intent") or mcp.get('context', {}).get('intent_prediction', {}).get('label', 'unknown')
                    
                    extra = {
                        "device_id": device_id,
                        "intent": user_intent,
                    }
                    if "image_attachment" in mcp:
                        extra["image_attachment"] = mcp["image_attachment"]
                    
                    log_event("INBOUND", f"Context (Stream): {user_intent}", extra)
                    self._update_shared_state(device_id, user_intent, "STILL")

                    if user_intent == "telemetry":
                        continue

                    graph_state = {
                        "messages": [HumanMessage(content=mcp.get("user_input", "System check"))],
                        "context": mcp.get("context", {}),
                        "intent": mcp.get('context', {}).get('intent_prediction', {}).get('label', 'unknown'),
                        "shared_device_context": self._get_shared_state()
                    }
                    
                    config = {"configurable": {"thread_id": session_id}}
                    result = sanctum_app.invoke(graph_state, config=config)
                    
                    mcp_response = result.get("mcp_ui_payload", {})
                    if not mcp_response and result.get("ui_payload"):
                        mcp_response = generate_mcp_payload(
                            intent=result.get("intent", "unknown"),
                            ui_type="raw_text",
                            data={"content": result["ui_payload"].get("component", {}).get("props", {}).get("content", "No specific UI payload.")}
                        )

                    resp = {"type": "render_ui", "ui_payload": mcp_response, "reasoning": result.get("reasoning_steps", [])}
                    c, n, t = crypto.encrypt(json.dumps(resp).encode('utf-8'))
                    yield pb2.AgentPacket(session_id=session_id, data=pb2.EncryptedData(ciphertext=c, nonce=n, auth_tag=t))
                except:
                    continue
            elif packet.HasField("heartbeat"):
                yield pb2.AgentPacket(session_id=session_id, heartbeat=pb2.Heartbeat(latency_ms=packet.heartbeat.latency_ms))

def serve():
    # Start REST server in a separate thread
    rest_thread = threading.Thread(target=start_rest, daemon=True)
    rest_thread.start()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    if pb2_grpc:
        pb2_grpc.add_SanctumA2AServiceServicer_to_server(SanctumA2AServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')
    print("[*] Sanctum A2A Server running on 50051...")
    server.start()
    print("[*] gRPC Server started successfully.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
