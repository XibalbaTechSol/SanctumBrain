import json
import re
from typing import Dict, Any, List
from .state import AgentState

import json
import re
import time
import os
import redis
import psutil
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .utils import log_event
# We import from .nodes to get the initialized local_model and on_device_model
from .nodes import local_model, on_device_model

class SecurityPolicy:
    """
    Defines the security and privacy levels for Sanctum OS.
    """
    LEVELS = {
        "LOCKDOWN": {
            "allow_external_tools": False,
            "pii_redaction_strictness": "MAX",
            "biometric_required_for_actions": True,
            "max_context_window": 5,
            "rate_limit_rpm": 5
        },
        "PRIVACY_FIRST": {
            "allow_external_tools": ["search"],
            "pii_redaction_strictness": "HIGH",
            "biometric_required_for_actions": True,
            "max_context_window": 10,
            "rate_limit_rpm": 20
        },
        "BALANCED": {
            "allow_external_tools": ["search", "code_exec"],
            "pii_redaction_strictness": "MEDIUM",
            "biometric_required_for_actions": False,
            "max_context_window": 20,
            "rate_limit_rpm": 60
        }
    }

    @staticmethod
    def get_policy(level: str = "BALANCED") -> Dict[str, Any]:
        return SecurityPolicy.LEVELS.get(level, SecurityPolicy.LEVELS["BALANCED"])

class AbnormalBehaviorDetector:
    """
    Detects anomalies in user interaction patterns using Redis for state.
    """
    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client

    def check_rate_limit(self, user_id: str, limit: int) -> bool:
        """Sliding window rate limiter."""
        if not self.r: return True
        key = f"rate_limit:{user_id}"
        now = time.time()
        
        # Remove old requests
        self.r.zremrangebyscore(key, 0, now - 60)
        
        # Count requests in last 60s
        count = self.r.zcard(key)
        if count >= limit:
            return False
            
        # Add current request
        self.r.zadd(key, {str(now): now})
        self.r.expire(key, 60)
        return True

    def detect_injection(self, text: str) -> bool:
        """Simple heuristic for prompt injection."""
        patterns = [
            r"ignore all previous instructions",
            r"system prompt",
            r"you are now a",
            r"developer mode",
            r"output the raw"
        ]
        for p in patterns:
            if re.search(p, text.lower()):
                return True
        return False

    def detect_intent_anomaly(self, user_id: str, current_intent: str) -> bool:
        """Detects if a user is rapidly switching to high-risk intents."""
        if not self.r: return False
        if current_intent not in ["code", "api"]: return False
        
        key = f"intent_anomaly:{user_id}"
        self.r.lpush(key, current_intent)
        self.r.ltrim(key, 0, 4) # Keep last 5 intents
        
        history = self.r.lrange(key, 0, -1)
        # If 4 out of last 5 intents are high-risk, flag anomaly
        high_risk_count = sum(1 for h in history if h in ["code", "api"])
        return high_risk_count >= 4

class SecurityAgent:
    """
    The security guard for the LangGraph orchestrator.
    """
    
    # Common PII patterns
    PII_PATTERNS = {
        "EMAIL": r'[\w\.-]+@[\w\.-]+\.\w+',
        "PHONE": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b',
        "SSN": r'\b\d{3}-\d{2}-\d{4}\b'
    }

    def __init__(self, policy_level: str = "BALANCED"):
        self.policy = SecurityPolicy.get_policy(policy_level)
        self.policy_level = policy_level
        
        # Initialize Redis for behavior detection
        try:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            self.r = redis.from_url(redis_url, decode_responses=True)
            self.detector = AbnormalBehaviorDetector(self.r)
        except:
            self.r = None
            self.detector = None

    def scrub_pii(self, text: str) -> str:
        """Smarter PII scrubbing: Regex first, then SLM if strictness is high."""
        scrubbed = text
        
        # 1. Regex-based scrubbing (Fast/Always on)
        for label, pattern in self.PII_PATTERNS.items():
            scrubbed = re.sub(pattern, f"[REDACTED_{label}]", scrubbed)
            
        # 2. SLM-based context scrubbing (Slower/Context-aware)
        if self.policy["pii_redaction_strictness"] in ["HIGH", "MAX"]:
            scrubbed = self.scrub_pii_slm(scrubbed)
            
        return scrubbed

    def scrub_pii_slm(self, text: str) -> str:
        """Uses the local SLM to identify and redact context-sensitive PII (names, specific locations, etc)."""
        prompt = (
            "You are a Sovereign Security Agent for Sanctum OS. "
            "Your task is to identify and redact sensitive information (names, specific addresses, company-secret projects) from the text. "
            "Replace sensitive entities with [REDACTED_ENTITY]. "
            "Return ONLY the redacted text, no explanations."
        )
        try:
            # We strictly use the on-device model for PII redaction to prevent data egress
            response = on_device_model.invoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"Redact this text: {text}")
            ])
            return response.content.strip()
        except Exception as e:
            log_event("SECURITY", f"SLM Redaction failed: {e}", node_id="security_agent")
            return text

    def validate_request(self, state: AgentState) -> Dict[str, Any]:
        """Checks if the incoming request/context violates any policies or shows abnormal behavior."""
        violations = []
        last_message = state["messages"][-1].content
        user_id = state.get("context", {}).get("device_id", "anonymous")
        
        # 1. Static Policy Check
        intent = state.get("intent")
        if intent == "code" and "code_exec" not in self.policy["allow_external_tools"]:
            violations.append("POLICY: CODE_EXEC_PROHIBITED")
            
        # 2. Abnormal Behavior Detection
        if self.detector:
            # Rate Limiting
            if not self.detector.check_rate_limit(user_id, self.policy["rate_limit_rpm"]):
                violations.append("BEHAVIOR: RATE_LIMIT_EXCEEDED")
                
            # Injection Heuristics
            if self.detector.detect_injection(last_message):
                violations.append("BEHAVIOR: PROMPT_INJECTION_DETECTED")
                
            # Intent Anomaly
            if self.detector.detect_intent_anomaly(user_id, intent):
                violations.append("BEHAVIOR: UNUSUAL_INTENT_PATTERN")
            
        return {
            "is_valid": len(violations) == 0,
            "violations": violations
        }

