[$deep-research]
# Reproducibility Master Prompt & Deep-Research Connector

## 1. Master Project Generator Prompt
```text
You are building the complete CampusHire Relay repository for the WeMakeDevs × DevTools Academy "Flip the Switch" Hackathon using Switch AI.

Target Tracks:
- Track 01: Best Business Workflow ($2,000 Cash)
- Track 02: Best Personal / Creative Workflow ($2,000 Cash)
- Side Track: Code with Wispr ($500 Cash)

Requirements:
1. Multi-Agent Dual-Room Architecture:
   - Room 1 (#campus-hire-drive): Human Placement Coordinator + @campus-hire-drive-coordinator (addressing: anyone) + @campus-hire-eligibility-auditor (addressing: owner-agents).
   - Room 2 (#student-prep-studio): Shortlisted candidates + @campus-hire-career-coach (addressing: anyone).
2. Switch Primitives:
   - Official version: 1 Switch Console template with params: (team, provider, location, directory, bridge).
   - Room Instructions briefing every agent on human approval gates and PII minimization.
   - Switch Room Documents (!list-documents) storing drive_brief.json and audit_receipt.json.
   - Role-based addressing separation and Three-Factor Security compliance.
3. Deterministic Python Tooling:
   - scripts/extract_criteria.py: Regex-hardened parser supporting en/em-dashes and hyphens, extracting deadlines and selection stages, flagging missing fields via requires_human_clarification.
   - scripts/validate_eligibility.py: Deterministic math engine checking batch, branch, CGPA, backlogs, duplicate student_ids, null checks, and generating SHA-256 audit_receipt.json.
   - scripts/generate_reports.py: Compiles eligible.csv, not_eligible.csv, needs_review.csv, attendance_sheet.csv (Hall-A seats), draft_announcement.md, and drive_checklist.md.
   - scripts/generate_student_prep.py: Generates tailored student preparation kits and Wispr Flow voice mock interview prompts.
4. Testing:
   - 10-test PyTest suite achieving 100% boundary and branch coverage (boundary CGPA 7.0, duplicate IDs, missing CGPA, isolated backlogs, clarification triggers).
5. Grounding:
   - Grounded in 2024–2026 multi-agent academic literature (MAST, ChatDev, MetaGPT, AutoGen, ProgRouter, Zou et al. ACL 2026).
```

---

## 2. Deep-Research Literature Connector
```text
[$deep-research]
Search recent (2024–2026) peer-reviewed academic literature on multi-agent LLM systems, human-agent collaboration, and agent verification frameworks:
- Primary Sources:
  1. MAST Taxonomy (Cemri et al., UC Berkeley 2025; arXiv:2503.13657): "Why Do Multi-Agent LLM Systems Fail? An Empirical Study of 1,642 Traces."
  2. LLM-Based Human-Agent Collaboration Survey (Zou et al., Findings of ACL 2026; arXiv:2505.00753).
  3. Multi-Agent Collaboration Mechanisms Survey (Tran et al., 2025; arXiv:2501.06322).
  4. ProgRouter (Li et al., Findings of ACL: EMNLP 2026; arXiv:2608.25992): Online Progress-Guided Orchestration for Multi-Agent LLM Workflows under Quality-Cost Tradeoffs.
  5. ChatDev: Communicative Agents for Software Development (Qian et al., ACL 2024; arXiv:2307.07924).
  6. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework (Hong et al., ICLR 2024 Oral; arXiv:2308.00352).
  7. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation (Wu et al., COLM 2024; arXiv:2308.08155).
- Synthesis Focus:
  - Extract failure mode statistics and explain how centralized Switch rooms prevent error cascade amplification (17.2x vs 4.4x).
  - Define human agency levels (A1 to A5) and map Human Approval Gate 1 and Exception Gate 2 to cognitive supervision cost reduction.
  - Document quality-cost tradeoffs of routing tabular arithmetic to zero-token Python verifiers.
```
