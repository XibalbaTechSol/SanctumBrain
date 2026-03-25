import time
from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from .nodes import model
from .mcp import generate_mcp_payload
from .utils import log_event

class OpenClawState(TypedDict):
    sensor_data: Dict[str, Any]
    intent: str
    plan: List[str]
    ui_payload: Dict[str, Any]
    error_feedback: str
    messages: list

def observe_node(state: OpenClawState):
    """
    Ingest real-time sensor fusion (accelerometer, mouse, PARA context).
    Calculates Information Flux (dI/dt).
    """
    log_event("OPENCLAW", "Observe Phase: Ingesting sensor fusion data.")
    # Mocking sensor ingestion and flux calculation
    sensor_data = state.get("sensor_data", {"velocity": "high", "focus": "editor"})
    return {"messages": [HumanMessage(content=f"Sensors: {sensor_data}")], "intent": "unknown"}

def orient_node(state: OpenClawState):
    """
    Map sensor vectors to User Intent using the Local LLM (Edge SLM) or Frontier model.
    """
    log_event("OPENCLAW", "Orient Phase: Mapping sensor vectors to Intent.")
    # Here we would normally invoke the Edge SLM to determine intent
    return {"intent": "render_dashboard"}

def decide_node(state: OpenClawState):
    """
    Use the OpenClaw 'Plan-and-Execute' pattern to determine which UI atoms to paint.
    """
    log_event("OPENCLAW", "Decide Phase: Planning UI atom rendering.")
    plan = ["fetch_para_context", "generate_dashboard_schema"]
    return {"plan": plan}

def act_node(state: OpenClawState):
    """
    Deliver the AGUI/A2UI payload via MCP to the Canvas.
    """
    log_event("OPENCLAW", "Act Phase: Delivering payload to Canvas.")
    # Simulated validation of generated payload
    payload = generate_mcp_payload(intent=state["intent"], ui_type="PARA_DASHBOARD", data={})
    return {"ui_payload": payload, "error_feedback": ""}

def validate_node(state: OpenClawState):
    """
    Self-Correction logic: If the 'Act' phase fails (UI validation error), OpenClaw must immediately 'Re-Orient'.
    """
    log_event("OPENCLAW", "Validate Phase: Checking execution integrity.")
    if not state.get("ui_payload") or state.get("intent") == "unknown":
        return {"error_feedback": "Invalid payload or intent. Re-orienting."}
    return {"error_feedback": "valid"}

def route_correction(state: OpenClawState):
    if state.get("error_feedback") != "valid" and state.get("error_feedback"):
        log_event("OPENCLAW", "Self-Correction Triggered: Routing back to Orient.")
        return "Orient"
    return END

def create_openclaw_graph():
    """Builds the Unified OpenClaw Loop."""
    workflow = StateGraph(OpenClawState)
    
    workflow.add_node("Observe", observe_node)
    workflow.add_node("Orient", orient_node)
    workflow.add_node("Decide", decide_node)
    workflow.add_node("Act", act_node)
    workflow.add_node("Validate", validate_node)
    
    # Define the information flux pathways
    workflow.set_entry_point("Observe")
    workflow.add_edge("Observe", "Orient")
    workflow.add_edge("Orient", "Decide")
    workflow.add_edge("Decide", "Act")
    workflow.add_edge("Act", "Validate")
    
    # Self-healing loop
    workflow.add_conditional_edges("Validate", route_correction, {"Orient": "Orient", END: END})
    
    return workflow.compile()

openclaw_app = create_openclaw_graph()