def security_ingress_node(state: AgentState):
    """
    Node to check security policies at the start of the graph.
    Also hydrates system 'Source of Truth' metrics (Pulse).
    """
    # 1. Pulse: Hydrate System Metrics
    log_event("GRAPH", "Sovereign Pulse Check", node_id="security_ingress")
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    system_status = {
        "cpu": cpu_usage, "mem": mem_usage, "disk": disk_usage,
        "vps_id": "Sanctum-Guard-01", "status": "Healthy"
    }

    # 2. Security Validation
    policy_level = state.get("context", {}).get("security_level", "BALANCED")
    agent = SecurityAgent(policy_level)
    
    log_event("SECURITY", f"Enforcing Ingress Policy: {policy_level}", node_id="security_ingress")
    check = agent.validate_request(state)
    
    if not check["is_valid"]:
        log_event("SECURITY", f"VIOLATION: {check['violations']}", node_id="security_ingress")
        return {
            "intent": "security_violation",
            "system_status": system_status,
            "reasoning_steps": [f"Security alert triggered: {v}" for v in check["violations"]]
        }
    
    # 3. Privacy: Scrub Input
    messages = state["messages"]
    last_msg = messages[-1]
    original_content = last_msg.content
    
    # Scrub the latest message if strictness is medium or higher
    if agent.policy["pii_redaction_strictness"] in ["MEDIUM", "HIGH", "MAX"]:
        last_msg.content = agent.scrub_pii(last_msg.content)
        if original_content != last_msg.content:
            log_event("SECURITY", "Privacy Layer: PII Redacted from input.", node_id="security_ingress")
    
    return {
        "system_status": system_status,
        "active_sentinels": [{"id": "sentinel-desktop", "type": "Desktop", "status": "Connected"}],
        "messages": [last_msg], 
        "reasoning_steps": ["Ingress security check passed (System Truth Hydrated)."]
    }

def security_egress_node(state: AgentState):
    """
    Node to verify the output payload doesn't leak info and matches A2UI safety.
    """
    policy_level = state.get("context", {}).get("security_level", "BALANCED")
    agent = SecurityAgent(policy_level)
    
    log_event("SECURITY", "Starting egress safety audit", node_id="security_egress")
    
    # Handle direct security violations from ingress
    if state.get("intent") == "security_violation":
        log_event("SECURITY", "Blocking output due to previous violation", node_id="security_egress")
        ui_payload = {
            "type": "render_ui",
            "component": {
                "type": "security_alert",
                "props": {
                    "title": "Access Denied",
                    "message": "The requested action violates the current security policy.",
                    "violations": state.get("reasoning_steps", [])
                }
            }
        }
        return {"ui_payload": ui_payload, "reasoning_steps": ["Egress: Returning security alert."]}

    ui_payload = state.get("ui_payload", {})
    if not ui_payload:
        return {"reasoning_steps": ["Egress: No UI payload to check."]}
        
    payload_str = json.dumps(ui_payload)
    
    # Scrub the final UI payload
    scrubbed_payload_str = agent.scrub_pii(payload_str)
    scrubbed_payload = json.loads(scrubbed_payload_str)
    
    if payload_str != scrubbed_payload_str:
        log_event("SECURITY", "Sensitive data removed from response payload.", node_id="security_egress")
    
    # Check if biometric is required for the specific component type
    if agent.policy["biometric_required_for_actions"]:
        if scrubbed_payload.get("component", {}).get("type") in ["payment_card", "system_setting"]:
            log_event("SECURITY", "Biometric verification required for high-privilege UI", node_id="security_egress")
            scrubbed_payload["requires_biometric"] = True

    log_event("SECURITY", "Egress audit complete. Payload released.", node_id="security_egress")
    return {"ui_payload": scrubbed_payload, "reasoning_steps": ["Egress security check completed."]}
