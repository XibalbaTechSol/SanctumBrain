import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import Hermes registry
try:
    from tools.registry import registry
except ImportError:
    # Fallback for different import paths
    import sys
    import os
    HERMES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "hermes")
    if HERMES_PATH not in sys.path:
        sys.path.append(HERMES_PATH)
    from tools.registry import registry

# Import Sanctum models
try:
    from app.db.models import Project, Area, Resource, Archive, Event, User
    from app.rag import retrieve_context
except ImportError:
    try:
        from db.models import Project, Area, Resource, Archive, Event, User
        from rag import retrieve_context
    except ImportError:
        # Try relative import if part of package
        try:
            from ..db.models import Project, Area, Resource, Archive, Event, User
            from ..rag import retrieve_context
        except ImportError:
            # Last ditch: add parent to path
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from db.models import Project, Area, Resource, Archive, Event, User
            from rag import retrieve_context

logger = logging.getLogger(__name__)

# --- Knowledge Retrieval Tool ---

async def retrieve_knowledge(args: Dict[str, Any]) -> str:
    """
    Retrieves relevant information from the private Sanctum memory (RAG).
    Args:
        query: The semantic search query.
        k: Number of chunks to retrieve (default 3).
    """
    query = args.get("query")
    k = args.get("k", 3)
    if not query: return "Error: Missing query"
    
    try:
        result = retrieve_context(query, k=k)
        context_text = "\n---\n".join(result.get("context_strings", []))
        return f"Retrieved Context:\n{context_text}"
    except Exception as e:
        return f"Retrieval Error: {e}"

# --- PARA Database Tool ---

async def query_para_database(args: Dict[str, Any]) -> str:
    """
    Queries or modifies the PARA (Projects, Areas, Resources, Archives) database.
    Args:
        action: 'LIST', 'CREATE', 'UPDATE', 'DELETE'
        type: 'PROJECT', 'AREA', 'RESOURCE', 'ARCHIVE'
        params: dict of properties (title, goal, status, etc.)
    """
    action = args.get("action", "LIST").upper()
    entity_type = args.get("type", "PROJECT").upper()
    params = args.get("params", {})
    
    try:
        model_map = {
            "PROJECT": Project,
            "AREA": Area,
            "RESOURCE": Resource,
            "ARCHIVE": Archive
        }
        
        model = model_map.get(entity_type)
        if not model:
            return json.dumps({"error": f"Unsupported type: {entity_type}"})

        if action == "LIST":
            items = await model.all().limit(20).values()
            return json.dumps([dict(i) for i in items], default=str)
            
        elif action == "CREATE":
            item = await model.create(**params)
            return f"Successfully created {entity_type}: {getattr(item, 'title', getattr(item, 'name', item.id))}"
            
        elif action == "UPDATE":
            item_id = params.get("id")
            if not item_id: return "Error: Missing ID for update"
            item = await model.get_or_none(id=item_id)
            if item:
                # Update attributes
                for k, v in params.items():
                    if k != "id" and hasattr(item, k):
                        setattr(item, k, v)
                await item.save()
                return f"Updated {entity_type}: {item_id}"
            return f"Error: {entity_type} not found"
            
        elif action == "DELETE":
            item_id = params.get("id")
            if not item_id: return "Error: Missing ID for deletion"
            item = await model.get_or_none(id=item_id)
            if item:
                await item.delete()
                return f"Deleted {entity_type}: {item_id}"
            return f"Error: {entity_type} not found"

        return f"Error: Unsupported action {action}"
    except Exception as e:
        return f"Database Error: {e}"

# --- Calendar Tool ---

async def manage_calendar_events(args: Dict[str, Any]) -> str:
    """
    Manages calendar events in the SanctumBrain database.
    Args:
        action: 'LIST', 'CREATE', 'UPDATE', 'DELETE'
        params: dict (title, description, start_time, end_time, etc.)
    """
    action = args.get("action", "LIST").upper()
    params = args.get("params", {})
    
    try:
        if action == "LIST":
            events = await Event.all().order_by("start_time").limit(20).values()
            return json.dumps([dict(e) for e in events], default=str)
            
        elif action == "CREATE":
            # Basic validation
            if "start_time" in params: params["start_time"] = datetime.fromisoformat(params["start_time"])
            if "end_time" in params: params["end_time"] = datetime.fromisoformat(params["end_time"])
            
            # Find default user for now
            user = await User.first()
            if not user: return "Error: No user found to associate event."
            
            event = await Event.create(user=user, **params)
            return f"Event created: {event.title} at {event.start_time}"
            
        elif action == "DELETE":
            event_id = params.get("id")
            event = await Event.get_or_none(id=event_id)
            if event:
                await event.delete()
                return f"Event deleted: {event_id}"
            return "Event not found."

        return f"Unsupported calendar action: {action}"
    except Exception as e:
        return f"Calendar Error: {e}"

# --- Registration ---

PARA_SCHEMA = {
    "name": "query_para_database",
    "description": "Access or modify the PARA knowledge structure (Projects, Areas, Resources, Archives).",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["LIST", "CREATE", "UPDATE", "DELETE"]},
            "type": {"type": "string", "enum": ["PROJECT", "AREA", "RESOURCE", "ARCHIVE"]},
            "params": {
                "type": "object",
                "description": "Entity properties (title, goal, status, id for update/delete)."
            }
        },
        "required": ["action", "type"]
    }
}

CALENDAR_SCHEMA = {
    "name": "manage_calendar_events",
    "description": "Read, create or remove events from the user's personal calendar.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["LIST", "CREATE", "UPDATE", "DELETE"]},
            "params": {
                "type": "object",
                "description": "Event properties (title, start_time, end_time, id for deletion)."
            }
        },
        "required": ["action"]
    }
}

KNOWLEDGE_SCHEMA = {
    "name": "retrieve_knowledge",
    "description": "Query the private Sanctum memory for relevant historical context, notes, or project information.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query to retrieve information for."},
            "k": {"type": "integer", "description": "Number of relevant chunks to return."}
        },
        "required": ["query"]
    }
}

def register_sanctum_tools():
    registry.register(
        name="retrieve_knowledge",
        toolset="sanctum",
        schema=KNOWLEDGE_SCHEMA,
        handler=retrieve_knowledge,
        is_async=True,
        emoji="🧠"
    )
    
    registry.register(
        name="query_para_database",
        toolset="sanctum",
        schema=PARA_SCHEMA,
        handler=query_para_database,
        is_async=True,
        emoji="🗂️"
    )
    
    registry.register(
        name="manage_calendar_events",
        toolset="sanctum",
        schema=CALENDAR_SCHEMA,
        handler=manage_calendar_events,
        is_async=True,
        emoji="📅"
    )

# Auto-register on import
register_sanctum_tools()

try:
    from app.tools.agui_tools import register_agui_tools
except ImportError:
    from tools.agui_tools import register_agui_tools

register_agui_tools()
