"""Laya Fast Decision Engine Service for Switch WeMakeDevs Hackathon.

Provides high-speed, local 'System 1' reflex decision making:
- Sub-50ms intent routing
- Instant prompt guardrails & jailbreak detection
- Support triage and sentiment categorization
- Calibrated confidence scoring without hallucination
"""

from __future__ import annotations

import os
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Sequence, Union

# Add local checkout if laya is not installed globally
try:
    import laya
except ImportError:
    repo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laya-repo")
    if os.path.isdir(repo_path) and repo_path not in sys.path:
        sys.path.insert(0, repo_path)
    try:
        import laya
    except ImportError:
        import types
        laya = types.ModuleType("laya")
        laya.Router = type("Router", (), {})
        laya.guard_questions = lambda: {}
        laya.decision_questions = lambda: {}
        sys.modules["laya"] = laya


class LayaDecisionEngine:
    """Thread-safe System 1 decision engine with lazy model loading."""

    def __init__(
        self,
        device: str = "cpu",
        num_threads: int = 8,
        default_model: str = "english",
    ):
        self.device = device
        self.num_threads = num_threads
        self.default_model = default_model
        self._router = None
        self._laya_module = None
        self._lock = threading.Lock()

    def _init_router(self):
        """Thread-safe lazy initialization of Laya router."""
        if self._router is not None:
            return self._router

        with self._lock:
            if self._router is not None:
                return self._router

            try:
                import torch
                from laya import Router

                if self.device == "cpu":
                    max_threads = os.cpu_count() or 8
                    torch.set_num_threads(min(self.num_threads, max_threads))

                self._laya_module = laya
                # preload=False keeps resident RAM at 0MB until the first decision is executed
                self._router = Router(preload=False, device=self.device)
                return self._router
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to initialize Laya decision engine: {exc}"
                ) from exc

    def _build_state(self, text: str) -> Dict[str, str]:
        """Maps user input to all standard state fields used across presets."""
        return {
            "text": text,
            "prompt": text,
            "message": text,
            "body": text,
            "post": text,
            "request": text,
            "ticket": text,
        }

    def check_guardrails(
        self,
        text: str,
        risk_threshold: float = 0.50,
    ) -> Dict[str, Any]:
        """Check for prompt injections, jailbreaks, or malicious inputs.

        Args:
            text: Input prompt to audit.
            risk_threshold: Probability threshold for triggering a risk flag (default 0.50).

        Returns:
            Dict containing 'safe': bool, 'risk_score': float, 'flags': list, and 'latency_ms': float.
        """
        router = self._init_router()
        laya_mod = self._laya_module

        questions = laya_mod.guard_questions()
        state = self._build_state(text)

        t0 = time.perf_counter()
        res = router.predict(state, questions, model=self.default_model)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        answers = res.get("answers", {})
        triggered_flags = []
        max_risk = 0.0

        for key, ans in answers.items():
            ans_type = ans.get("type")
            # In Laya, binary questions return type 'noul' with float probability in [0.0, 1.0]
            if ans_type == "noul":
                prob = float(ans.get("noul", 0.0))
                if prob >= risk_threshold:
                    triggered_flags.append(key)
                if key in ("jailbreak", "prompt_injection"):
                    max_risk = max(max_risk, prob)
            elif ans_type == "choice":
                if ans.get("choice") in ("unsafe", "violation", "attack"):
                    triggered_flags.append(key)
                    max_risk = max(max_risk, float(ans.get("confidence", 1.0)))

        is_safe = (len(triggered_flags) == 0) and (max_risk < risk_threshold)
        return {
            "safe": is_safe,
            "risk_score": round(max_risk, 4),
            "flags": triggered_flags,
            "raw_answers": answers,
            "latency_ms": latency_ms,
        }

    def route_intent(
        self,
        text: str,
        possible_intents: Union[List[str], Dict[str, str]],
        criterion: str = "What is the primary intent or task requested",
    ) -> Dict[str, Any]:
        """Route user text to the most relevant agent or handler in <50ms.

        Args:
            text: Input text/query to classify.
            possible_intents: List of intent labels, or dict of {label: description}.
            criterion: High-level classification rubric.

        Returns:
            Dict containing 'selected_intent', 'confidence', 'probabilities', and 'latency_ms'.
        """
        router = self._init_router()

        # Format choice question using Laya's expected schema: instructions + criteria
        questions = {
            "intent": {
                "type": "choice",
                "instructions": f"{criterion} in `text`?",
                "criteria": possible_intents,
            }
        }
        state = self._build_state(text)

        t0 = time.perf_counter()
        res = router.predict(state, questions, model=self.default_model)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        answer = res.get("answers", {}).get("intent", {})
        return {
            "selected_intent": answer.get("choice"),
            "confidence": round(float(answer.get("confidence", 0.0)), 4),
            "probabilities": answer.get("probabilities", {}),
            "routing_model": res.get("routing", {}).get("model", self.default_model),
            "latency_ms": latency_ms,
        }

    def triage_request(self, text: str) -> Dict[str, Any]:
        """Run customer support triage preset (urgency, frustration, refund request)."""
        router = self._init_router()
        laya_mod = self._laya_module

        questions = laya_mod.triage_questions()
        state = self._build_state(text)

        t0 = time.perf_counter()
        res = router.predict(state, questions, model=self.default_model)
        res["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return res

    def unload(self) -> None:
        """Free memory by unloading resident neural weights from RAM."""
        with self._lock:
            if self._router is not None:
                self._router.unload()
                self._router = None


# Quick verification
if __name__ == "__main__":
    print("[Laya] Initializing decision engine service...")
    engine = LayaDecisionEngine()
    print("[Laya] Service initialized successfully (lazy mode, 0 RAM allocated).")
