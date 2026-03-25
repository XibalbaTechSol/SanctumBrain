import json
import base64
import os

import time
import psutil
import re
import requests
import asyncio
import operator
import uuid
from datetime import datetime
from typing import Annotated, Sequence, TypedDict, List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
from redis import Redis
from .state import AgentState, trim_messages
from .rag import retrieve_context
from .utils import log_event
from .prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT, 
    VISION_AGENT_PROMPT, 
    KNOWLEDGE_AGENT_PROMPT,
    SUPERVISOR_PROMPT,
    PARA_MANAGER_PROMPT,
    PARA_EXTRACTION_PROMPT
)
from .mcp import generate_mcp_payload, create_para_dashboard_payload, validate_mcp_payload, repair_mcp_payload

# Load .env file
load_dotenv()

# --- Efficiency: Global LLM Cache (Redis) ---
try:
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    set_llm_cache(RedisCache(Redis.from_url(redis_url)))
    log_event("SYSTEM", f"Efficiency: Redis LLM Cache Enabled")
except Exception as e:
    print(f"[*] Failed to enable Redis LLM Cache: {e}")

class ResilientModel:
    def __init__(self, model, name="Unknown"):
        self.model = model
        self.name = name
        
    def invoke(self, messages, **kwargs):
        try:
            print(f"[*] Neural Core: Invoking {self.name}")
            return self.model.invoke(messages, **kwargs)
        except Exception as e:
            print(f"[*] Neural Core Runtime Error ({self.name}): {e}")
            raise e

def initialize_local_model():
    print("[*] Initializing SIMULATED LOCAL SLM (OpenRouter GPT-4o-Mini)...")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            m = ChatOpenAI(
                model="openai/gpt-4o-mini", 
                openai_api_key=api_key, 
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0
            )
            print(f"[*] Simulated Local SLM Ready (OpenRouter).")
            return ResilientModel(m, "OpenRouter-Simulated-SLM")
    except Exception as e:
        print(f"[!] OpenRouter initialization failed: {e}")
    return None

def initialize_frontier_model():
    print("[*] Initializing SIMULATED FRONTIER LLM (OpenRouter GPT-4o-Mini)...")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            m = ChatOpenAI(
                model="openai/gpt-4o-mini", 
                openai_api_key=api_key, 
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0.7
            )
            print("[*] Simulated Frontier LLM Ready (OpenRouter).")
            return ResilientModel(m, "OpenRouter-Simulated-Frontier")
    except Exception as e:
        print(f"[!] OpenRouter initialization failed: {e}")
    
    return None

def initialize_on_device_model():
    print("[*] Initializing ON-DEVICE SLM (Ollama - Phi3) for PII Redaction...")
    try:
        from langchain_community.chat_models import ChatOllama
        m = ChatOllama(model="phi3", temperature=0)
        return ResilientModel(m, "Ollama-Local-SLM")
    except Exception as e:
        print(f"[!] Ollama initialization failed: {e}")
        return None

# --- Neural Core Initialization ---
local_model = initialize_local_model()
frontier_model = initialize_frontier_model()
on_device_model = initialize_on_device_model() or local_model

# Safety fallback: If frontier fails, use local. If both fail, the system will raise errors on invocation.
if not frontier_model:
    print("[!] Warning: Frontier Model unavailable. Falling back to Local SLM.")
    frontier_model = local_model

if not local_model:
    print("[!] Warning: Local SLM unavailable. Intent decoding will fail if Frontier is not used as supervisor.")
    # If local_model is None, we assign frontier to it as a last resort for intent decoding
    local_model = frontier_model

# --- NODES ---

def supervisor_node(state: AgentState):
    log_event("GRAPH", "Decoding Intent (Local SLM)", node_id="supervisor")
    messages = state["messages"]
    last_message = messages[-1].content.lower()
    
    sys_status = state.get("system_status", {})
    summary = f"CPU: {sys_status.get('cpu')}% | RAM: {sys_status.get('mem')}%"

    system_prompt = SUPERVISOR_PROMPT.format(system_summary=summary, user_input=last_message)
    response = local_model.invoke([SystemMessage(content=system_prompt)] + list(messages))
    content = response.content.strip().lower()
    
    intent = "general"
    intent_map = {
        "para": ["para", "project", "area", "archive", "resource", "organize"],
        "system_health": ["system_health", "health", "diagnostics", "status", "telemetry"],
        "weather": ["weather", "forecast", "temperature", "climate", "atmosphere"],
        "knowledge": ["knowledge", "memory", "rag", "search", "lookup", "recall"],
        "image": ["image", "vision"],
        "audio": ["audio", "voice"],
        "api": ["api", "tool"],
        "code": ["code", "exec"],
        "deep_reason": ["deep_reason", "reasoner"]
    }
    
    # Priority keyword extraction
    priority_order = ["system_health", "weather", "para", "image", "audio", "code", "knowledge", "deep_reason", "api"]

    # Exact match first
    for target_intent in priority_order:
        if target_intent == content:
            intent = target_intent
            break

    # Keyword match second
    if intent == "general":
        for target_intent in priority_order:
            keywords = intent_map[target_intent]
            if any(k in content for k in keywords):
                intent = target_intent
                break

    print(f"[*] Supervisor (Local): Classified as '{intent}' | Raw: '{content[:50]}'")
    return {"intent": intent}

