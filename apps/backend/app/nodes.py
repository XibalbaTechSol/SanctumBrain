import json
import base64
import os
import time
import psutil
import re
import subprocess
import sys
import io
from datetime import datetime
from typing import Annotated, Sequence, TypedDict, List, Dict, Any
from dotenv import load_dotenv

# --- Hermes (Aura) Integration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HERMES_PATH = os.path.join(PROJECT_ROOT, "hermes")
if HERMES_PATH not in sys.path:
    sys.path.append(HERMES_PATH)

# Isolate Aura's configuration within the project
AURA_HOME = os.path.join(PROJECT_ROOT, "apps", "backend", ".sanctum_hermes")
os.environ["HERMES_HOME"] = AURA_HOME

try:
    from run_agent import AIAgent
    HERMES_AVAILABLE = True
except ImportError:
    print("[!] Warning: Hermes Agent framework not found at", HERMES_PATH)
    HERMES_AVAILABLE = False

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
from redis import Redis

try:
    from app.state import AgentState
    from app.utils import log_event
    from app.prompts import AURA_SYSTEM_PROMPT, SECURITY_AGENT_PROMPT
    from app.mcp import generate_mcp_payload
    from app.tools.sanctum_tools import register_sanctum_tools
except ImportError:
    # Local fallback
    try:
        from .state import AgentState
        from .utils import log_event
        from .prompts import AURA_SYSTEM_PROMPT, SECURITY_AGENT_PROMPT
        from .mcp import generate_mcp_payload
        from .tools.sanctum_tools import register_sanctum_tools
    except ImportError:
        from state import AgentState
        from utils import log_event
        from prompts import AURA_SYSTEM_PROMPT, SECURITY_AGENT_PROMPT
        from mcp import generate_mcp_payload
        from tools.sanctum_tools import register_sanctum_tools

# Load .env file
load_dotenv()

# --- Model Initialization ---

class ResilientModel:
    def __init__(self, model, name):
        self.model = model
        self.name = name
    def invoke(self, messages):
        return self.model.invoke(messages)

def initialize_google_model():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            m = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key, temperature=0)
            print("[*] Frontier LLM Ready (Google Gemini).")
            return ResilientModel(m, "Google-Gemini-Pro")
    except Exception as e:
        print(f"[!] Gemini initialization failed: {e}")
    return None

def initialize_local_model():
    print("[*] Initializing LOCAL SLM...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        m = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0)
        print("[*] Local SLM Ready (Gemini Flash).")
        return ResilientModel(m, "Gemini-Flash-Local")
    return None

def initialize_frontier_model():
    m = initialize_google_model()
    if m: return m
    return initialize_local_model()

def initialize_on_device_model():
    print("[*] Initializing ON-DEVICE SLM (Ollama - Phi3) for PII Redaction...")
    try:
        from langchain_community.chat_models import ChatOllama
        m = ChatOllama(model="phi3", temperature=0)
        return ResilientModel(m, "Ollama-Local-SLM")
    except Exception as e:
        print(f"[!] Ollama initialization failed: {e}")
        return None

# Static model instances for security nodes
local_model = initialize_local_model()
frontier_model = initialize_frontier_model()
on_device_model = initialize_on_device_model()

def initialize_gemma4_model():
    print("[*] Initializing GEMMA 4 (Edge Inference Simulator)...")
    # Using Flash as a proxy for speed in edge synthesis simulation
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        m = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.2)
        return ResilientModel(m, "Gemma-4-Edge")
    return None

gemma4_model = initialize_gemma4_model()

# --- Prompts ---
AGUI_CLIENT_PROMPT = """
You are Gemma 4, the Edge Inference layer of SanctumBrain.
Your task is to "PAINT" the Generative UI based on the Orchestrator's intent and data.
- INPUT: A base UI intent and raw data.
- TASK: Refine the AGUI/A2UI manifest. Add adaptive styling, optimize for the edge device, and ensure high-fidelity presentation.
- OUTPUT: Valid AGUI JSON only.
If the intent matches a known high-fidelity pattern (BANKING, WEATHER, CALENDAR), ensure the components are rich and interactive.
"""

# --- Aura Orchestrator Implementation ---

