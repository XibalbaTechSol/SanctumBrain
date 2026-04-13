import asyncio
import os
import json
from tortoise import Tortoise
from app.db.models import AdaptiveUIComponent

TORTOISE_CONFIG = {
    "connections": {"default": os.getenv("DATABASE_URL", "postgres://sanctum:sanctum_pass@localhost:5432/sanctum_db").replace("postgresql://", "postgres://")},
    "apps": {
        "models": {
            "models": ["app.db.models"],
            "default_connection": "default",
        },
    },
}

async def seed_adaptive_ui():
    await Tortoise.init(config=TORTOISE_CONFIG)
    
    # Banking UI Template
    banking_manifest = {
        "mcp_version": "1.0",
        "intent": "BANKING",
        "ui": {
            "type": "ADAPTIVE_DASHBOARD",
            "data": {
                "title": "Sovereign Wealth Overview",
                "accounts": [
                    {"label": "Direct Sovereign", "balance": "$85,240.00", "trend": "+2.4%"},
                    {"label": "Private Vault", "balance": "12.45 BTC", "trend": "+1.1%"}
                ],
                "recent_activity": []
            },
            "theme": {
                "primary": "#10b981", # Emerald
                "glass": True
            }
        }
    }
    
    await AdaptiveUIComponent.update_or_create(
        id="BANKING_UI",
        defaults={
            "name": "Sovereign Banking Adaptive Template",
            "component_type": "ADAPTIVE_DASHBOARD",
            "manifest": json.dumps(banking_manifest),
            "adaptive_rules": {"mode": "high_security", "density": "comfortable"}
        }
    )
    
    # Weather UI Template
    weather_manifest = {
        "mcp_version": "1.0",
        "intent": "WEATHER",
        "ui": {
            "type": "WEATHER_CARD",
            "data": {
                "location": "Sovereign Nest",
                "temp": "22°C",
                "condition": "Clear Blue"
            }
        }
    }
    
    await AdaptiveUIComponent.update_or_create(
        id="WEATHER_UI",
        defaults={
            "name": "Kinetic Weather Template",
            "component_type": "WEATHER_CARD",
            "manifest": json.dumps(weather_manifest)
        }
    )
    
    print("[*] Adaptive UI Seeding Complete (Banking & Weather).")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed_adaptive_ui())
