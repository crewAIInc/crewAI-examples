"""AgentStamp trust check tool for CrewAI agents."""

import json
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


API_BASE_URL = "https://agentstamp.org/api/v1"
API_TIMEOUT_SECONDS = 10


class TrustCheckInput(BaseModel):
    """Input schema for the AgentStamp trust check tool."""

    wallet_address: str = Field(
        ...,
        description="The wallet address (0x... for EVM, base58 for Solana) of the agent to verify.",
    )


class AgentStampTrustCheckTool(BaseTool):
    """Check an AI agent's trust score and verification status via AgentStamp.

    AgentStamp provides cryptographic identity stamps, trust scoring (0-100),
    and reputation tracking for AI agents. This tool queries the public trust
    check API to verify an agent before collaboration.

    Free to use — no API key required.
    """

    name: str = "agentstamp_trust_check"
    description: str = (
        "Verify an AI agent's trustworthiness using AgentStamp. "
        "Returns trust score (0-100), stamp tier (free/bronze/silver/gold), "
        "endorsement count, and heartbeat status. "
        "Input: wallet address of the agent to check."
    )
    args_schema: Type[BaseModel] = TrustCheckInput

    def _run(self, wallet_address: str) -> str:
        """Execute trust check against AgentStamp API."""
        url = f"{API_BASE_URL}/trust/check/{wallet_address}"

        try:
            response = requests.get(url, timeout=API_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()

            return json.dumps(
                {
                    "trusted": data.get("trusted", False),
                    "score": data.get("score", 0),
                    "tier": data.get("tier", "none"),
                    "agent_name": data.get("agent", {}).get("name", "Unknown"),
                    "endorsements": data.get("agent", {}).get("endorsements", 0),
                    "heartbeat_active": data.get("agent", {}).get(
                        "heartbeat_active", False
                    ),
                    "wallet_address": wallet_address,
                    "stamp_chain": data.get("agent", {}).get("stamp_chain", "unknown"),
                    "created_at": data.get("agent", {}).get("created_at", "unknown"),
                },
                indent=2,
            )

        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return json.dumps(
                    {
                        "trusted": False,
                        "score": 0,
                        "tier": "none",
                        "agent_name": "Not Registered",
                        "endorsements": 0,
                        "heartbeat_active": False,
                        "wallet_address": wallet_address,
                        "error": "Agent not found in AgentStamp registry",
                    },
                    indent=2,
                )
            return json.dumps(
                {
                    "error": f"AgentStamp API error: {exc}",
                    "wallet_address": wallet_address,
                },
                indent=2,
            )
        except requests.exceptions.RequestException as exc:
            return json.dumps(
                {
                    "error": f"Network error: {exc}",
                    "wallet_address": wallet_address,
                },
                indent=2,
            )
