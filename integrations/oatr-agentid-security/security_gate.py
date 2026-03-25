"""
Three-layer security gate for CrewAI.

Layer 1: OATR (Open Agent Trust Registry) - runtime attestation
Layer 2: AgentID - per-agent identity verification
Layer 3: Combined pre-kickoff callback for CrewAI

Usage:
    from security_gate import security_gate

    crew = Crew(
        agents=[...],
        tasks=[...],
        before_kickoff_callbacks=[security_gate],
    )
"""

import time
import httpx
from jose import jwt, JWTError


# ── Layer 1: OATR - verify the runtime is registered and non-revoked ──

MANIFEST_URL = "https://raw.githubusercontent.com/FransDevelopment/open-agent-trust-registry/main/registry/manifest.json"
_manifest_cache = {"data": None, "fetched_at": 0}
CACHE_TTL = 15 * 60  # 15 minutes, matches SDK's CACHE_TTL_MS


def load_manifest():
    """Fetch and cache the signed registry manifest."""
    if time.time() - _manifest_cache["fetched_at"] < CACHE_TTL and _manifest_cache["data"]:
        return _manifest_cache["data"]
    resp = httpx.get(MANIFEST_URL)
    resp.raise_for_status()
    _manifest_cache["data"] = resp.json()
    _manifest_cache["fetched_at"] = time.time()
    return _manifest_cache["data"]


def verify_runtime_attestation(attestation_jwt: str, expected_audience: str) -> dict:
    """
    Verify a runtime attestation JWT against the OATR manifest.
    Mirrors the verification logic in the TypeScript SDK (verify.ts).
    Returns {"valid": True/False, "reason": ...}
    """
    manifest = load_manifest()

    header = jwt.get_unverified_header(attestation_jwt)

    issuer_id = header.get("iss")
    kid = header.get("kid")

    if not issuer_id or not kid or header.get("alg") != "EdDSA":
        return {"valid": False, "reason": "invalid_signature"}

    # Look up issuer in manifest
    issuer = manifest.get("issuers", {}).get(issuer_id)
    if not issuer:
        return {"valid": False, "reason": "unknown_issuer"}

    # Check issuer status
    if issuer.get("status") != "active":
        return {"valid": False, "reason": "revoked_issuer"}

    # Find the key by kid
    active_keys = [
        k for k in issuer.get("public_keys", [])
        if k["kid"] == kid and k["status"] == "active"
    ]
    if not active_keys:
        return {"valid": False, "reason": "unknown_key"}

    key = active_keys[0]

    # Verify signature (Ed25519)
    try:
        verified_claims = jwt.decode(
            attestation_jwt,
            {"kty": "OKP", "crv": "Ed25519", "x": key["public_key"]},
            algorithms=["EdDSA"],
            audience=expected_audience,
        )
    except jwt.ExpiredSignatureError:
        return {"valid": False, "reason": "expired_attestation"}
    except jwt.JWTClaimsError:
        return {"valid": False, "reason": "audience_mismatch"}
    except JWTError:
        return {"valid": False, "reason": "invalid_signature"}

    return {"valid": True, "claims": verified_claims, "issuer": issuer}


# ── Layer 2: AgentID - verify the specific agent's identity ──

try:
    from agentid_crewai import AgentIDVerifyTool
    _verify_tool = AgentIDVerifyTool()
    AGENTID_AVAILABLE = True
except ImportError:
    _verify_tool = None
    AGENTID_AVAILABLE = False


# ── Layer 3: Combined pre-kickoff security gate ──

def security_gate(inputs: dict) -> dict:
    """
    Run before crew kickoff via CrewAI's before_kickoff_callbacks.
    Verifies runtime attestation (OATR) and agent identity (AgentID).

    Expected input keys:
        runtime_attestation: JWT string from the agent's runtime
        agent_id: AgentID identifier for per-agent verification
        audience: expected audience for the attestation (defaults to "https://your-crew.com")

    Both keys are optional. If neither is provided, the gate passes.
    """
    attestation = inputs.get("runtime_attestation")
    agent_id = inputs.get("agent_id")
    audience = inputs.get("audience", "https://your-crew.com")

    # OATR: is the runtime registered?
    if attestation:
        result = verify_runtime_attestation(attestation, audience=audience)
        if not result["valid"]:
            raise PermissionError(f"Runtime verification failed: {result['reason']}")

    # AgentID: is this specific agent who it claims?
    if agent_id and AGENTID_AVAILABLE:
        verification = _verify_tool.run(agent_id=agent_id)
        if not verification.get("verified"):
            raise PermissionError("Agent identity verification failed")

    return inputs
