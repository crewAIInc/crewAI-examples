"""
Audit trail for CrewAI — logs every tool call with agent identity.

Each entry records: who (agent_id), what (tool + args), when (timestamp),
and the verification status at time of call.

Usage:
    from audit_trail import AuditTrail

    audit = AuditTrail()
    audit.log_tool_call(agent_id, tool_name, args, result)
    audit.log_verification(agent_id, verified, trust_score)

    # Export
    audit.export_json("audit_log.json")
    audit.print_summary()
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path


class AuditTrail:
    """Append-only audit log for agent actions."""

    def __init__(self, log_dir: str = None):
        self._log_dir = Path(log_dir or Path(__file__).parent / "audit_logs")
        self._log_dir.mkdir(exist_ok=True)
        self._entries: list[dict] = []
        self._session_id = f"session_{int(time.time())}"

    def log_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        args: dict = None,
        result: str = None,
    ):
        """Log a tool invocation by an agent."""
        entry = {
            "type": "tool_call",
            "session": self._session_id,
            "agent_id": agent_id,
            "tool": tool_name,
            "args": args or {},
            "result_preview": (result or "")[:200],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._entries.append(entry)
        self._append_to_file(entry)

    def log_verification(
        self,
        agent_id: str,
        verified: bool,
        trust_score: float = None,
        method: str = "agentid",
    ):
        """Log an identity verification check."""
        entry = {
            "type": "verification",
            "session": self._session_id,
            "agent_id": agent_id,
            "verified": verified,
            "trust_score": trust_score,
            "method": method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._entries.append(entry)
        self._append_to_file(entry)

    def log_gate_result(
        self,
        gate: str,
        passed: bool,
        details: dict = None,
    ):
        """Log a security gate pass/fail."""
        entry = {
            "type": "gate",
            "session": self._session_id,
            "gate": gate,
            "passed": passed,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._entries.append(entry)
        self._append_to_file(entry)

    def _append_to_file(self, entry: dict):
        """Append entry to today's log file."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self._log_dir / f"audit_{today}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def export_json(self, filename: str = None) -> str:
        """Export all entries as JSON."""
        path = filename or str(self._log_dir / f"audit_{self._session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, indent=2, default=str)
        return path

    def print_summary(self):
        """Print a summary of the audit trail."""
        tool_calls = [e for e in self._entries if e["type"] == "tool_call"]
        verifications = [e for e in self._entries if e["type"] == "verification"]
        gates = [e for e in self._entries if e["type"] == "gate"]

        print(f"Audit Trail — Session {self._session_id}")
        print(f"  Tool calls:     {len(tool_calls)}")
        print(f"  Verifications:  {len(verifications)}")
        print(f"  Gate checks:    {len(gates)}")
        print(f"  Gates passed:   {sum(1 for g in gates if g['passed'])}")
        print(f"  Gates failed:   {sum(1 for g in gates if not g['passed'])}")

        agents = set(e.get("agent_id", "") for e in self._entries if e.get("agent_id"))
        print(f"  Unique agents:  {len(agents)}")
        for aid in sorted(agents):
            calls = sum(1 for e in tool_calls if e["agent_id"] == aid)
            print(f"    {aid}: {calls} tool calls")
