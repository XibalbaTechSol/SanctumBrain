import sys
import os
from dotenv import load_dotenv
import asyncio # Import asyncio
from tortoise import Tortoise, run_async # Import Tortoise and run_async

# Load .env file at the earliest possible moment
load_dotenv()

from app.server import serve as start_grpc_server
from app.graph import sanctum_app
from langchain_core.messages import HumanMessage
import json

# Tortoise ORM Configuration
TORTOISE_CONFIG = {
    "connections": {"default": os.getenv("DATABASE_URL", "postgres://user:password@localhost:5432/sanctum_brain").replace("postgresql://", "postgres://")},
    "apps": {
        "models": {
            "models": ["app.db.models"], # Register app models
            "default_connection": "default",
        },
    },
}

async def init_db():
    await Tortoise.init(config=TORTOISE_CONFIG)
    # Generate the schema (creates tables if they don't exist)
    await Tortoise.generate_schemas()
    print("Database initialized and schema generated.")

def test_graph():
    print("--- 🛡️ Starting Project Sanctum Security Test ---")
    
    # Test 1: PII Scrubbing
    print("\n[TEST 1] PII Scrubbing (Privacy-First Policy)")
    state_pii = {
        "messages": [HumanMessage(content="My email is john.doe@example.com and phone is 555-0199.")],
        "context": {
            "security_level": "PRIVACY_FIRST",
            "intent_prediction": {"label": "general_navigation"}
        }
    }
    config = {"configurable": {"thread_id": "test_thread"}}
    result_pii = sanctum_app.invoke(state_pii, config=config)
    print("Reasoning:", result_pii.get("reasoning_steps", []))
    
    # Check for the new standardized payload key
    mcp_payload = result_pii.get("mcp_ui_payload", {})
    ui_data = mcp_payload.get("ui", {}).get("data", {})
    print("Scrubbed UI Content:", ui_data.get("content", "N/A"))

    # Test 2: Policy Violation (Lockdown mode prohibits tools)
    print("\n[TEST 2] Policy Violation (LOCKDOWN prohibits code exec)")
    state_violation = {
        "messages": [HumanMessage(content="Run this python code: print('hello')")],
        "context": {
            "security_level": "LOCKDOWN",
            "intent_prediction": {"label": "execute_code"}
        },
        "intent": "code" # Force intent for test
    }
    result_violation = sanctum_app.invoke(state_violation, config=config)
    
    mcp_violation = result_violation.get("mcp_ui_payload", {})
    ui_type = mcp_violation.get("ui", {}).get("type", "UNKNOWN")
    print("UI Type:", ui_type)
    print("Alert Message:", result_violation.get("tool_output", "Security Violation: Access Denied"))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # run_async(init_db()) # Initialize DB asynchronously
        start_grpc_server()
    else:
        test_graph()
        print("\n[TIP] Run 'python main.py serve' to start the gRPC A2A server.")