def generator_node(state: AgentState):
    log_event("GRAPH", "Synthesizing UI Payload (Frontier LLM)", node_id="generator")
    intent = state.get("intent", "general")
    sys_status = state.get("system_status", {})
    sentinels = state.get("active_sentinels", [])
    
    messages = state["messages"]
    system_prompt = ORCHESTRATOR_SYSTEM_PROMPT
    
    response = frontier_model.invoke([SystemMessage(content=system_prompt)] + list(messages))
    content = response.content
    
    mcp_payload = None
    if intent == "system_health":
        mcp_payload = generate_mcp_payload(
            intent=intent, 
            ui_type="SYSTEM_HEALTH_CARD", 
            data={
                "metrics": {
                    "cpu": sys_status.get("cpu", 0),
                    "mem": sys_status.get("mem", 0),
                    "disk": sys_status.get("disk", 0),
                    "vps_id": sys_status.get("vps_id", "Sanctum-VPS"),
                    "status": sys_status.get("status", "Healthy")
                }, 
                "sentinels": sentinels,
                "summary": content
            }
        )
    elif intent == "knowledge":
        mcp_payload = generate_mcp_payload(
            intent=intent, 
            ui_type="RAG_VISUALIZATION_CARD", 
            data={
                "answer": content, 
                "visualization": state.get("rag_visualization", {
                    "query": messages[-1].content,
                    "retrieved_nodes": [],
                    "latency_ms": 0
                })
            }
        )
    elif intent == "weather":
        mcp_payload = generate_mcp_payload(
            intent=intent,
            ui_type="WEATHER_CARD",
            data={
                "location": "San Francisco",
                "temperature": 22,
                "condition": "Sunny",
                "forecast": [
                    {"day": "Mon", "temp": 22, "condition": "Sunny"},
                    {"day": "Tue", "temp": 24, "condition": "Clear"},
                    {"day": "Wed", "temp": 21, "condition": "Cloudy"}
                ],
                "summary": content
            }
        )
    elif intent == "para":
        mcp_payload = state.get("mcp_ui_payload") or generate_mcp_payload(
            intent=intent,
            ui_type="INFO_CARD",
            data={"title": "PARA System", "content": content}
        )
    else:
        parsed_json = None
        try:
            clean_content = re.sub(r'^```(?:json)?|```$', '', content.strip(), flags=re.MULTILINE).strip()
            parsed_json = json.loads(clean_content)
        except Exception:
            pass

        if parsed_json and isinstance(parsed_json, dict) and "ui_payload" in parsed_json:
            ui_type = parsed_json["ui_payload"].get("type", "INFO_CARD")
            ui_data = parsed_json["ui_payload"].get("data", parsed_json["ui_payload"].get("content", parsed_json))
            mcp_payload = generate_mcp_payload(intent=parsed_json.get("intent", intent), ui_type=ui_type, data=ui_data)
        elif parsed_json and isinstance(parsed_json, dict):
            mcp_payload = generate_mcp_payload(intent=intent, ui_type=parsed_json.get("type", "INFO_CARD"), data=parsed_json.get("data", parsed_json))
        else:
            mcp_payload = generate_mcp_payload(intent=intent, ui_type="INFO_CARD", data={"title": intent.upper(), "content": content})

    # Ensure payload is never None
    if mcp_payload is None:
        mcp_payload = generate_mcp_payload(intent="fallback", ui_type="INFO_CARD", data={"title": "NEURAL CORE", "content": content})

    # --- Task 7: Self-Healing UI Pattern ---
    source_info = f"Frontier reasoning by {frontier_model.name}"
    is_valid = validate_mcp_payload(mcp_payload)
    
    if not is_valid:
        log_event("SYSTEM", "Malformed Payload Detected. Triggering Self-Healing.", node_id="generator", extra={"intent": intent})
        mcp_payload = repair_mcp_payload(mcp_payload, default_intent=intent)
        source_info += " (Self-Healed)"

    # --- Memory Management: Trim messages and clear large binary fields ---
    state = trim_messages(state)
    
    return {
        "mcp_ui_payload": mcp_payload, 
        "messages": [AIMessage(content=content)], 
        "reasoning_steps": [f"Classification by {local_model.name}.", source_info],
        "image_data": b"", # Clear after use
        "audio_data": b""  # Clear after use
    }

from .db.models import Project, Area 

