"""
Tests for the three-layer security gate.

Run with: python -m pytest test_security_gate.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from security_gate import (
    verify_runtime_attestation,
    security_gate,
    load_manifest,
    _manifest_cache,
    CACHE_TTL,
)


# ── Test manifest for OATR verification ──

MOCK_MANIFEST = {
    "version": "1.0",
    "generated_at": "2026-03-24T00:00:00Z",
    "expires_at": "2026-03-25T00:00:00Z",
    "total_issuers": 1,
    "issuers": {
        "test-runtime": {
            "issuer_id": "test-runtime",
            "display_name": "Test Runtime",
            "website": "https://test-runtime.example.com",
            "status": "active",
            "public_keys": [
                {
                    "kid": "test-runtime-2026-03",
                    "algorithm": "Ed25519",
                    "public_key": "dLkXRmTqvXiVGOb57JZ-5cdH0GXH_lWVB-5pKY3Cee4",
                    "status": "active",
                }
            ],
        },
        "revoked-runtime": {
            "issuer_id": "revoked-runtime",
            "display_name": "Revoked Runtime",
            "website": "https://revoked.example.com",
            "status": "suspended",
            "public_keys": [
                {
                    "kid": "revoked-runtime-2026-03",
                    "algorithm": "Ed25519",
                    "public_key": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "status": "active",
                }
            ],
        },
    },
}


class TestVerifyRuntimeAttestation:
    """Tests for Layer 1: OATR runtime verification."""

    @patch("security_gate.load_manifest", return_value=MOCK_MANIFEST)
    def test_unknown_issuer_rejected(self, mock_manifest):
        """JWT from an unregistered issuer is rejected."""
        from jose import jwt as jose_jwt

        # Create a JWT with an issuer not in the manifest
        token = jose_jwt.encode(
            {"sub": "agent-1", "aud": "https://crew.com", "iss": "unknown-runtime"},
            "fake-key",
            algorithm="HS256",
            headers={"iss": "unknown-runtime", "kid": "unknown-2026-03", "alg": "EdDSA"},
        )
        result = verify_runtime_attestation(token, "https://crew.com")
        assert result["valid"] is False
        assert result["reason"] == "unknown_issuer"

    @patch("security_gate.load_manifest", return_value=MOCK_MANIFEST)
    def test_revoked_issuer_rejected(self, mock_manifest):
        """JWT from a revoked/suspended issuer is rejected."""
        from jose import jwt as jose_jwt

        token = jose_jwt.encode(
            {"sub": "agent-1", "aud": "https://crew.com", "iss": "revoked-runtime"},
            "fake-key",
            algorithm="HS256",
            headers={"iss": "revoked-runtime", "kid": "revoked-runtime-2026-03", "alg": "EdDSA"},
        )
        result = verify_runtime_attestation(token, "https://crew.com")
        assert result["valid"] is False
        assert result["reason"] == "revoked_issuer"

    @patch("security_gate.load_manifest", return_value=MOCK_MANIFEST)
    def test_unknown_key_rejected(self, mock_manifest):
        """JWT with valid issuer but wrong kid is rejected."""
        from jose import jwt as jose_jwt

        token = jose_jwt.encode(
            {"sub": "agent-1", "aud": "https://crew.com", "iss": "test-runtime"},
            "fake-key",
            algorithm="HS256",
            headers={"iss": "test-runtime", "kid": "wrong-kid-2026-99", "alg": "EdDSA"},
        )
        result = verify_runtime_attestation(token, "https://crew.com")
        assert result["valid"] is False
        assert result["reason"] == "unknown_key"

    @patch("security_gate.load_manifest", return_value=MOCK_MANIFEST)
    def test_missing_header_fields_rejected(self, mock_manifest):
        """JWT missing required header fields is rejected."""
        from jose import jwt as jose_jwt

        # No iss in header
        token = jose_jwt.encode(
            {"sub": "agent-1"},
            "fake-key",
            algorithm="HS256",
            headers={"kid": "test-runtime-2026-03", "alg": "EdDSA"},
        )
        result = verify_runtime_attestation(token, "https://crew.com")
        assert result["valid"] is False
        assert result["reason"] == "invalid_signature"


class TestSecurityGate:
    """Tests for Layer 3: Combined security gate."""

    def test_passes_with_no_credentials(self):
        """Gate passes when no attestation or agent_id is provided."""
        result = security_gate({"topic": "test topic"})
        assert result["topic"] == "test topic"

    @patch("security_gate.verify_runtime_attestation")
    def test_blocks_invalid_runtime(self, mock_verify):
        """Gate raises PermissionError for invalid runtime."""
        mock_verify.return_value = {"valid": False, "reason": "unknown_issuer"}
        with pytest.raises(PermissionError, match="unknown_issuer"):
            security_gate({
                "runtime_attestation": "fake.jwt.token",
                "audience": "https://crew.com",
            })

    @patch("security_gate.verify_runtime_attestation")
    def test_passes_valid_runtime(self, mock_verify):
        """Gate passes for valid runtime attestation."""
        mock_verify.return_value = {"valid": True, "claims": {}, "issuer": {}}
        result = security_gate({
            "topic": "test",
            "runtime_attestation": "valid.jwt.token",
            "audience": "https://crew.com",
        })
        assert result["topic"] == "test"

    def test_preserves_all_inputs(self):
        """Gate returns all input keys unchanged."""
        inputs = {"topic": "test", "extra_key": "extra_value", "number": 42}
        result = security_gate(inputs)
        assert result == inputs
