from typing import Dict, Any, List

def generate_mcp_payload(intent: str, ui_type: str, data: Dict[str, Any], tools: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Generates a standardized MCP UI payload for cross-platform delivery (Desktop, Mobile, Web).
    """
    return {
        "mcp_version": "1.0",
        "intent": intent,
        "ui": {
            "type": ui_type,
            "data": data,
            "orb_state": {
                "color": "#4a90e2" if intent != "security_violation" else "#e74c3c",
                "pulse": 1.2 if intent == "reasoning" else 1.0,
                "rotation_speed": 0.5 if intent != "idle" else 0.1
            }
        },
        "tools": tools or []
    }

def validate_mcp_payload(payload: Dict[str, Any]) -> bool:
    """
    Validates that the payload conforms to the AGUI/MCP schema.
    Returns True if valid, False otherwise.
    """
    if not isinstance(payload, dict): return False
    required_keys = ["mcp_version", "intent", "ui"]
    if not all(k in payload for k in required_keys): return False
    if not isinstance(payload["ui"], dict) or "type" not in payload["ui"]: return False
    return True

def repair_mcp_payload(payload: Dict[str, Any], default_intent: str = "general") -> Dict[str, Any]:
    """
    Attempts to repair a malformed payload by injecting missing required root keys.
    """
    if not isinstance(payload, dict):
        return generate_mcp_payload(default_intent, "INFO_CARD", {"content": str(payload)})
    
    repaired = payload.copy()
    if "mcp_version" not in repaired: repaired["mcp_version"] = "1.0"
    if "intent" not in repaired: repaired["intent"] = default_intent
    if "ui" not in repaired or not isinstance(repaired["ui"], dict):
        repaired["ui"] = {"type": "INFO_CARD", "data": {"content": "System: Payload auto-repaired due to malformed UI schema."}}
    
    if "orb_state" not in repaired["ui"]:
        repaired["ui"]["orb_state"] = {"color": "#4a90e2", "pulse": 1.0, "rotation_speed": 0.5}
    
    return repaired

def create_para_dashboard_payload(view: str, items: List[Dict[str, Any]], intent: str = "PARA_MANAGEMENT") -> Dict[str, Any]:
    """
    Convenience function for PARA dashboard payloads.
    Includes hints for available PARA tools.
    """
    data = {
        "view": view, # KANBAN, TABLE, GALLERY
        "items": items
    }
    tools = [
        {"name": "query_para_database", "description": "Modify the PARA structure (CREATE, UPDATE, DELETE)"}
    ]
    return generate_mcp_payload(intent, "PARA_DASHBOARD", data, tools=tools)
