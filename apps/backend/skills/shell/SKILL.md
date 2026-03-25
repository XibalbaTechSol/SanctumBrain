---
name: Shell Execution Skill
description: Allows the agent to run commands on the VPS environment (Sanctum Guard).
user-invocable: true
metadata: {"category": "system", "version": "1.0.0"}
---

# Shell Execution Skill

## When to use
- Use this skill whenever a system task is required: `git` operations, `npm` builds, checking `docker` status, or searching logs.
- Use this skill to investigate the system state (e.g., `whoami`, `pwd`, `ls`).

## Workflow
1. **Plan:** Before running a command, describe what you expect to achieve and why this command is safe.
2. **Execute:** Run the command in the shell environment.
3. **Observe:** Capture both `stdout` and `stderr`.
4. **Reflect:** If the command fails, analyze the error. If it succeeds, use the output to inform the next step in your agentic loop.

## Guardrails
- **No Self-Destruct:** Never run `rm -rf /` or similar destructive commands on the system.
- **No Lockout:** Do not modify `ssh` configurations or `iptables` rules that could lock the user out of the VPS.
- **Timeout:** Commands that take too long should be killed or run in the background with a PID check.

## Response Pattern
- Output the result in a code block: ` ```bash ... ``` `.
- Summarize the outcome in one line if the output is large.
