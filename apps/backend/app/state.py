import operator
from typing import Annotated, Sequence, TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # --- CORE CONVERSATION ---
    messages: Annotated[Sequence[BaseMessage], add_messages]
    intent: str
    reasoning_steps: Annotated[List[str], operator.add]
    
    # --- PARA: ACTIVE MEMORY POINTERS ---
    active_project_id: str
    active_area: str
    context_resources: List[str] # List of UUIDs to PARA Resources
    
    # --- MULTI-MODAL DATA ---
    image_data: bytes # Base64 or raw bytes of a screenshot/photo
    audio_data: bytes # Base64 or raw bytes of a voice command
    
    # --- SYSTEM TRUTH (Source of Truth) ---
    system_status: Dict[str, Any] # cpu, mem, uptime, vps_id
    active_sentinels: List[Dict[str, Any]]
    memory_stats: Dict[str, Any] # total_chunks, last_ingest
    user_context: Dict[str, Any] # habits, preferences, active_projects
    event_timeline: List[Dict[str, Any]]
    
    # --- OUTPUT PAYLOADS ---
    # The generated UI payload to be sent to the client (A2UI/MCP)
    ui_payload: Dict[str, Any]
    mcp_ui_payload: Dict[str, Any] # Standardized MCP schema for cross-platform UI
    tool_output: str
    
    # --- PRIVACY & SECURITY ---
    pii_redacted: bool
    
    # --- INTERMEDIATE DATA ---
    rag_visualization: Dict[str, Any]
    retrieved_context: str
    context: Dict[str, Any] # Raw context from incoming request

def trim_messages(state: AgentState, max_messages: int = 15) -> AgentState:
    """
    Trims the message history to prevent memory bloat while keeping the SystemMessage.
    """
    messages = state.get("messages", [])
    if not isinstance(messages, list) or len(messages) <= max_messages:
        return state
    
    # Keep the first message if it's a SystemMessage, otherwise just take the last N
    system_messages = [m for m in messages if hasattr(m, "type") and m.type == "system"]
    other_messages = [m for m in messages if not hasattr(m, "type") or m.type != "system"]
    
    # Keep last N - (number of system messages)
    trimmed_others = other_messages[-(max_messages - len(system_messages)):]
    
    state["messages"] = system_messages + trimmed_others
    return state
