import os
import subprocess
from typing import Dict, Any, List
import requests
from .security import SecurityAgent

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

    def execute_shell(self, command: str) -> str:
        """Executes a shell command in a controlled environment."""
        if "code_exec" not in self.security.policy["allow_external_tools"]:
            return "Error: Shell execution is prohibited."
            
        print(f"[*] Tool: Executing shell command: {command}")
        try:
            # Note: In production, use a more restricted environment
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout or "Command executed successfully (no output)."
            else:
                return f"Error ({result.returncode}): {result.stderr}"
        except Exception as e:
            return f"Exception: {e}"

def tool_node(state: Dict[str, Any]):
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
        
    return {
        "reasoning_steps": [f"Tool execution completed for intent: {intent}"],
        "tool_output": result
    }
