#!/usr/bin/env python3
"""
Laya Fast Decision CLI Gate for Switch AI Rooms.
Exposes sub-50ms System 1 reflex routing, guardrails, and STAR mock interview scoring.
"""
import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from laya_service import LayaDecisionEngine


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/laya_gate.py audit-notice <notice_file_or_text>")
        print("  python scripts/laya_gate.py route-message <chat_message>")
        print("  python scripts/laya_gate.py evaluate-star <spoken_answer_text>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    engine = LayaDecisionEngine()

    if cmd == "audit-notice":
        if len(sys.argv) < 3:
            print("Error: notice file or text required", file=sys.stderr)
            sys.exit(1)
        target = sys.argv[2]
        if Path(target).exists():
            text = Path(target).read_text(encoding="utf-8")
        else:
            text = target

        result = engine.check_guardrails(text)
        print(json.dumps(result, indent=2))
        if not result["safe"]:
            print(f"[SECURITY ALERT] Unsafe input blocked! Risk: {result['risk_score']}, Flags: {result['flags']}", file=sys.stderr)
            sys.exit(2)

    elif cmd == "route-message":
        if len(sys.argv) < 3:
            print("Error: message text required", file=sys.stderr)
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        result = engine.route_intent(text)
        print(json.dumps(result, indent=2))

    elif cmd == "evaluate-star":
        if len(sys.argv) < 3:
            print("Error: student response transcript required", file=sys.stderr)
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        result = engine.evaluate_star_response(text)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
