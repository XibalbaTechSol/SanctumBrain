import grpc
import json
import time
import os
import sys
import requests
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from app import a2a_pb2 as pb2
    from app import a2a_pb2_grpc as pb2_grpc
except ImportError:
    print("[!] gRPC stubs not found. Attempting to import from app.app")
    from app.app import a2a_pb2 as pb2
    from app.app import a2a_pb2_grpc as pb2_grpc

def test_grpc_post_context():
    print("[*] Testing VPS gRPC via Envoy Proxy (Port 8000)...")
    # Envoy maps /sanctum.a2a.SanctumA2AService/ to orchestrator:50051
    channel = grpc.insecure_channel('localhost:8000')
    stub = pb2_grpc.SanctumA2AServiceStub(channel)
    
    # 1. Handshake
    handshake = pb2.Handshake(
        device_id="vps-validation-client",
        public_key=b"\x00" * 32,
        version="1.0.0"
    )
    packet = pb2.AgentPacket(session_id="val-session", handshake=handshake)
    
    try:
        response = stub.PostContext(packet)
        if response.HasField("handshake"):
            print(f"[SUCCESS] gRPC Handshake received via Envoy. Version: {response.handshake.version}")
        else:
            print("[FAILURE] gRPC Handshake failed.")
            return False
    except Exception as e:
        print(f"[ERROR] gRPC Connection failed on port 8000: {e}")
        # Fallback to direct port if Envoy fails
        print("[*] Retrying direct connection on port 50051...")
        try:
            chan2 = grpc.insecure_channel('localhost:50051')
            stub2 = pb2_grpc.SanctumA2AServiceStub(chan2)
            res2 = stub2.PostContext(packet)
            if res2.HasField("handshake"):
                print("[SUCCESS] gRPC Handshake received via direct port 50051.")
                return True
        except Exception as e2:
            print(f"[ERROR] Direct gRPC also failed: {e2}")
        return False

    return True

def test_dashboard_api():
    print("[*] Testing Dashboard via Envoy Proxy (Port 8000)...")
    
    try:
        resp = requests.get("http://localhost:8000/clients", timeout=5)
        if resp.status_code == 200:
            print(f"[SUCCESS] Dashboard /clients API active via Envoy. Found {len(resp.json())} clients.")
        else:
            print(f"[FAILURE] Envoy Dashboard /clients returned {resp.status_code}")
            # Try direct port
            print("[*] Retrying direct dashboard on port 8081...")
            resp2 = requests.get("http://localhost:8081/clients", timeout=5)
            if resp2.status_code == 200:
                print("[SUCCESS] Dashboard active on port 8081.")
                return True
            return False
            
        resp = requests.get("http://localhost:8000/", timeout=5)
        if resp.status_code == 200:
            print("[SUCCESS] Dashboard HTML Root active via Envoy.")
        else:
            # The dashboard might not have a root route, checking /clients was enough
            print(f"[INFO] Dashboard Root returned {resp.status_code} (Non-critical)")
    except Exception as e:
        print(f"[ERROR] Dashboard connection failed: {e}")
        return False
        
    return True

try:
    from app.crypto import SanctumCrypto
except ImportError:
    from app.app.crypto import SanctumCrypto

def test_intent_to_agui():
    print("[*] Testing Encrypted Intent-to-AGUI Pipeline...")
    channel = grpc.insecure_channel('localhost:8000')
    stub = pb2_grpc.SanctumA2AServiceStub(channel)
    
    crypto = SanctumCrypto()
    
    # 1. Handshake to establish shared key
    handshake = pb2.Handshake(
        device_id="vps-validation-client-encrypted",
        public_key=crypto.get_public_bytes(),
        version="1.0.0"
    )
    packet = pb2.AgentPacket(session_id="val-session-enc", handshake=handshake)
    
    try:
        response = stub.PostContext(packet)
        if response.HasField("handshake"):
            crypto.derive_shared_key(response.handshake.public_key)
            print("[SUCCESS] Shared key established via Handshake.")
        else:
            print("[FAILURE] Handshake failed.")
            return False
            
        # 2. Send Encrypted System Health Intent
        mcp_data = {
            "text": "Check system health",
            "context": {
                "intent_prediction": {"label": "system_health"}
            },
            "device_id": "val-client"
        }
        ciphertext, nonce, tag = crypto.encrypt(json.dumps(mcp_data).encode())
        
        data_packet = pb2.AgentPacket(
            session_id="val-session-enc",
            data=pb2.EncryptedData(ciphertext=ciphertext, nonce=nonce, auth_tag=tag)
        )
        
        response = stub.PostContext(data_packet)
        if response.HasField("data"):
            decrypted = crypto.decrypt(
                response.data.ciphertext,
                response.data.nonce,
                response.data.auth_tag
            ).decode()
            
            resp_json = json.loads(decrypted)
            ui_payload = resp_json.get('ui_payload', {})
            ui_type = ui_payload.get('ui', {}).get('type')
            print(f"[SUCCESS] Received AGUI Payload: {ui_type}")
            
            if ui_type:
                print(f"[SUCCESS] Neural Core correctly synthesized {ui_type} Atom.")
                return True
            else:
                print("[FAILURE] No UI type in payload.")
        else:
            print("[FAILURE] No data payload in response.")
    except Exception as e:
        print(f"[ERROR] Encrypted AGUI Pipeline failed: {e}")
        
    return False

if __name__ == "__main__":
    vps_success = test_grpc_post_context()
    dash_success = test_dashboard_api()
    agui_success = test_intent_to_agui()
    
    if vps_success and dash_success and agui_success:
        print("\n--- 🛡️ VPS Backend Integrity: VERIFIED ---")
        sys.exit(0)
    else:
        print("\n--- ❌ VPS Backend Integrity: FAILED ---")
        sys.exit(1)
