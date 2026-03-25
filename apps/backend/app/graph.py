import json
import os
import asyncio
import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver
from psycopg_pool import ConnectionPool

from .state import AgentState
from .nodes import (
    supervisor_node, 
    generator_node, 
    rag_node, 
    code_execution_node, 
    vision_node, 
    audio_node, 
    reasoner_node,
    para_manager_node
)
from .security import (
    security_ingress_node,
    security_egress_node
)
from .tools import tool_node
from .utils import log_event

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "graph_config.json")

# Mapping of node IDs in config to actual Python functions
NODE_FUNCTIONS = {
    "security_ingress": security_ingress_node,
    "supervisor": supervisor_node,
    "vision": vision_node,
    "audio": audio_node,
    "tools": tool_node,
    "rag": rag_node,
    "reasoner": reasoner_node,
    "generator": generator_node,
    "code_exec": code_execution_node,
    "security_egress": security_egress_node,
    "para_manager": para_manager_node,
}

# --- Task 7: Routing Optimization ---
ROUTING_MAP = {} # Global cache for intent-to-node transitions

def dynamic_router(state: AgentState, source_node: str, edges: list):
    """
    Optimized router using pre-filtered edges for O(1) local lookup latency.
    Reduces compute cycles by eliminating O(E) list comprehensions per step.
    """
    intent = state.get("intent")
    steps = state.get("reasoning_steps", [])
    last_step = steps[-1] if steps else ""
    
    # Check cache first for high-velocity O(1) lookup
    cache_key = f"{source_node}:{intent}"
    if cache_key in ROUTING_MAP:
        return ROUTING_MAP[cache_key]
    
    # Intent-based routing (priority)
    for edge in edges:
        condition = edge.get("condition")
        if condition and condition.startswith("intent="):
            target_intent = condition.split("=")[1]
            if intent == target_intent:
                target = edge["target"]
                res = END if target == "__end__" else target
                ROUTING_MAP[cache_key] = res # Cache successful hit
                return res

    # Logic-based routing
    for edge in edges:
        condition = edge.get("condition")
        if not condition: continue
        if condition == "passed" and intent != "security_violation":
            return edge["target"]
        if condition == "violation" and intent == "security_violation":
            return edge["target"]
        if condition == "REFINE" and "REFINE" in last_step:
            return edge["target"]
        if condition == "COMPLETE" and ("COMPLETE" in last_step or "REFINE" in last_step):
            return edge["target"]

    # Fallback to default edge (unconditional)
    for edge in edges:
        if not edge.get("condition"):
            target = edge["target"]
            return END if target == "__end__" else target

    log_event("ERROR", f"No valid path found from {source_node}. Routing to generator.")
    return "generator"

def create_sanctum_graph(checkpointer):
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"[!] Error loading graph config: {e}")
    workflow = StateGraph(AgentState)
    added_nodes = set()
    for node_cfg in config.get("nodes", []):
        node_id = node_cfg["id"]
        if node_id in NODE_FUNCTIONS:
            workflow.add_node(node_id, NODE_FUNCTIONS[node_id])
            added_nodes.add(node_id)
    edges_by_source = {}
    for edge in config.get("edges", []):
        source = edge["source"]
        if source not in edges_by_source:
            edges_by_source[source] = []
        edges_by_source[source].append(edge)
    for source, edges in edges_by_source.items():
        if source == "__start__":
            workflow.set_entry_point(edges[0]["target"])
            continue
        if source not in added_nodes: continue
        has_conditions = any(e.get("condition") for e in edges)
        if has_conditions:
            targets = {e["target"]: (END if e["target"] == "__end__" else e["target"]) for e in edges}
            workflow.add_conditional_edges(source, lambda state, s=source, ed=edges: dynamic_router(state, s, ed), targets)
        else:
            target = edges[0]["target"]
            workflow.add_edge(source, END if target == "__end__" else target)
    return workflow.compile(checkpointer=checkpointer)

# --- Checkpointer Management ---
def get_checkpointer():
    print("[*] Using MemorySaver for Graph Checkpointing (Stability Mode).")
    return MemorySaver()

# Initialize with stability mode
_checkpointer = get_checkpointer()
sanctum_app = create_sanctum_graph(_checkpointer)
