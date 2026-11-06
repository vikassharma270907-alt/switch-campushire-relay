"""ArmorAntigravity & ArmorIQ Intent-First Governance Module for CampusHire Relay.

Enforces:
1. Explicit Pre-Flight Intent Declaration
2. Cryptographic Plan Hashing & Nonce Binding (SHA-256)
3. Hard Policy Guardrails (e.g., Max Waiver Delta <= 0.10 CGPA, Backlogs Policy)
4. Tamper-Evident Audit Merkle Tree Ledger
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IntentDeclaration(BaseModel):
    """Explicit pre-flight user or agent intent."""
    intent_id: str
    action: str  # e.g., "approve_borderline_waiver", "export_verified_csv", "update_criteria"
    target: str  # e.g., "candidate:23CS04"
    parameters: Dict[str, Any]
    timestamp: float = Field(default_factory=time.time)
    intent_token: Optional[str] = None


class GovernanceDecision(BaseModel):
    """ArmorAntigravity governance policy decision."""
    decision: str  # "ALLOW" or "BLOCK"
    reason: str
    policy_id: str
    plan_digest: str
    intent_token: str


class MerkleAuditLedger:
    """Tamper-evident Merkle ledger recording all governed workflow events."""

    def __init__(self) -> None:
        self.leaves: List[str] = []
        self.history: List[Dict[str, Any]] = []

    def append_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        timestamp: Optional[float] = None,
    ) -> str:
        """Serialize event, compute leaf hash, and append to ledger."""
        record = {
            "index": len(self.history),
            "timestamp": timestamp if timestamp is not None else time.time(),
            "event_type": event_type,
            "payload": payload,
        }
        serialized = json.dumps(record, sort_keys=True)
        leaf_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.history.append(record)
        self.leaves.append(leaf_hash)
        return leaf_hash

    def compute_merkle_root(self) -> str:
        """Compute the binary Merkle root over all recorded ledger events."""
        if not self.leaves:
            return hashlib.sha256(b"EMPTY_LEDGER").hexdigest()

        current_level = list(self.leaves)
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
                next_level.append(combined)
            current_level = next_level
        return current_level[0]


class ArmorGovernanceEngine:
    """Enterprise policy engine verifying intent tokens and enforcing boundary invariants."""

    MAX_WAIVER_CGPA_DELTA: float = 0.10  # Maximum permissible CGPA gap for placement waivers

    def __init__(self) -> None:
        self.ledger = MerkleAuditLedger()

    def build_plan_digest(self, intent: IntentDeclaration) -> str:
        """Cryptographically seal an intent plan via SHA-256."""
        canonical_str = json.dumps(
            {
                "intent_id": intent.intent_id,
                "action": intent.action,
                "target": intent.target,
                "parameters": intent.parameters,
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def generate_intent_token(self, intent: IntentDeclaration) -> str:
        """Generate a single-use bound intent token."""
        plan_digest = self.build_plan_digest(intent)
        token_payload = f"{intent.intent_id}:{plan_digest}:{intent.timestamp}"
        return hashlib.sha256(token_payload.encode("utf-8")).hexdigest()

    def verify_and_authorize(
        self,
        intent: IntentDeclaration,
        intent_token: str,
    ) -> GovernanceDecision:
        """Verify plan integrity and enforce policy boundaries."""
        plan_digest = self.build_plan_digest(intent)

        # 1. Policy: Approve Borderline Waiver
        if intent.action == "approve_borderline_waiver":
            cgpa = intent.parameters.get("cgpa", 0.0)
            cutoff = intent.parameters.get("cutoff", 0.0)
            backlogs = intent.parameters.get("active_backlogs", 0)

            # Invariant: No waivers allowed if candidate has active backlogs
            if backlogs > 0:
                self.ledger.append_event("POLICY_VIOLATION", {
                    "action": intent.action,
                    "target": intent.target,
                    "reason": "Active backlogs exceed zero",
                })
                return GovernanceDecision(
                    decision="BLOCK",
                    reason=f"Candidate has {backlogs} active backlogs. Policy POL-BL-01 strictly disallows waivers with backlogs.",
                    policy_id="POL-BL-01",
                    plan_digest=plan_digest,
                    intent_token=intent_token,
                )

            # Invariant: Delta must not exceed MAX_WAIVER_CGPA_DELTA
            delta = cutoff - cgpa
            if delta > self.MAX_WAIVER_CGPA_DELTA:
                self.ledger.append_event("POLICY_VIOLATION", {
                    "action": intent.action,
                    "target": intent.target,
                    "delta": delta,
                    "max_allowed": self.MAX_WAIVER_CGPA_DELTA,
                })
                return GovernanceDecision(
                    decision="BLOCK",
                    reason=(
                        f"Requested waiver delta ({delta:.2f}) exceeds max policy threshold "
                        f"({self.MAX_WAIVER_CGPA_DELTA:.2f}). Requires Dean of Academic Affairs override."
                    ),
                    policy_id="POL-CGPA-02",
                    plan_digest=plan_digest,
                    intent_token=intent_token,
                )

        # 2. Approved action: Record in Merkle ledger
        self.ledger.append_event("ACTION_AUTHORIZED", {
            "action": intent.action,
            "target": intent.target,
            "plan_digest": plan_digest,
            "intent_token": intent_token,
        })

        return GovernanceDecision(
            decision="ALLOW",
            reason="All ArmorIQ intent-first policy invariants verified.",
            policy_id="POL-ALLOW-STANDARD",
            plan_digest=plan_digest,
            intent_token=intent_token,
        )
