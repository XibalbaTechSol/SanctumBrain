import json
import time
import requests
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from app.db.models import User, Nudge, PlatformConfig
from app.utils import log_event

logger = logging.getLogger(__name__)

class NudgeSystem:
    """
    Proactive behavior nudge engine.
    Analyzes user goals and context to dispatch encouraging messages via messaging platforms.
    """
    
    @staticmethod
    async def evaluate_and_nudge(user_id: str):
        """
        Main entry point for evaluating if a user needs a nudge.
        """
        user = await User.get_or_none(id=user_id).prefetch_related("projects", "nudges")
        if not user:
            return

        # 1. Fetch active goals/projects
        projects = await user.projects.filter(status="ACTIVE")
        if not projects:
            return

        # 2. Logic: Simple 'proactive check-in' for now
        # In a real system, this would use an LLM to analyze recent chat context vs goals
        for project in projects:
            # Check if we've already nudged for this project today
            today = datetime.now().date()
            existing_nudge = await Nudge.filter(
                user=user, 
                title__icontains=project.title,
                created_at__gte=today
            ).exists()

            if not existing_nudge:
                nudge_content = f"Sovereign Alert: Your project '{project.title}' is still in focus. Have you made any progress toward your goal of '{project.goal}' today?"
                
                # Save nudge to DB
                await Nudge.create(
                    user=user,
                    title=f"Goal Nudge: {project.title}",
                    content=nudge_content,
                    type="PROJECT"
                )
                
                # Dispatch to platforms
                await NudgeSystem.dispatch_nudge(user_id, nudge_content)
                log_event("NUDGE", f"Dispatched nudge for {project.title} to user {user_id}")

    @staticmethod
    async def dispatch_nudge(user_id: str, content: str):
        """
        Sends the nudge message to all active messaging platforms.
        """
        active_platforms = await PlatformConfig.filter(is_active=True)
        
        for config in active_platforms:
            if config.platform == "TELEGRAM":
                await NudgeSystem._send_telegram(config.api_token, user_id, content)
            elif config.platform == "WHATSAPP":
                await NudgeSystem._send_whatsapp(config.api_token, user_id, content)

    @staticmethod
    async def _send_telegram(token: str, chat_id: str, text: str):
        """Helper to send telegram message via bot API."""
        # Note: chat_id needs to be the actual telegram chat ID, 
        # which should be stored in the User model or a mapping table.
        # For now, we assume user_id is the chat_id for simplicity in this prototype.
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            resp = requests.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }, timeout=5)
            if resp.status_code != 200:
                logger.error(f"Telegram Nudge Failed: {resp.text}")
        except Exception as e:
            logger.error(f"Telegram Connection Error: {e}")

    @staticmethod
    async def _send_whatsapp(token: str, phone_number: str, text: str):
        """Helper to send WhatsApp message via Meta API."""
        # Similar to Telegram, uses Meta Cloud API
        logger.info(f"WhatsApp Nudge Simulation: {text} to {phone_number}")
        # Implementation of Meta API call would go here
