import os
import subprocess
from typing import Dict, Any, List
import requests
import json

try:
    from .security import SecurityAgent
    from .db.models import Project, Area, InboxItem, SystemWorkflow
except ImportError:
    from security import SecurityAgent
    from db.models import Project, Area, InboxItem, SystemWorkflow

class SanctumToolBox:
    """
    A collection of tools that the Sanctum OS Agent can use,
    wrapped in security checks.
    """
    
    def __init__(self, policy_level: str = "BALANCED"):
        self.policy_level = policy_level
        self.security = SecurityAgent(policy_level)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def web_search(self, query: str) -> str:
        if "search" not in self.security.policy["allow_external_tools"]:
            return "Error: Web search is prohibited by security policy."
        print(f"[*] Tool: Searching web for '{query}'...")
        return f"Results for '{query}': [1] Sanctum OS documentation... [2] Secure agent architectures..."

    def secure_api_call(self, method: str, url: str, data: Dict = None) -> str:
        allowed_domains = ["api.enterprise.com", "internal.vault.local"]
        domain = url.split("//")[-1].split("/")[0]
        if domain not in allowed_domains:
            return f"Error: Domain {domain} is not in the enterprise allowlist."
        print(f"[*] Tool: Calling secure API {url}...")
        return "Success: API response received (Mocked)."

    def list_files(self, path: str = ".") -> str:
        """Lists files in the project directory."""
        if "file_system" not in self.security.policy["allow_external_tools"]:
            return "Error: File system access is prohibited."
        
        target_path = os.path.abspath(os.path.join(self.base_dir, path))
        if not target_path.startswith(self.base_dir):
            return "Error: Access denied (Path traversal)."
            
        try:
            items = os.listdir(target_path)
            return "\n".join(items)
        except Exception as e:
            return f"Error: {e}"

    def read_file(self, file_path: str) -> str:
        """Reads a file from the project directory."""
        if "file_system" not in self.security.policy["allow_external_tools"]:
            return "Error: File system access is prohibited."
            
        target_path = os.path.abspath(os.path.join(self.base_dir, file_path))
        if not target_path.startswith(self.base_dir):
            return "Error: Access denied."
            
        try:
            with open(target_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"

    def read_system_logs(self, limit: int = 50) -> str:
        """Reads the 'system.log' for debugging execution traces."""
        log_path = os.path.join(self.base_dir, "system.log")
        if not os.path.exists(log_path):
            return "Error: system.log not found."
            
        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
                return "".join(lines[-limit:])
        except Exception as e:
            return f"Error reading logs: {e}"

    async def query_para_database(self, entity_type: str, action: str = "LIST", params: Dict = None) -> str:
        """Direct CRUD access to PARA databases."""
        try:
            if entity_type.upper() == "PROJECT":
                if action == "LIST":
                    items = await Project.all().limit(20).values()
                    return json.dumps([dict(i) for i in items], default=str)
            elif entity_type.upper() == "AREA":
                if action == "LIST":
                    items = await Area.all().limit(20).values()
                    return json.dumps([dict(i) for i in items], default=str)
            elif entity_type.upper() == "INBOX":
                if action == "LIST":
                    items = await InboxItem.all().order_by("-created_at").limit(20).values()
                    return json.dumps([dict(i) for i in items], default=str)
            return f"Error: Unsupported entity {entity_type} or action {action}"
        except Exception as e:
            return f"Database Error: {e}"

    async def manage_automation(self, action: str = "READ", workflow_id: str = "active-workflow", data: Dict = None) -> str:
        """Reads or modifies system workflows/automation graph."""
        try:
            if action == "READ":
                wf = await SystemWorkflow.get_or_none(id=workflow_id)
                if not wf:
                    # Fallback to local config file if DB record doesn't exist
                    config_path = os.path.join(self.base_dir, "graph_config.json")
                    if os.path.exists(config_path):
                        with open(config_path, "r") as f:
                            return f.read()
                    return json.dumps({"nodes": "[]", "edges": "[]"})
                return json.dumps({"id": wf.id, "name": wf.name, "nodes": wf.nodes, "edges": wf.edges})
            
            elif action == "SAVE":
                if not data:
                    return "Error: No data provided for saving."
                
                wf, created = await SystemWorkflow.get_or_create(id=workflow_id)
                wf.name = data.get("name", wf.name or "Untitled Scenario")
                wf.nodes = json.dumps(data.get("nodes", [])) if isinstance(data.get("nodes"), list) else data.get("nodes", "[]")
                wf.edges = json.dumps(data.get("edges", [])) if isinstance(data.get("edges"), list) else data.get("edges", "[]")
                await wf.save()
                return json.dumps({"status": "success", "id": wf.id, "created": created})
            
            elif action == "LIST":
                wfs = await SystemWorkflow.all().values("id", "name", "updated_at")
                return json.dumps(list(wfs), default=str)
                
            return f"Error: Action {action} not implemented."
        except Exception as e:
            return f"Automation Error: {e}"

async def tool_node(state: Dict[str, Any]):
    """
    The LangGraph node that executes tool calls.
    Expects the last message to contain a tool request if intent matches.
    """
    intent = state.get("intent")
    query = state["messages"][-1].content
    policy_level = state.get("system_status", {}).get("security_level", "BALANCED")
    toolbox = SanctumToolBox(policy_level)
    
    result = ""
    if intent == "knowledge":
        result = toolbox.web_search(query)
    elif intent == "code":
        # Check if it's a shell command or python code
        if "ls " in query or "cat " in query or "pwd" in query:
            # Very simple parser for now
            cmd = query.split("run ")[-1] if "run " in query else query
            result = toolbox.execute_shell(cmd)
        else:
            result = "Error: Please specify 'run [command]' for shell execution."
    elif intent == "api":
        result = toolbox.secure_api_call("GET", "https://api.enterprise.com/status")
    elif intent == "system_health":
        result = toolbox.read_system_logs()
    elif intent == "para":
        result = await toolbox.query_para_database("PROJECT", "LIST")
    elif intent == "automation":
        result = await toolbox.manage_automation("READ")
        
    return {
        "reasoning_steps": [f"System-wide tool execution completed: {intent}"],
        "tool_output": result
    }
