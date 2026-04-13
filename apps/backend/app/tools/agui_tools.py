import json
import logging
from typing import Dict, Any, List

# Import Hermes registry
try:
    from tools.registry import registry
except ImportError:
    import sys
    import os
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    HERMES_PATH = os.path.join(PROJECT_ROOT, "hermes")
    if HERMES_PATH not in sys.path:
        sys.path.append(HERMES_PATH)
    from tools.registry import registry

logger = logging.getLogger(__name__)

async def render_generative_ui(args: Dict[str, Any]) -> str:
    """
    Directly dictates the AGUI/A2UI protocol payload for the client interface.
    Use this to synthesize specialized interfaces (dashboards, cards, maps, etc.) 
    instead of just returning text.
    
    Args:
        intent: The high-level intent (e.g., 'CALENDAR', 'PARA_MANAGEMENT', 'SECURITY_AUDIT').
        ui_type: The component type (e.g., 'INFO_CARD', 'PARA_DASHBOARD', 'CHART', 'MAP').
        payload: The specific data object required by the component.
    """
    intent = args.get("intent", "general")
    ui_type = args.get("ui_type", "INFO_CARD")
    payload = args.get("payload", {})

    # We return a structured string that the aura_orchestrator can parse
    # and use to update the state's mcp_ui_payload.
    result = {
        "status": "UI_SYNTHESIS_REQUESTED",
        "intent": intent,
        "ui_type": ui_type,
        "payload": payload
    }
    return json.dumps(result)

AGUI_SCHEMA = {
    "name": "render_generative_ui",
    "description": "Synthesize a generative UI component (AGUI Atom) for the mobile or web client. Use this whenever a specialized visualization is better than text.",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string", 
                "description": "High-level goal of the UI (e.g. CALENDAR, RESOURCE_LIST)."
            },
            "ui_type": {
                "type": "string",
                "enum": ["INFO_CARD", "PARA_DASHBOARD", "ANALYTICS_CHART", "SECURITY_ALERT", "MEDIA_PLAYER"],
                "description": "The specific AGUI component to render."
            },
            "payload": {
                "type": "object",
                "description": "The data properties for the component (e.g. {items: [...], title: '...'})"
            }
        },
        "required": ["intent", "ui_type", "payload"]
    }
}

def register_agui_tools():
    registry.register(
        name="render_generative_ui",
        toolset="agui",
        schema=AGUI_SCHEMA,
        handler=render_generative_ui,
        is_async=True,
        emoji="✨"
    )
