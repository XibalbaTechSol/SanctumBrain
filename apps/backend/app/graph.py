import json
import os
import asyncio
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

try:
    from app.state import AgentState
    from app.nodes import aura_orchestrator, agui_client_node
    from app.security import (
        security_ingress_node,
        security_egress_node
    )
    from app.utils import log_event
except ImportError:
    try:
        from .state import AgentState
        from .nodes import aura_orchestrator, agui_client_node
        from .security import (
            security_ingress_node,
            security_egress_node
        )
        from .utils import log_event
    except ImportError:
        from state import AgentState
        from nodes import aura_orchestrator, agui_client_node
        from security import (
            security_ingress_node,
            security_egress_node
        )
        from utils import log_event

# Mapping of node IDs in config to actual Python functions
NODE_FUNCTIONS = {
    "security_ingress": security_ingress_node,
    "aura_orchestrator": aura_orchestrator,
    "security_egress": security_egress_node,
    "agui_client": agui_client_node
}

def create_sanctum_graph(checkpointer):
    workflow = StateGraph(AgentState)
    
    # 1. Add Core Nodes
    workflow.add_node("security_ingress", security_ingress_node)
    workflow.add_node("aura_orchestrator", aura_orchestrator)
    workflow.add_node("security_egress", security_egress_node)
    workflow.add_node("agui_client", agui_client_node)
    
    # 2. Define Static Sovereign Flow
    workflow.set_entry_point("security_ingress")
    
    # Ingress logic: passed -> Aura, violation -> Egress
    workflow.add_conditional_edges(
        "security_ingress",
        lambda state: "security_egress" if state.get("intent") == "security_violation" else "aura_orchestrator",
        {
            "aura_orchestrator": "aura_orchestrator",
            "security_egress": "security_egress"
        }
    )
    
    # Aura always flows to Egress for final audit
    workflow.add_edge("aura_orchestrator", "security_egress")
    
    # Egress leads to AGUI Client dispatch
    workflow.add_edge("security_egress", "agui_client")
    
    # Client dispatch leads to termination
    workflow.add_edge("agui_client", END)
    
    return workflow.compile(checkpointer=checkpointer)

# --- Checkpointer Management ---
def get_checkpointer():
    return MemorySaver()

# Initialize the Sovereign Graph
_checkpointer = get_checkpointer()
sanctum_app = create_sanctum_graph(_checkpointer)
