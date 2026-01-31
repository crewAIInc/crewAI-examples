# 🛡️ Agent OS Safety Governance for CrewAI

This example demonstrates how to add **kernel-level safety governance** to your CrewAI agents using [Agent OS](https://github.com/imran-siddique/agent-os).

## The Problem

CrewAI agents are powerful, but they can hallucinate dangerous operations:
- `rm -rf /` - Delete everything
- `sudo` commands - Privilege escalation
- `chmod 777` - Open permissions to everyone
- Accessing sensitive paths like `/etc/passwd`

Prompt engineering alone cannot reliably prevent these issues.

## The Solution

Agent OS provides a **kernel-level safety layer** that intercepts operations BEFORE they execute:

```
Agent wants to run: rm -rf /home/user/*
         ↓
    Agent OS Kernel
         ↓
    Policy Check: BLOCKED ❌
         ↓
    Agent receives: PermissionError
```

## Quick Start

```bash
# No dependencies needed for the demo!
python main.py
```

## What You'll See

1. **Cleanup Bot** tries to delete files → **BLOCKED** 🚫
2. **Data Analyst** reads CSV files → **ALLOWED** ✅
3. **Deploy Bot** tries `sudo` → **BLOCKED** 🚫

```
╔═══════════════════════════════════════════════════════════╗
║  🚫 ACCESS DENIED - POLICY VIOLATION                      ║
╠═══════════════════════════════════════════════════════════╣
║  Action:  rm -rf /home/user/Downloads/*                   ║
║  Reason:  Destructive file operation detected             ║
║  Status:  BLOCKED BY KERNEL                               ║
╚═══════════════════════════════════════════════════════════╝
```

## Production Integration

For production use with real CrewAI crews:

```python
from crewai import Agent, Task, Crew
from agent_os import AgentOSKernel

# Your normal CrewAI setup
analyst = Agent(
    role="Data Analyst",
    goal="Analyze sales data",
    backstory="Expert data analyst"
)

task = Task(
    description="Analyze Q4 sales and generate report",
    agent=analyst
)

crew = Crew(agents=[analyst], tasks=[task])

# Wrap with Agent OS (one line!)
kernel = AgentOSKernel(policy="strict")
safe_crew = kernel.wrap(crew)

# Now it's protected - dangerous ops will be blocked
result = safe_crew.kickoff()
```

## Configuration

Create `.agentos.yml` in your project:

```yaml
version: "1.0"
policy: strict

rules:
  file_operations:
    allow:
      - read
      - list
    deny:
      - delete
      - modify
  
  commands:
    deny:
      - sudo
      - rm -rf
      - chmod 777
  
  paths:
    deny:
      - /etc/*
      - /var/*
      - /root/*
```

## Why Kernel-Level?

| Approach | Reliability | Bypass Risk |
|----------|-------------|-------------|
| Prompt Engineering | Low | High |
| Output Filtering | Medium | Medium |
| **Agent OS Kernel** | **High** | **Low** |

Agent OS operates at the system call level, making it much harder to bypass than prompt-based solutions.

## Learn More

- **GitHub**: https://github.com/imran-siddique/agent-os
- **Documentation**: Coming soon
- **Discord**: Coming soon

## License

MIT - Use freely in your projects!
