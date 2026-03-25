import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "system.log")

def log_event(event_type, msg, extra=None, node_id=None):
    """Writes an event to the system log for the dashboard."""
    event = {
        "type": event_type,
        "msg": msg,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    if node_id:
        event["node_id"] = node_id
        
    if extra:
        event.update(extra)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
