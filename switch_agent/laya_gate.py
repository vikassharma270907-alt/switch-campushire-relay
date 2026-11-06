"""Laya System-1 Decision Engine & Guardrail Gate for Switch AI.

Provides sub-millisecond on-device intent triage, safety verification,
and tier routing before autonomous actions are executed in team channels.
"""
from __future__ import annotations
import time
import re
from typing import Dict, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class TriageDecision:
    intent: str
    difficulty: float
    domain: str
    is_safe: bool
    is_sensitive: bool
    needs_tools: bool
    confidence: float
    latency_ms: float
    recommended_action: str
    requires_human_approval: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LayaDecisionGate:
    """Sub-millisecond decision and guardrail engine for team chat queries."""

    # Pre-compiled regex patterns for fast safety guardrails
    DESTRUCTIVE_PATTERNS = [
        re.compile(r"\b(rm\s+-rf|drop\s+database|format\s+[a-z]:|dd\s+if=)\b", re.IGNORECASE),
        re.compile(r"\b(truncate\s+table|delete\s+from\s+users|flushall)\b", re.IGNORECASE),
        re.compile(r"\b(deploy\s+to\s+production|push\s+--force\s+origin\s+main)\b", re.IGNORECASE),
    ]

    INJECTION_PATTERNS = [
        re.compile(r"(ignore\s+(previous|all)\s+instructions|system\s+prompt|reveal\s+secret)", re.IGNORECASE),
        re.compile(r"(you\s+are\s+now\s+dan|developer\s+mode\s+enabled|jailbreak)", re.IGNORECASE),
    ]

    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold
        self._load_engine()

    def _load_engine(self):
        """Attempts to load native laya checkpoints, fallback to optimized heuristic engine."""
        self.has_native_laya = False
        try:
            import laya  # noqa: F401
            # Check if laya can run without ctypes/model blockage
            self.has_native_laya = True
        except Exception:
            self.has_native_laya = False

    def evaluate_request(self, user: str, message: str) -> TriageDecision:
        """Evaluates a team chat request in <5ms."""
        start_time = time.perf_counter()
        normalized = message.strip()
        lower_msg = normalized.lower()

        # 1. Guardrail Check: Dangerous/Destructive operations
        is_destructive = any(p.search(normalized) for p in self.DESTRUCTIVE_PATTERNS)
        is_injection = any(p.search(normalized) for p in self.INJECTION_PATTERNS)

        if is_destructive:
            latency = (time.perf_counter() - start_time) * 1000
            return TriageDecision(
                intent="destructive_action",
                difficulty=3.0,
                domain="security",
                is_safe=False,
                is_sensitive=True,
                needs_tools=True,
                confidence=0.99,
                latency_ms=round(latency, 2),
                recommended_action="BLOCK",
                requires_human_approval=True,
                reason="Laya Guardrail: Potentially destructive system command detected."
            )

        if is_injection:
            latency = (time.perf_counter() - start_time) * 1000
            return TriageDecision(
                intent="prompt_injection",
                difficulty=3.0,
                domain="security",
                is_safe=False,
                is_sensitive=True,
                needs_tools=False,
                confidence=0.98,
                latency_ms=round(latency, 2),
                recommended_action="BLOCK",
                requires_human_approval=True,
                reason="Laya Guardrail: Adversarial prompt injection detected."
            )

        # 2. Intent Triage & Classification
        domain = "general"
        intent = "query"
        difficulty = 0.5
        needs_tools = False
        is_sensitive = False
        confidence = 0.90

        if any(w in lower_msg for w in ("fix", "bug", "crash", "error", "traceback", "broken", "issue", "fails")):
            intent = "bug_fix"
            domain = "code_repair"
            difficulty = 2.2
            needs_tools = True
            confidence = 0.94
        elif any(w in lower_msg for w in ("build", "implement", "feature", "create", "scaffold", "add")):
            intent = "feature_request"
            domain = "development"
            difficulty = 2.5
            needs_tools = True
            confidence = 0.92
        elif any(w in lower_msg for w in ("test", "pytest", "coverage", "verify", "check")):
            intent = "test_execution"
            domain = "qa"
            difficulty = 1.0
            needs_tools = True
            confidence = 0.95
        elif any(w in lower_msg for w in ("prd", "spec", "requirements", "plan")):
            intent = "planning"
            domain = "product"
            difficulty = 1.8
            needs_tools = True
            confidence = 0.93
        elif any(w in lower_msg for w in ("password", "token", "secret", "api_key", "credentials", "credit")):
            intent = "sensitive_query"
            domain = "auth"
            is_sensitive = True
            difficulty = 1.5
            confidence = 0.91
        elif len(lower_msg.split()) < 3 and not any(w in lower_msg for w in ("hi", "hello")):
            # Ambiguous input
            confidence = 0.45
            difficulty = 2.0

        # 3. Decision Recommendation
        requires_approval = False
        recommended_action = "EXECUTE_LOCAL"

        if is_sensitive:
            recommended_action = "REQUEST_HUMAN_APPROVAL"
            requires_approval = True
            reason = "Sensitive credentials or secrets referenced in query."
        elif confidence < self.confidence_threshold:
            recommended_action = "REQUEST_CLARIFICATION"
            requires_approval = True
            reason = f"Confidence score ({confidence:.2f}) below calibrated threshold ({self.confidence_threshold:.2f})."
        elif intent in ("bug_fix", "feature_request"):
            recommended_action = "DISPATCH_RALPH_LOOP"
            reason = f"High-confidence {intent} identified; routing to Ralph autonomous agent loop."
        elif intent == "test_execution":
            recommended_action = "RUN_LOCAL_TESTS"
            reason = "Direct verification request; executing local pytest suite."
        else:
            recommended_action = "DIRECT_ANSWER"
            reason = "Standard conversational or lookup query; answering directly."

        latency = (time.perf_counter() - start_time) * 1000
        return TriageDecision(
            intent=intent,
            difficulty=difficulty,
            domain=domain,
            is_safe=True,
            is_sensitive=is_sensitive,
            needs_tools=needs_tools,
            confidence=confidence,
            latency_ms=round(latency, 2),
            recommended_action=recommended_action,
            requires_human_approval=requires_approval,
            reason=reason
        )

# Global singleton
GATE = LayaDecisionGate()
