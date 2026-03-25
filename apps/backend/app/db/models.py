from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime
from typing import Optional, List, Dict, Any

class User(models.Model):
    id = fields.CharField(max_length=50, pk=True)
    email = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

class Project(models.Model):
    id = fields.CharField(max_length=50, pk=True)
    title = fields.CharField(max_length=255)
    goal = fields.TextField(null=True)
    deadline = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=50, default="ACTIVE")
    type = fields.CharField(max_length=50, default="PROJECT")
    user = fields.ForeignKeyField("models.User", related_name="projects", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "projects"

class Habit(models.Model):
    id = fields.CharField(max_length=50, pk=True)
    name = fields.CharField(max_length=255)
    user = fields.ForeignKeyField("models.User", related_name="habits")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "habits"

class HabitLog(models.Model):
    id = fields.UUIDField(pk=True)
    habit = fields.ForeignKeyField("models.Habit", related_name="logs")
    user = fields.ForeignKeyField("models.User", related_name="habit_logs", null=True)
    completed_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "habit_logs"

class Event(models.Model):
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    user = fields.ForeignKeyField("models.User", related_name="events")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "events"

class Area(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    responsibility_level = fields.IntField(default=1)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "areas"

class Resource(models.Model):
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    content_type = fields.CharField(max_length=50) # 'DOC', 'LINK', 'CODE', 'MEDIA', 'NOTE'
    content_payload = fields.JSONField(null=True) 
    tags = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "resources"

class Archive(models.Model):
    id = fields.UUIDField(pk=True)
    original_id = fields.UUIDField()
    original_type = fields.CharField(max_length=50) # 'PROJECT', 'AREA', 'RESOURCE'
    archived_at = fields.DatetimeField(auto_now_add=True)
    reason = fields.TextField(null=True)

    class Meta:
        table = "archives"

class SystemWorkflow(models.Model):
    id = fields.CharField(max_length=100, pk=True)
    name = fields.CharField(max_length=255)
    nodes = fields.TextField() # JSON string
    edges = fields.TextField() # JSON string
    is_active = fields.BooleanField(default=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "system_workflows"

class Nudge(models.Model):
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    type = fields.CharField(max_length=50) # 'HABIT', 'PROJECT', 'SYSTEM'
    dismissed = fields.BooleanField(default=False)
    user = fields.ForeignKeyField("models.User", related_name="nudges")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "nudges"

class McpServer(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.CharField(max_length=50) # 'STDIO', 'SSE'
    command = fields.CharField(max_length=255, null=True)
    args = fields.TextField(null=True) # JSON string
    url = fields.CharField(max_length=255, null=True)
    user = fields.ForeignKeyField("models.User", related_name="mcp_servers")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "mcp_servers"

class Review(models.Model):
    id = fields.UUIDField(pk=True)
    content = fields.TextField()
    type = fields.CharField(max_length=50) # 'DAILY', 'WEEKLY', 'MONTHLY'
    user = fields.ForeignKeyField("models.User", related_name="reviews")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reviews"

class PushToken(models.Model):
    id = fields.UUIDField(pk=True)
    token = fields.CharField(max_length=255)
    device_type = fields.CharField(max_length=50) # 'IOS', 'ANDROID', 'WEB'
    user = fields.ForeignKeyField("models.User", related_name="push_tokens")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "push_tokens"

class InboxItem(models.Model):
    id = fields.UUIDField(pk=True)
    content = fields.TextField()
    source = fields.CharField(max_length=50, default="WEB") # 'WEB', 'VOICE', 'EMAIL'
    processed = fields.BooleanField(default=False)
    user = fields.ForeignKeyField("models.User", related_name="inbox_items")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "inbox_items"

class NodeEvent(models.Model):
    id = fields.UUIDField(pk=True)
    node_id = fields.CharField(max_length=100)
    workflow_id = fields.CharField(max_length=100, default="active-workflow")
    type = fields.CharField(max_length=50) # 'INFO', 'ERROR', 'SUCCESS'
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "node_events"

# Pydantic models
Project_Pydantic = pydantic_model_creator(Project, name="Project_Pydantic")
Area_Pydantic = pydantic_model_creator(Area, name="Area_Pydantic")
Resource_Pydantic = pydantic_model_creator(Resource, name="Resource_Pydantic")
Archive_Pydantic = pydantic_model_creator(Archive, name="Archive_Pydantic")
User_Pydantic = pydantic_model_creator(User, name="User_Pydantic")
Habit_Pydantic = pydantic_model_creator(Habit, name="Habit_Pydantic")
