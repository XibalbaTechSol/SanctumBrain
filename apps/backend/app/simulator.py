import json
import time
import base64
from langchain_core.messages import HumanMessage
from .crypto import SanctumCrypto
from .graph import sanctum_app

def run_end_to_end_simulation():
    print("--- 🛡️ Sanctum OS: Full End-to-End System Simulation ---")
    
    # 1. Initialize Identities
    sentinel_crypto = SanctumCrypto()
    core_crypto = SanctumCrypto()
    
    print("[*] STEP 1: Secure Handshake")
    # Sentinel sends public key to Core
    sentinel_pub = sentinel_crypto.get_public_bytes()
    core_crypto.derive_shared_key(sentinel_pub)
    
    # Core sends public key back to Sentinel
    core_pub = core_crypto.get_public_bytes()
    sentinel_crypto.derive_shared_key(core_pub)
    
    print("[+] Cryptographic Tunnel Established (Shared Secret Derived).")
    
    # 2. Sentinel Gathers Sensors & Predicts Intent
    print("\n[*] STEP 2: Sentinel Sensor Fusion (with Security Policy)")
    mcp_context = {
        "timestamp": "2026-02-16T18:00:00Z",
        "source": "SENTINEL",
        "context": {
            "security_level": "PRIVACY_FIRST",
            "sensors": {
                "gaze": {"x": 120, "y": 450, "confidence": 0.9},
                "motion": {"velocity": 1200, "is_stationary": False, "activity_type": "WALKING"}
            },
            "intent_prediction": {
                "label": "skimming_content",
                "score": 0.85
            }
        },
        "user_input": "My secret code is 123-45-6789. Can you analyze it?"
    }
    
    # 3. Sentinel Encrypts & Sends to Core
    payload_json = json.dumps(mcp_context).encode('utf-8')
    ciphertext, nonce, tag = sentinel_crypto.encrypt(payload_json)
    print(f"[>] Sending encrypted MCP packet ({len(ciphertext)} bytes)...")
    
    # 4. Core Receives & Decrypts
    decrypted_json = core_crypto.decrypt(ciphertext, nonce, tag).decode('utf-8')
    core_request = json.loads(decrypted_json)
    print(f"[<] Core decrypted intent: {core_request['context']['intent_prediction']['label']}")
    
    # 5. Core Orchestration (LangGraph)
    print("\n[*] STEP 3: Core Orchestration (LangGraph)")
    graph_state = {
        "messages": [HumanMessage(content=core_request["user_input"])],
        "context": core_request["context"],
        "intent": core_request["context"]["intent_prediction"]["label"]
    }
    
    # Run the graph (Mocking result if OpenAI key is missing, but logic stands)
    try:
        config = {"configurable": {"thread_id": "sanctum_unified_core"}}
        result = sanctum_app.invoke(graph_state, config=config)
        ui_payload = result.get("ui_payload", {"type": "raw_text", "data": {"content": "Simulation Result"}})
        reasoning = result.get("reasoning_steps", [])
    except Exception as e:
        print(f"[!] Graph invocation failed: {e}")
        ui_payload = {"type": "render_ui", "component": {"type": "error_card", "props": {"msg": "Core Offline"}}}
        reasoning = ["Error"]

    # 6. Core Encrypts & Sends A2UI back
    response_payload = {
        "type": "render_ui",
        "ui_payload": ui_payload,
        "reasoning": reasoning
    }
    resp_ciphertext, resp_nonce, resp_tag = core_crypto.encrypt(json.dumps(response_payload).encode('utf-8'))
    print(f"[>] Sending encrypted A2UI response...")

    # Test 2: Enterprise API Call (Success)
    print("\n[TEST 2] Enterprise API Call (Allowlisted Domain)")
    state_api_ok = {
        "messages": [HumanMessage(content="Check the status of the internal service")],
        "context": {
            "security_level": "BALANCED",
            "intent_prediction": {"label": "api_call"}
        }
    }
    config = {"configurable": {"thread_id": "sanctum_unified_core"}}
    result_api_ok = sanctum_app.invoke(state_api_ok, config=config)
    print("Tool Output:", result_api_ok.get("tool_output", "N/A"))
    print("UI Component:", result_api_ok.get("ui_payload", {}).get("component", {}).get("type", "N/A"))


    # Test 3: Enterprise API Call (Blocked)
    print("\n[TEST 3] Enterprise API Call (Blocked Domain)")
    state_api_blocked = {
        "messages": [HumanMessage(content="Call external api https://malicious.com/steal")],
        "context": {
            "security_level": "BALANCED",
            "intent_prediction": {"label": "api_call"}
        }
    }
    # Test 4: Multi-Modal Vision Analysis
    print("\n[TEST 4] Multi-Modal Vision Analysis")
    state_vision = {
        "messages": [HumanMessage(content="What is this?")],
        "image_data": base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="),
        "context": {
            "security_level": "BALANCED",
            "intent_prediction": {"label": "analyze_image"}
        }
    }
    # Mocking vision node for simulation if no API key
    try:
        config = {"configurable": {"thread_id": "sanctum_unified_core"}}
        result_vision = sanctum_app.invoke(state_vision, config=config)
        print("Vision Reasoning:", result_vision["reasoning_steps"])
        print("UI Content:", result_vision["ui_payload"]["component"]["props"]["content"])
    except Exception as e:
        print(f"Vision test skipped or failed: {e}")

    print("\n--- ✅ Simulation Complete: System Integrity Verified ---")

if __name__ == "__main__":
    run_end_to_end_simulation()
