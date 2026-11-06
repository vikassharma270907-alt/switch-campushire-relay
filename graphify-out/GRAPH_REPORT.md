# Graph Report - switch wemakedev hackathon  (2026-11-06)

## Corpus Check
- 17 files · ~8,042 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 1, .ini 1, .cmd 1)

## Summary
- 223 nodes · 292 edges · 14 communities (8 shown, 6 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 28 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d236578d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- LayaDecisionEngine
- server.py
- reviews
- ralph_runner.py
- knowledge_base
- test_switch_agent.py
- pre_merge_checks
- SwitchGuard: On-Device Triage & Autonomous Collaborative Agent
- Ralph Agent Instructions
- Ralph Agent Instructions
- ralph.sh script

## God Nodes (most connected - your core abstractions)
1. `LayaDecisionEngine` - 15 edges
2. `TestLayaDecisionEngine` - 15 edges
3. `reviews` - 13 edges
4. `LayaDecisionGate` - 11 edges
5. `🧪 Verified Test Suite` - 9 edges
6. `Ralph Agent Instructions` - 9 edges
7. `Ralph Agent Instructions` - 9 edges
8. `knowledge_base` - 8 edges
9. `RalphCollaborativeRunner` - 8 edges
10. `pre_merge_checks` - 6 edges

## Surprising Connections (you probably didn't know these)
- `🧪 Verified Test Suite` --references--> `test_switch_agent_protocol_handshake()`  [INFERRED]
  README.md → tests/test_switch_agent.py
- `🧪 Verified Test Suite` --references--> `test_api_triage_endpoint()`  [INFERRED]
  README.md → tests/test_switch_agent.py
- `🧪 Verified Test Suite` --references--> `test_laya_gate_submillisecond_latency()`  [INFERRED]
  README.md → tests/test_switch_agent.py
- `🧪 Verified Test Suite` --references--> `test_laya_gate_destructive_command_blocking()`  [INFERRED]
  README.md → tests/test_switch_agent.py
- `🧪 Verified Test Suite` --references--> `test_laya_gate_prompt_injection_blocking()`  [INFERRED]
  README.md → tests/test_switch_agent.py

## Import Cycles
- None detected.

## Communities (14 total, 6 thin omitted)

### Community 1 - "server.py"
Cohesion: 0.08
Nodes (9): RalphCollaborativeRunner, RalphIterationEvent, api_ralph_execute(), api_test_run(), api_triage(), RalphExecuteRequest, serve_dashboard(), switch_agent_protocol() (+1 more)

### Community 2 - "reviews"
Cohesion: 0.07
Nodes (28): enabled, auto_incremental_review, auto_pause_after_reviewed_commits, drafts, enabled, simplify, unit_tests, instructions (+20 more)

### Community 4 - "knowledge_base"
Cohesion: 0.09
Nodes (24): enabled, chat, allow_non_org_members, auto_reply, integrations, inheritance, jira, linear (+16 more)

### Community 5 - "test_switch_agent.py"
Cohesion: 0.19
Nodes (10): 🧪 Verified Test Suite, LayaDecisionGate, test_api_triage_endpoint(), test_laya_gate_bug_fix_dispatch_to_ralph(), test_laya_gate_destructive_command_blocking(), test_laya_gate_human_approval_trigger(), test_laya_gate_prompt_injection_blocking(), test_laya_gate_submillisecond_latency() (+2 more)

### Community 6 - "pre_merge_checks"
Cohesion: 0.17
Nodes (12): instructions, mode, name, mode, mode, custom_checks, description, issue_assessment (+4 more)

### Community 7 - "SwitchGuard: On-Device Triage & Autonomous Collaborative Agent"
Cohesion: 0.20
Nodes (9): 1. Run the Tests, 2. Launch the Collaborative Agent Server, 3. Open the War Room, 4. Endpoints, Built for the *Flip the Switch Hackathon 2026* (WeMakeDevs x DevTools Academy x Switch AI), 🚀 Quick Start, SwitchGuard: On-Device Triage & Autonomous Collaborative Agent, 💡 The Core Problem (+1 more)

### Community 8 - "Ralph Agent Instructions"
Cohesion: 0.20
Nodes (9): Browser Testing (If Available), Consolidate Patterns, Important, Progress Report Format, Quality Requirements, Ralph Agent Instructions, Stop Condition, Update CLAUDE.md Files (+1 more)

### Community 9 - "Ralph Agent Instructions"
Cohesion: 0.20
Nodes (9): Browser Testing (Required for Frontend Stories), Consolidate Patterns, Important, Progress Report Format, Quality Requirements, Ralph Agent Instructions, Stop Condition, Update AGENTS.md Files (+1 more)

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LayaDecisionEngine` connect `LayaDecisionEngine` to `ralph_runner.py`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `🧪 Verified Test Suite` (e.g. with `test_api_triage_endpoint()` and `test_laya_gate_bug_fix_dispatch_to_ralph()`) actually correct?**
  _`🧪 Verified Test Suite` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `LayaDecisionEngine` be split into smaller, more focused modules?**
  _Cohesion score 0.07087486157253599 - nodes in this community are weakly interconnected._
- **Why does `TestLayaDecisionEngine` connect `LayaDecisionEngine` to `ralph_runner.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Should `server.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07575757575757576 - nodes in this community are weakly interconnected._
- **Why does `reviews` connect `reviews` to `knowledge_base`, `pre_merge_checks`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Should `reviews` be split into smaller, more focused modules?**
  _Cohesion score 0.07142857142857142 - nodes in this community are weakly interconnected._