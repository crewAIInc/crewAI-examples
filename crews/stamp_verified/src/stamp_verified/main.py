#!/usr/bin/env python
"""Entry point for the stamp_verified crew."""

import sys

from stamp_verified.crew import StampVerifiedCrew


def run():
    """Run the trust-verified agent crew."""
    inputs = {
        "wallet_address": "0xYOUR_AGENT_WALLET_ADDRESS",
        "min_score": 50,
        "task_description": (
            "Analyze market trends for AI agent infrastructure and produce "
            "a summary report. This task requires a trusted agent with a "
            "minimum trust score of 50."
        ),
    }
    StampVerifiedCrew().crew().kickoff(inputs=inputs)


def train():
    """Train the crew for a given number of iterations."""
    inputs = {
        "wallet_address": "0xYOUR_AGENT_WALLET_ADDRESS",
        "min_score": 50,
        "task_description": "Analyze market trends for AI agent infrastructure.",
    }
    try:
        StampVerifiedCrew().crew().train(
            n_iterations=int(sys.argv[1]), inputs=inputs
        )
    except Exception as exc:
        raise Exception(f"An error occurred while training the crew: {exc}") from exc