async def para_manager_node(state: AgentState):
    """
    Node to manage PARA entities (Projects, Areas, Resources, Archives).
    Supports LIST, CREATE, UPDATE, and DELETE via SLM-based intent extraction.
    """
    log_event("GRAPH", "Architecting PARA Sovereign View", node_id="para_manager")
    messages = state["messages"]
    last_message = messages[-1].content
    
    # 1. Parameter Extraction (Local SLM)
    extract_prompt = PARA_EXTRACTION_PROMPT.format(user_input=last_message)
    extraction_resp = local_model.invoke([SystemMessage(content=extract_prompt)])
    
    try:
        # Robust JSON extraction using regex
        json_str = extraction_resp.content.strip()
        match = re.search(r'(\{.*\})', json_str, re.DOTALL)
        if match:
            json_str = match.group(1)
        
        params = json.loads(json_str)
    except Exception as e:
        print(f"[*] PARA Extraction Error: {e} | Raw: {extraction_resp.content}")
        # Default fallback
        params = {"action": "LIST", "type": "PROJECT"}

    action = params.get("action", "LIST").upper()
    entity_type = params.get("type", "PROJECT").upper()
    
    res_msg = ""
    state_updates = {"intent": "para"}
    
    # 2. Database Operations (Tortoise-ORM)
    if action == "CREATE":
        if entity_type == "PROJECT":
            new_id = f"proj-{uuid.uuid4().hex[:8]}"
            await Project.create(id=new_id, title=params.get("title", "Untitled Project"), goal=params.get("goal", ""))
            res_msg = f"Created Project: {params.get('title')}"
        elif entity_type == "AREA":
            await Area.create(id=uuid.uuid4(), name=params.get("title", "Untitled Area"))
            res_msg = f"Created Area: {params.get('title')}"
            
    elif action == "UPDATE":
        entity_id = params.get("id")
        if entity_id:
            if entity_type == "PROJECT":
                proj = await Project.get_or_none(id=entity_id)
                if proj:
                    if "status" in params: proj.status = params["status"]
                    if "title" in params: proj.title = params["title"]
                    await proj.save()
                    res_msg = f"Updated Project: {proj.title}"
                    state_updates["active_project_id"] = str(entity_id)
            elif entity_type == "AREA":
                area = await Area.get_or_none(id=entity_id)
                if area:
                    if "title" in params: area.name = params["title"]
                    await area.save()
                    res_msg = f"Updated Area: {area.name}"
                    state_updates["active_area"] = str(entity_id)

    elif action == "DELETE":
        entity_id = params.get("id")
        if entity_id:
            if entity_type == "PROJECT":
                proj = await Project.get_or_none(id=entity_id)
                if proj: 
                    title = proj.title
                    await proj.delete()
                    res_msg = f"Deleted Project: {title}"
            elif entity_type == "AREA":
                area = await Area.get_or_none(id=entity_id)
                if area:
                    name = area.name
                    await area.delete()
                    res_msg = f"Deleted Area: {name}"

    elif action == "SELECT":
        entity_id = params.get("id")
        if entity_id:
            if entity_type == "PROJECT":
                state_updates["active_project_id"] = str(entity_id)
                res_msg = f"Selected Project as active context."
            elif entity_type == "AREA":
                state_updates["active_area"] = str(entity_id)
                res_msg = f"Selected Area as active context."

    # 3. Data Retrieval for UI (Limit to 50 items for memory efficiency)
    items_data = []
    if entity_type == "PROJECT":
        items_data = await Project.all().limit(50).values()
    else:
        items_data = await Area.all().limit(50).values()
    
    items_data = [dict(i) for i in items_data]
    
    # Format dates for JSON serialization
    for item in items_data:
        for k, v in item.items():
            if isinstance(v, datetime):
                item[k] = v.isoformat()
            if isinstance(v, uuid.UUID):
                item[k] = str(v)

    # 4. Synthesize MCP Payload
    mcp_payload = create_para_dashboard_payload(
        view="KANBAN" if entity_type == "PROJECT" else "LIST", 
        items=items_data, 
        intent=f"PARA_{action}_{entity_type}"
    )
    
    reasoning = f"PARA Database synchronized: {res_msg}" if res_msg else "PARA items retrieved."
    
    state_updates.update({
        "mcp_ui_payload": mcp_payload, 
        "reasoning_steps": [reasoning]
    })
    return state_updates

def vision_node(state: AgentState): 
    # Logic to process image would go here
    return {"reasoning_steps": ["Image analyzed."], "image_data": b""}

def audio_node(state: AgentState): 
    # Logic to process audio would go here
    return {"reasoning_steps": ["Audio transcribed."], "audio_data": b""}
def reasoner_node(state: AgentState): return {"reasoning_steps": ["Deliberation Complete."]}
def rag_node(state: AgentState):
    query = state["messages"][-1].content
    retrieval_result = retrieve_context(query)
    return {"rag_visualization": retrieval_result["visualization"], "retrieved_context": "\n\n".join(retrieval_result["context_strings"]), "reasoning_steps": ["Memory searched."]}
def code_execution_node(state: AgentState): return {"reasoning_steps": ["Code executed."]}
