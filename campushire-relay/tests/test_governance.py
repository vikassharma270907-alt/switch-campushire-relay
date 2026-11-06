"""Unit tests for ArmorAntigravity & ArmorIQ Intent Governance."""

import pytest
from campushire.governance import (
    ArmorGovernanceEngine,
    IntentDeclaration,
    MerkleAuditLedger,
)


def test_merkle_ledger_empty():
    ledger = MerkleAuditLedger()
    root = ledger.compute_merkle_root()
    assert len(root) == 64  # SHA-256 hex digest length


def test_merkle_ledger_deterministic_root():
    ledger1 = MerkleAuditLedger()
    ledger2 = MerkleAuditLedger()

    fixed_time = 1700000000.0
    h1 = ledger1.append_event("TEST_EVENT", {"data": "sample"}, timestamp=fixed_time)
    h2 = ledger2.append_event("TEST_EVENT", {"data": "sample"}, timestamp=fixed_time)
    assert h1 == h2


def test_merkle_ledger_multi_leaf_root():
    ledger = MerkleAuditLedger()
    for i in range(5):
        ledger.append_event(f"EVENT_{i}", {"seq": i})
    root = ledger.compute_merkle_root()
    assert len(root) == 64
    assert len(ledger.leaves) == 5


def test_governance_allow_valid_waiver():
    engine = ArmorGovernanceEngine()
    intent = IntentDeclaration(
        intent_id="INT-001",
        action="approve_borderline_waiver",
        target="candidate:23CS04",
        parameters={"cgpa": 7.96, "cutoff": 8.00, "active_backlogs": 0},
    )
    token = engine.generate_intent_token(intent)
    decision = engine.verify_and_authorize(intent, token)

    assert decision.decision == "ALLOW"
    assert decision.policy_id == "POL-ALLOW-STANDARD"
    assert len(engine.ledger.leaves) == 1


def test_governance_block_excessive_delta():
    engine = ArmorGovernanceEngine()
    intent = IntentDeclaration(
        intent_id="INT-002",
        action="approve_borderline_waiver",
        target="candidate:23CS08",
        parameters={"cgpa": 7.85, "cutoff": 8.00, "active_backlogs": 0},  # Delta = 0.15 > 0.10
    )
    token = engine.generate_intent_token(intent)
    decision = engine.verify_and_authorize(intent, token)

    assert decision.decision == "BLOCK"
    assert decision.policy_id == "POL-CGPA-02"
    assert "exceeds max policy threshold" in decision.reason


def test_governance_block_active_backlogs():
    engine = ArmorGovernanceEngine()
    intent = IntentDeclaration(
        intent_id="INT-003",
        action="approve_borderline_waiver",
        target="candidate:23CS09",
        parameters={"cgpa": 7.98, "cutoff": 8.00, "active_backlogs": 1},  # Has 1 backlog
    )
    token = engine.generate_intent_token(intent)
    decision = engine.verify_and_authorize(intent, token)

    assert decision.decision == "BLOCK"
    assert decision.policy_id == "POL-BL-01"
    assert "strictly disallows waivers with backlogs" in decision.reason
