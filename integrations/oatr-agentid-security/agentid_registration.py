"""
AgentID registration flow for CrewAI agents.

On first run, each agent registers with AgentID and receives an ECDSA P-256
certificate. The certificate is cached locally so subsequent runs skip
registration.

Usage:
    from agentid_registration import ensure_registered, get_agent_id

    # Register agent before crew runs
    agent_id = ensure_registered("ResearchBot", ["web-search", "summarization"])

    # Verify another agent
    from agentid_registration import verify_agent
    result = verify_agent(agent_id)
"""

import json
import os
import hashlib
from pathlib import Path

import httpx

AGENTID_API = os.getenv("AGENTID_API_URL", "https://www.getagentid.dev/api/v1")
AGENTID_KEY = os.getenv("AGENTID_API_KEY", "")
CACHE_FILE = Path(__file__).parent / ".agentid_cache.json"
_TIMEOUT = 15


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def _save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def ensure_registered(
    name: str,
    capabilities: list[str] = None,
    description: str = "",
    platform: str = "crewai",
) -> str:
    """Register agent with AgentID if not already cached. Returns agent_id."""
    cache = _load_cache()
    cache_key = hashlib.sha256(name.encode()).hexdigest()[:16]

    if cache_key in cache:
        return cache[cache_key]["agent_id"]

    if not AGENTID_KEY:
        raise ValueError(
            "AGENTID_API_KEY not set. Get one at https://getagentid.dev/dashboard/keys"
        )

    resp = httpx.post(
        f"{AGENTID_API}/agents/register",
        headers={
            "Authorization": f"Bearer {AGENTID_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "name": name,
            "description": description,
            "capabilities": capabilities or [],
            "platform": platform,
        },
        timeout=_TIMEOUT,
        follow_redirects=True,
    )

    if resp.status_code >= 400:
        raise RuntimeError(f"AgentID registration failed: {resp.text}")

    data = resp.json()
    cache[cache_key] = {
        "agent_id": data["agent_id"],
        "name": name,
        "certificate": data.get("certificate", ""),
    }
    _save_cache(cache)
    return data["agent_id"]


def get_agent_id(name: str) -> str | None:
    """Get cached agent_id by name. Returns None if not registered."""
    cache = _load_cache()
    cache_key = hashlib.sha256(name.encode()).hexdigest()[:16]
    entry = cache.get(cache_key)
    return entry["agent_id"] if entry else None


def verify_agent(agent_id: str) -> dict:
    """Verify an agent's identity via AgentID. No API key needed."""
    resp = httpx.post(
        f"{AGENTID_API}/agents/verify",
        headers={"Content-Type": "application/json"},
        json={"agent_id": agent_id},
        timeout=_TIMEOUT,
        follow_redirects=True,
    )
    return resp.json()
