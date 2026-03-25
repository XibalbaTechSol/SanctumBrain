---
name: File Management Skill
description: Allows the agent to read, write, and organize files on the VPS (Sanctum Guard).
user-invocable: true
metadata: {"category": "filesystem", "version": "1.0.0"}
---

# File Management Skill

## When to use
- Use this skill to manage your own **Memory** and **PARA v2 Schema**.
- Use this skill to read documentation, code, or existing project files to gather context.
- Use this skill to update the `SOUL.md` or other system-level agent files based on user preferences.

## Workflow
1. **Locate:** Use `find` or `ls` to identify the target file or directory.
2. **Read:** Use `cat` or `tail` to understand the file's content.
3. **Write/Edit:** Use `sed`, `grep`, or complete file writes (`write_file`) to apply changes.
4. **Validate:** Verify that the change was successful (e.g., `cat` the updated content).

## Guardrails
- **No Overwrites:** Do not overwrite files without first reading them to understand their purpose.
- **Privacy:** Never write PII (Passwords, Keys) to a plaintext file.
- **Backup:** Create a `.bak` copy for system-level configuration files before modification.

## Response Pattern
- Summarize the change: "Updated `SOUL.md` with new user preference for TypeScript."
- Use file paths relative to the project root.
