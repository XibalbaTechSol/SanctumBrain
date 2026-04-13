import asyncio
import os
from tortoise import Tortoise

TORTOISE_CONFIG = {
    "connections": {"default": os.getenv("DATABASE_URL", "postgres://sanctum:sanctum_pass@localhost:5432/sanctum_db").replace("postgresql://", "postgres://")},
    "apps": {
        "models": {
            "models": ["app.db.models"],
            "default_connection": "default",
        },
    },
}

async def generate_schemas():
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()
    print("[*] Schemas generated (including adaptive_ui_components).")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(generate_schemas())
