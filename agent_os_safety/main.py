#!/usr/bin/env python3
"""
🛡️ Agent OS Safety Governance for CrewAI
=========================================

This example demonstrates how to add kernel-level safety governance
to your CrewAI agents using Agent OS.

What it shows:
- CrewAI agents attempt dangerous operations (rm -rf, sudo, etc.)
- Agent OS kernel intercepts and BLOCKS these operations
- Safe operations (file reads) are ALLOWED
- Full audit logging of all agent actions

Run:
    python main.py

For production use:
    pip install agent-os
    # Then wrap your crew with AgentOSKernel

Learn more: https://github.com/imran-siddique/agent-os
"""

import time
from datetime import datetime
from typing import Any

# ============================================================================
# ANSI Colors for Terminal Output
# ============================================================================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🛡️  AGENT OS - Safety Governance for CrewAI            ║
    ║                                                           ║
    ║   Kernel-level safety for autonomous AI agents            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}""")

def print_section(title: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}  {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'─' * 60}{Colors.RESET}\n")

def print_blocked(action: str, reason: str):
    print(f"""
{Colors.RED}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║  🚫 ACCESS DENIED - POLICY VIOLATION                      ║
    ╠═══════════════════════════════════════════════════════════╣
    ║                                                           ║
    ║  Action:  {action:<47} ║
    ║  Reason:  {reason:<47} ║
    ║  Status:  BLOCKED BY KERNEL                               ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}""")

def print_allowed(action: str):
    print(f"{Colors.GREEN}  ✅ ALLOWED:{Colors.RESET} {action}")

def print_log(level: str, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    color = {
        "INFO": Colors.CYAN,
        "WARN": Colors.YELLOW,
        "ERROR": Colors.RED,
        "BLOCK": Colors.RED + Colors.BOLD,
    }.get(level, Colors.WHITE)
    print(f"  {Colors.WHITE}[{timestamp}]{Colors.RESET} {color}[{level}]{Colors.RESET} {message}")


# ============================================================================
# Agent OS Kernel (Safety Layer)
# ============================================================================

class SafetyPolicy:
    """
    Defines what operations are allowed/blocked.
    
    In production, this would be configured via .agentos.yml or API.
    """
    
    BLOCKED_OPERATIONS = [
        ("os.remove", "Destructive file operation"),
        ("os.unlink", "Destructive file operation"),
        ("shutil.rmtree", "Destructive file operation"),
        ("rm -rf", "Destructive file operation"),
        ("rm -r", "Destructive file operation"),
        ("sudo", "Privilege escalation"),
        ("chmod 777", "Dangerous permission change"),
        ("chmod +x", "Permission modification"),
        ("curl | bash", "Remote code execution"),
        ("wget | sh", "Remote code execution"),
    ]
    
    BLOCKED_PATHS = [
        "/etc/",
        "/var/",
        "/usr/",
        "/root/",
        "/home/",
        "C:\\Windows",
        "C:\\Program Files",
    ]
    
    @classmethod
    def check(cls, action: str) -> tuple[bool, str]:
        """Check if an action is allowed. Returns (allowed, reason)."""
        action_lower = action.lower()
        
        # Check blocked operations
        for pattern, reason in cls.BLOCKED_OPERATIONS:
            if pattern.lower() in action_lower:
                return False, f"{reason} detected: {pattern}"
        
        # Check blocked paths
        for path in cls.BLOCKED_PATHS:
            if path.lower() in action_lower:
                return False, f"Access to protected path: {path}"
        
        return True, "Operation allowed"


class AgentOSKernel:
    """
    The Agent OS Kernel intercepts all agent operations.
    
    In production, this integrates with the full Agent OS runtime
    for process isolation, resource limits, and audit logging.
    """
    
    def __init__(self, agent_id: str = "crewai-agent"):
        self.agent_id = agent_id
        self.audit_log = []
        self.blocked_count = 0
        self.allowed_count = 0
        
        print_log("INFO", f"Kernel initialized for agent: {agent_id}")
        print_log("INFO", "Safety policies loaded: file_ops, commands, paths")
    
    def execute(self, action: str) -> bool:
        """
        Execute an action through the kernel.
        Returns True if allowed, False if blocked.
        """
        print_log("INFO", f"Agent requested: {action}")
        
        allowed, reason = SafetyPolicy.check(action)
        
        # Record in audit log
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "action": action,
            "allowed": allowed,
            "reason": reason,
        })
        
        if not allowed:
            self.blocked_count += 1
            print_log("BLOCK", f"DENIED: {reason}")
            print_blocked(action, reason[:45])
            return False
        
        self.allowed_count += 1
        print_allowed(action)
        return True
    
    def get_stats(self) -> dict:
        total = self.blocked_count + self.allowed_count
        return {
            "agent_id": self.agent_id,
            "total_requests": total,
            "allowed": self.allowed_count,
            "blocked": self.blocked_count,
            "violation_rate": f"{(self.blocked_count / total * 100):.1f}%" if total > 0 else "0%",
        }


# ============================================================================
# Simulated CrewAI Agents
# ============================================================================

class SimulatedAgent:
    """Simulates a CrewAI agent for the demo."""
    
    def __init__(self, role: str, goal: str, kernel: AgentOSKernel):
        self.role = role
        self.goal = goal
        self.kernel = kernel
        print_log("INFO", f"Created agent: {role} ({goal})")
    
    def execute_task(self, task: str, actions: list[str]) -> bool:
        """Execute a task with a list of actions."""
        print(f"\n{Colors.YELLOW}  🤖 Agent '{self.role}' executing: {task}{Colors.RESET}")
        
        success = True
        for action in actions:
            time.sleep(0.5)  # Dramatic pause
            if not self.kernel.execute(action):
                success = False
        
        return success


class SimulatedTask:
    """Simulates a CrewAI task."""
    
    def __init__(self, description: str, agent: SimulatedAgent, actions: list[str]):
        self.description = description
        self.agent = agent
        self.actions = actions
    
    def execute(self) -> bool:
        return self.agent.execute_task(self.description, self.actions)


# ============================================================================
# Demo Scenarios
# ============================================================================

def run_demo():
    print_banner()
    
    # Initialize kernel
    print_section("INITIALIZING AGENT OS KERNEL")
    kernel = AgentOSKernel(agent_id="demo-crew")
    
    # Create agents
    print_section("CREATING CREWAI AGENTS")
    
    cleanup_agent = SimulatedAgent(
        role="Cleanup Bot",
        goal="System Cleaner",
        kernel=kernel
    )
    
    analyst_agent = SimulatedAgent(
        role="Data Analyst",
        goal="Analytics",
        kernel=kernel
    )
    
    deploy_agent = SimulatedAgent(
        role="Deploy Bot",
        goal="DevOps",
        kernel=kernel
    )
    
    # Demo 1: Cleanup task (should be blocked)
    print_section("DEMO 1: CLEANUP TASK (Agent tries to delete files)")
    print(f"{Colors.MAGENTA}  Task: 'Clean up old files and free disk space'{Colors.RESET}\n")
    
    cleanup_task = SimulatedTask(
        description="Clean up old cache files",
        agent=cleanup_agent,
        actions=[
            "os.remove('/tmp/cache/*')",
            "shutil.rmtree('/var/log/old')",
            "rm -rf /home/user/Downloads/*",
        ]
    )
    cleanup_task.execute()
    
    # Demo 2: Analysis task (should be allowed)
    print_section("DEMO 2: ANALYSIS TASK (Safe read operations)")
    print(f"{Colors.MAGENTA}  Task: 'Analyze sales data'{Colors.RESET}\n")
    
    analysis_task = SimulatedTask(
        description="Analyze Q4 sales data",
        agent=analyst_agent,
        actions=[
            "read_file('data.csv')",
            "pandas.read_csv('report.csv')",
        ]
    )
    success = analysis_task.execute()
    if success:
        print(f"\n{Colors.GREEN}  ✅ Task completed successfully!{Colors.RESET}")
    
    # Demo 3: Deploy task (should be blocked)
    print_section("DEMO 3: DEPLOY TASK (Agent tries privilege escalation)")
    print(f"{Colors.MAGENTA}  Task: 'Deploy new version to production'{Colors.RESET}\n")
    
    deploy_task = SimulatedTask(
        description="Deploy app to production",
        agent=deploy_agent,
        actions=[
            "sudo systemctl restart app",
            "chmod 777 /var/www",
        ]
    )
    deploy_task.execute()
    
    # Print statistics
    print_section("KERNEL STATISTICS")
    stats = kernel.get_stats()
    
    print(f"""
{Colors.CYAN}  📊 Agent OS Kernel Report
  ─────────────────────────────────────────
  Agent ID:        {stats['agent_id']}
  Total Requests:  {stats['total_requests']}
  ✅ Allowed:      {stats['allowed']}
  🚫 Blocked:      {stats['blocked']}
  Violation Rate:  {stats['violation_rate']}
  ─────────────────────────────────────────{Colors.RESET}
""")
    
    print(f"""
{Colors.GREEN}{Colors.BOLD}
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║   ✅ DEMO COMPLETE - Your system stayed safe!            ║
  ║                                                           ║
  ║   Agent OS blocked {stats['blocked']} dangerous operations            ║
  ║   while allowing {stats['allowed']} safe ones.                        ║
  ║                                                           ║
  ║   This is kernel-level safety, not prompt engineering.   ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}""")
    
    print(f"\n{Colors.CYAN}  🔗 Learn more: https://github.com/imran-siddique/agent-os{Colors.RESET}\n")


if __name__ == "__main__":
    run_demo()