def aura_orchestrator(state: AgentState):
    """
    Aura Orchestrator: The primary agent harness for SanctumBrain.
    Uses Hermes under the hood, rebranded as Aura.
    """
    if not HERMES_AVAILABLE:
        return {"reasoning_steps": ["Aura harness not initialized. Check hermes/ submodule."], "intent": "general"}

    log_event("AURA", "Synchronizing neural state...", node_id="aura_orchestrator")
    
    last_message = state["messages"][-1].content
    system_status = state.get("system_status", {})
    active_sentinels = state.get("active_sentinels", [])
    
    # Enrich system prompt with real-time "System Truth"
    dynamic_system_prompt = AURA_SYSTEM_PROMPT + f"\n\nCURRENT SYSTEM TRUTH:\n"
    dynamic_system_prompt += f"- VPS Status: {system_status.get('status', 'Unknown')}\n"
    dynamic_system_prompt += f"- CPU Load: {system_status.get('cpu', 0)}%\n"
    dynamic_system_prompt += f"- Memory: {system_status.get('mem', 0)}%\n"
    dynamic_system_prompt += f"- Active Sentinels: {len(active_sentinels) if active_sentinels else 0}\n"
    
    # Initialize Aura (Hermes)
    aura_model = os.getenv("AURA_MODEL", "google/gemini-2.0-flash-001")
    aura_provider = os.getenv("AURA_PROVIDER", "auto")
    
    # Check for 'Free Mode' (Gemini CLI via MCP)
    if os.getenv("AURA_FREE_MODE", "false").lower() == "true":
        aura_model = "mcp-sampling://auto"
        aura_provider = "mcp-sampling"
        log_event("AURA", "Switching to Sovereign Free Mode (Gemini CLI MCP)", node_id="aura_orchestrator")

    agent = AIAgent(
        model=aura_model,
        provider=aura_provider,
        quiet_mode=True,
        platform="sanctum-brain",
        enabled_toolsets=["sanctum", "terminal", "file", "web", "agui"]
    )
    
    try:
        # Run conversation through Aura
        result = agent.run_conversation(
            user_message=last_message,
            system_message=dynamic_system_prompt,
            conversation_history=[{"role": m.__class__.__name__.replace("Message", "").lower(), "content": m.content} for m in state["messages"][:-1]]
        )
        
        final_response = result.get("final_response", "Aura has synthesized your request.")
        trajectory = result.get("agent_trajectory", ["Aura processed the request."])
        
        # Determine intent if not provided
        intent = state.get("intent", "general")
        
        # --- NEW: Extract AGUI Payload from Hermes Tool Trajectory ---
        mcp_payload = {}
        agui_requests = [step for step in result.get("steps", []) if step.get("tool_name") == "render_generative_ui"]
        
        if agui_requests:
            try:
                # Pluck the last UI synthesis request
                sr_json = agui_requests[-1].get("tool_output", "{}")
                sr = json.loads(sr_json)
                if sr.get("status") == "UI_SYNTHESIS_REQUESTED":
                    intent = sr.get("intent", intent)
                    mcp_payload = generate_mcp_payload(
                        intent=intent,
                        ui_type=sr.get("ui_type", "INFO_CARD"),
                        data=sr.get("payload", {})
                    )
                    log_event("AURA", f"Kinetic UI Synthesized: {sr.get('ui_type')}", node_id="aura_orchestrator")
            except:
                pass
        
        # Fallback if no tool was called but we still need UI
        if not mcp_payload:
            used_tools = [step.get("tool_name") for step in result.get("steps", []) if "tool_name" in step]
            if "query_para_database" in used_tools:
                intent = "PARA_MANAGEMENT"
            elif "manage_calendar_events" in used_tools:
                intent = "CALENDAR"
            
            mcp_payload = generate_mcp_payload(
                intent=intent,
                ui_type="INFO_CARD",
                data={
                    "title": "Aura Response",
                    "content": final_response,
                    "reasoning": trajectory
                }
            )

        return {
            "messages": [AIMessage(content=final_response)],
            "reasoning_steps": [f"Aura: {step}" for step in trajectory],
            "intent": intent,
            "mcp_ui_payload": mcp_payload,
            "ui_payload": mcp_payload # For legacy compatibility
        }
    except Exception as e:
        log_event("ERROR", f"Aura Orchestrator Failed: {e}", node_id="aura_orchestrator")
        return {"reasoning_steps": [f"Aura error: {e}"], "intent": "general"}

async def agui_client_node(state: AgentState):
    """
    Gemma 4 Edge Inference Node:
    Takes the orchestrator's intention and "paints" the final A2UI/AGUI manifest.
    Dynamically creates/refines UI elements using edge-optimized reasoning.
    """
    log_event("SYSTEM", "Gemma 4: Starting Kinetic UI Synthesis (Painting Phase)", node_id="agui_client_node")
    
    intent = state.get("intent", "general")
    mcp_payload = state.get("mcp_ui_payload", {})
    
    # Simulate Edge Inference (Gemma 4)
    if gemma4_model and mcp_payload:
        try:
            # Check for reusable components in DB
            from app.db.models import AdaptiveUIComponent
            component = await AdaptiveUIComponent.get_or_none(id=f"{intent.upper()}_UI")
            
            base_manifest = component.manifest if component else json.dumps(mcp_payload)
            
            # Construct Synthesis Message
            synthesis_msg = f"PAINT THE UI.\nINTENT: {intent}\nBASE MANIFEST: {base_manifest}\nUSER_CONTEXT: {state.get('user_context', {})}"
            
            response = gemma4_model.invoke([
                SystemMessage(content=AGUI_CLIENT_PROMPT),
                HumanMessage(content=synthesis_msg)
            ])
            
            # Extract the "painted" JOSN
            try:
                painted_json = re.search(r'\{.*\}', response.content, re.DOTALL).group()
                final_payload = json.loads(painted_json)
                
                # If this was a successful adaptive synthesis, we could save/update it here
                # (Optional: Logic to save refined components back to AdaptiveUIComponent)
                
                log_event("SYSTEM", f"Gemma 4: UI Painting Complete ({intent})", node_id="agui_client_node")
                return {
                    "mcp_ui_payload": final_payload,
                    "status": "DISPATCHED"
                }
            except:
                log_event("WARNING", "Gemma 4 synthesis failed to return valid JSON. Using original payload.", node_id="agui_client_node")
        except Exception as e:
            log_event("ERROR", f"Gemma 4 Stage Failed: {e}", node_id="agui_client_node")

    return {
        "mcp_ui_payload": mcp_payload,
        "status": "DISPATCHED"
    }

# Note: Legacy specialist nodes (vision, audio, etc.) have been removed.
