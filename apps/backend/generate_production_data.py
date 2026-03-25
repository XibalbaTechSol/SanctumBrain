import asyncio
import os
import random
import uuid
from datetime import datetime, timedelta
from tortoise import Tortoise, run_async
from app.db.models import User, Project, Habit, HabitLog, Event, InboxItem, Resource, Area
from app.rag import ingest_text

# Tortoise ORM Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sanctum:sanctum_pass@127.0.0.1:5432/sanctum_db")
# Tortoise expects postgres:// instead of postgresql://
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://")

TORTOISE_CONFIG = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.db.models"],
            "default_connection": "default",
        },
    },
}

# Templates for realistic data
PROJECT_TEMPLATES = [
    ("Neural Core Alpha", "Developing the primary gRPC orchestration layer."),
    ("Bio-Signal Sync", "Integrating wearable biometric data into the agent stream."),
    ("Quantified Self 2.0", "Advanced PARA-based personal dashboard."),
    ("Sovereign VPS Guard", "Hardening the Linux kernel for private compute."),
    ("Living Canvas UI", "Next.js 15 based kinetic interface development."),
    ("Agentic Memory RAG", "OpenSearch vector pipeline for long-term persistence."),
    ("Voice Synthesis Lab", "Low-latency edge TTS/STT optimization."),
    ("Decentralized Web", "Peer-to-peer data synchronization protocols."),
    ("Smart Home Automations", "IoT bridging for the Sanctum OS."),
    ("Legacy Migration", "Moving old Evernote data to PARA structure.")
]

HABITS = ["Meditation", "Deep Work", "Exercise", "Read Research Paper", "Write Documentation", "Review Goals", "Hydrate", "Cold Shower"]
EVENT_TITLES = ["Standup Sync", "Focus Block", "Deep Inference Session", "Brainstorming", "Review Session", "System Maintenance", "Client Meeting", "Project Deep-Dive"]
INBOX_CONTENT = [
    "Check this link: https://arxiv.org/abs/2401.0000",
    "Buy more NVLink cables for the cluster.",
    "Refactor the gRPC handshake logic.",
    "Draft the SOUL.md for the new personality layer.",
    "Reminder: Backup the Postgres data volume.",
    "Read: The future of autonomous agent ecosystems.",
    "Someone mentioned a new Rust-based vector store.",
    "Schedule a physical health checkup.",
    "Investigate the 500 error in the Habits widget.",
    "Idea: Dynamic kinetic transitions for the Orb."
]

AREAS = ["Personal Health", "Financial Independence", "Open Source Projects", "Professional Growth", "System Architecture", "Household Management"]

async def generate_data():
    print("[*] Initializing Database...")
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    user_id = "demo-user-id"
    user, created = await User.get_or_create(
        id=user_id,
        defaults={"email": "demo@user.com", "name": "Demo User"}
    )
    if created:
        print(f"[+] Created Demo User: {user_id}")
    else:
        print(f"[*] Using Existing Demo User: {user_id}")

    now = datetime.now()
    start_date = now - timedelta(days=5*365) # 5 years ago

    print(f"[*] Generating 5 years of data starting from {start_date.date()}...")

    # 1. Generate Areas
    print("[*] Generating Areas...")
    area_objs = []
    for a_name in AREAS:
        area = await Area.create(name=a_name, responsibility_level=random.randint(1, 5))
        area_objs.append(area)

    # 2. Generate Projects
    print("[*] Generating Projects...")
    statuses = ["ACTIVE", "COMPLETED", "ON_HOLD", "ARCHIVED"]
    for i in range(50):
        title, goal = random.choice(PROJECT_TEMPLATES)
        p_id = f"p-{uuid.uuid4().hex[:8]}"
        created_at = start_date + timedelta(days=random.randint(0, 5*365))
        await Project.create(
            id=p_id,
            title=f"{title} #{i}",
            goal=goal,
            status=random.choice(statuses),
            user=user,
            created_at=created_at,
            deadline=created_at + timedelta(days=random.randint(30, 180))
        )

    # 3. Generate Habits and Logs
    print("[*] Generating Habits and 5 years of logs...")
    for h_name in HABITS:
        habit = await Habit.create(id=f"h-{uuid.uuid4().hex[:8]}", name=h_name, user=user)
        # Create logs for ~80% of days
        logs_to_create = []
        current_day = start_date
        while current_day < now:
            if random.random() < 0.8:
                logs_to_create.append(HabitLog(
                    id=uuid.uuid4(),
                    habit=habit,
                    user=user,
                    completed_at=current_day + timedelta(hours=random.randint(6, 22))
                ))
            current_day += timedelta(days=1)
            
            # Bulk create every 1000 logs to avoid memory issues
            if len(logs_to_create) >= 1000:
                await HabitLog.bulk_create(logs_to_create)
                logs_to_create = []
        
        if logs_to_create:
            await HabitLog.bulk_create(logs_to_create)

    # 4. Generate Events
    print("[*] Generating 1500+ Events...")
    events_to_create = []
    for _ in range(1500):
        start_time = start_date + timedelta(days=random.randint(0, 5*365), hours=random.randint(0, 23))
        end_time = start_time + timedelta(minutes=random.choice([30, 60, 90, 120]))
        events_to_create.append(Event(
            id=uuid.uuid4(),
            title=random.choice(EVENT_TITLES),
            description="System generated historical event.",
            start_time=start_time,
            end_time=end_time,
            user=user
        ))
        if len(events_to_create) >= 500:
            await Event.bulk_create(events_to_create)
            events_to_create = []
    if events_to_create:
        await Event.bulk_create(events_to_create)

    # 5. Generate Inbox Items
    print("[*] Generating Inbox Items...")
    for _ in range(300):
        await InboxItem.create(
            id=uuid.uuid4(),
            content=random.choice(INBOX_CONTENT),
            source=random.choice(["WEB", "VOICE", "EMAIL"]),
            processed=random.choice([True, False]),
            user=user,
            created_at=start_date + timedelta(days=random.randint(0, 5*365))
        )

    # 6. Generate RAG Memory (Vector Store)
    print("[*] Generating RAG Memory chunks...")
    rag_topics = [
        "Architecture of the Sanctum Brain system.",
        "How to scale LangGraph nodes across multiple VPS instances.",
        "Security protocols for gRPC A2A communication.",
        "PARA method: Projects, Areas, Resources, Archives.",
        "Optimizing OpenSearch for high-dimensional vector search.",
        "Biometric data integration for personalized agent response.",
        "Thermal management of edge compute clusters.",
        "Historical data trends in personal habit tracking.",
        "Privacy-first LLM inference using local SLM layers.",
        "Dynamic UI rendering via AGUI JSON manifests."
    ]
    for _ in range(100):
        topic = random.choice(rag_topics)
        content = f"Memory Entry: {topic} Synthetic detail about {topic.lower()}. This ensures RAG retrieval has high-density clusters over time."
        # Use ingest_text from rag.py
        ingest_text(content, metadata={"topic": topic, "source": "synthetic_generator"})

    print("[SUCCESS] 5 Years of dynamic content successfully ingested.")
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(generate_data())
