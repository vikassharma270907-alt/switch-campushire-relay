# Moving AI Coding Agents from Isolated Terminals to Auditable Team Chat: How We Built CampusHire Relay on Switch AI

*Published for the WeMakeDevs × DevTools Academy "Flip the Switch" Hackathon (November 2026)*  
*Targeting Track 01: Best Business Workflow, Track 02: Best Personal / Creative Workflow, and Side Track: Code with Wispr*  
*Live Article on Dev.to: [https://dev.to/vikas_sharma_ffe81cb77741/moving-ai-coding-agents-from-isolated-terminals-to-auditable-team-chat-how-we-built-campushire-53me](https://dev.to/vikas_sharma_ffe81cb77741/moving-ai-coding-agents-from-isolated-terminals-to-auditable-team-chat-how-we-built-campushire-53me)*

---

## Introduction: The Terminal Isolation & "All-or-Nothing" LLM Problem

If you've used tools like Claude Code, OpenAI Codex, or OpenCode over the past year, you’ve experienced the productivity of AI-assisted engineering. You prompt your terminal, the model edits files, runs tests, and fixes syntax errors.

**Yet, the moment you move into team workflows, terminal-bound agents break down:**
1. **Context Ephemerality:** Everything lives and dies in a local shell session. The moment the tab closes, your team has zero record of why the agent took a specific action.
2. **The "Single-Pilot" Silo:** Non-technical stakeholders—project managers, HR directors, university placement heads—cannot participate in or oversee what the agent is doing.
3. **The "All-or-Nothing" LLM Trap:** Dispatching every single message check, prompt-injection audit, or tabular calculation to an LLM introduces 2–5 seconds of latency, high token costs, and floating-point arithmetic errors.

During the **WeMakeDevs × DevTools Academy "Flip the Switch" Hackathon**, our team built **CampusHire Relay** to solve this problem.

CampusHire Relay takes AI coding agents out of isolated developer terminals and embeds them directly into persistent, auditable team channels (**Mattermost / Slack**) using **Switch AI**, augmented with **Laya's sub-50ms local neural reflex engine** for Kahneman Dual-Process cognition.

🔗 **Quick Links & Live Artifacts:**
- 🌐 **Live Web Application:** [https://switch-campushire-relay.vercel.app/](https://switch-campushire-relay.vercel.app/)
- 📊 **Interactive Pitch Deck (9 Slides):** [https://switch-campushire-relay.vercel.app/slides](https://switch-campushire-relay.vercel.app/slides)
- 💻 **GitHub Repository:** [https://github.com/vikassharma270907-alt/switch-campushire-relay](https://github.com/vikassharma270907-alt/switch-campushire-relay)

---

## 1. Dual-Process Architecture: System 1 (Laya) & System 2 (Switch AI)

Rather than treating LLMs as brute-force hammers for every task, CampusHire Relay introduces a two-tier cognitive architecture:
- **System 1 (Local Neural Reflex Layer via Laya):** Fast, sub-50ms local CPU evaluation. Performs prompt-injection guardrails, rapid message intent classification, and real-time STAR mock-interview scoring with zero token expenditure.
- **System 2 (Deliberative Multi-Agent Collaboration via Switch AI):** Structured, persistent team chat in Mattermost where three specialized AI coding agents collaborate with humans under cryptographic verification and strict approval gates.

```
Switch Room 1: #campus-hire-drive (Track 01: Business Operations)
├── System 1 Reflex Gate (Laya: Pre-LLM Injection Check & Intent Routing <1ms)
├── Human Placement Coordinator (@coordinator)
├── Drive Coordinator Agent (@campus-hire-drive-coordinator | addressing: anyone)
└── Eligibility Auditor Agent (@campus-hire-eligibility-auditor | addressing: owner-agents)

Switch Room 2: #student-prep-studio (Track 02: Candidate Interview Prep)
├── Shortlisted Students (STU001, STU002)
├── Career Coach Agent (@campus-hire-career-coach | addressing: anyone)
└── System 1 Reflex Coach (Laya: Spoken STAR Rubric Scoring & Recommendations)
```

---

## 2. Under the Hood: Six Switch Primitives We Leveraged

CampusHire Relay is engineered around Switch's native architectural mechanisms:

### Primitive 1: PostgreSQL Row-Backed Message Bus
In Switch, every room, thread, and message is an auditable row in PostgreSQL protected by workspace Row-Level Security (RLS). When a recruiter notice is processed and approved, that decision is immutably logged.

### Primitive 2: Addressing Policy (`anyone` vs. `owner-agents`)
Switch uniquely decouples resource access from invocation rights:
- `@campus-hire-drive-coordinator` has `addressing: anyone`: Any placement officer in the channel can post a notice and ask the agent to parse it.
- `@campus-hire-eligibility-auditor` is locked to `addressing: owner-agents`: Only the coordinator agent or workspace owner can trigger a database audit.

### Primitive 3: Room Instructions (`switch/room-instructions.md`)
Switch briefs every agent joining a room with persistent instructions. We use this to enforce:
1. System 1 pre-screening before ingesting recruiter notices.
2. Mandatory human approval before database queries.
3. Communicative dehallucination (halting when notices omit cutoffs).
4. PII minimization (logging only student IDs like `STU001` in public channels).

### Primitive 4: Three-Factor Security Compliance
Switch's documentation warns against the simultaneous presence of:
`Unsupervised Action` + `Critical Reach` + `Unvetted Input`

CampusHire Relay breaks this unsafe triad:
- External recruiter notices (*Unvetted Input*) are pre-screened by Laya in <1ms, parsed by the coordinator agent, and locked behind a mandatory **Human Approval Gate**.
- The student database (*Critical Reach*) is queried exclusively by a deterministic Python script, never by an autonomous LLM prompt.
- Candidate coaching is separated into a linked room (`#student-prep-studio`), completely isolated from the master database.

### Primitive 5: Room Documents (`!list-documents`)
Agents store structured knowledge directly into room memory using `create_room_document`:
- `drive_brief.json`: The locked, approved eligibility rules.
- `audit_receipt.json`: A SHA-256 cryptographic receipt of input CSV, criteria JSON, and verified output CSV.

### Primitive 6: Wispr Flow Voice Dictation
By integrating Wispr Flow, placement coordinators dictate approvals hands-free (*"Approved. @coord lock the criteria and hand off to @auditor"*), while students in `#student-prep-studio` practice spoken STAR-method mock interviews with `@campus-hire-career-coach`.

---

## 3. Academic Research Grounding: Why Our Multi-Agent Design Works

Our architecture is informed by 2024–2026 academic research in multi-agent systems:

1. **The MAST Failure Taxonomy (Cemri et al., UC Berkeley 2025; arXiv:2503.13657):**  
   In an analysis of 1,642 multi-agent traces across 7 frameworks, 44.2% of failures stemmed from system design issues and 32.4% from inter-agent misalignment. The study showed that independent agents operating without centralized oversight amplify errors by **17.2×** compared to **4.4×** with centralized coordination. Switch provides that exact centralized coordination layer.
2. **Kahneman Dual-Process & ProgRouter (Li et al., ACL EMNLP 2026; arXiv:2608.25992):**  
   Step-wise routing: local neural reflex (Laya) for sub-50ms filtering and intent routing, reserving high-order LLM reasoning for multi-agent negotiation, while delegating tabular calculations to deterministic Python scripts.
3. **Communicative Dehallucination (ChatDev, Qian et al., ACL 2024):**  
   When agents proactively request clarification on ambiguous inputs before acting, executability increases to 88%. Our parser (`extract_criteria.py`) outputs `requires_human_clarification: true` whenever a notice omits cutoffs, halting execution before errors propagate.
4. **Structured Handoffs & SOPs (MetaGPT, Hong et al., ICLR 2024):**  
   MetaGPT proved that passing typed schemas rather than free prose reduces code corrections by 67%. Our agents exchange strict JSON and CSV artifacts (`drive_brief.json`, `audit_receipt.json`, `eligible.csv`).

---

## 4. Quickstart: Reproducing CampusHire Relay in 60 Seconds

```bash
# 1. Clone & install dependencies
git clone https://github.com/vikassharma270907-alt/switch-campushire-relay.git
cd switch-campushire-relay
pip install -r requirements.txt

# 2. Run the 41-test unit test suite (95% coverage)
pytest -v

# 3. Execute the deterministic pipeline end-to-end
python scripts/laya_gate.py audit-notice data/sample_recruiter_notice.md
python scripts/extract_criteria.py data/sample_recruiter_notice.md outputs/drive_brief.json
python scripts/validate_eligibility.py data/sample_students.csv outputs/drive_brief.json outputs/eligibility_results.csv
python scripts/generate_reports.py
python scripts/generate_student_prep.py
python scripts/laya_gate.py evaluate-star "During my final year project, our team optimized database throughput. I built an asynchronous Redis caching layer, reducing latency by 65%."
```

### The Verification Output:
```json
{
  "students_csv_sha256": "5508f7aa6fb03130a2c1fbc69e6aeaaad7cf2eb138d772961a9d2b131d7e68c5",
  "criteria_json_sha256": "82647df707ab784312e7b6844219477b7007baeb47e57cf974bb81a153a10f7d",
  "results_csv_sha256": "4a9debe425ba232e9291ccc09be05f80fef3d40ee9a9690fad8465bdb5600d82",
  "total_records": 7,
  "eligible_count": 2,
  "not_eligible_count": 4,
  "needs_review_count": 1
}
```

---

## Conclusion: The Future of Team-Agent Collaboration

The greatest value of AI in 2026 isn't a chatbot answering questions in an isolated silo. It is the ability for humans and specialized AI coding agents to collaborate in shared, governed team spaces.

With **Switch AI** and **Laya**, our coding agents are no longer solitary CLI utilities—they are accountable teammates. 

Check out our repository at [vikassharma270907-alt/switch-campushire-relay](https://github.com/vikassharma270907-alt/switch-campushire-relay), star the project on GitHub, test the live app at [switch-campushire-relay.vercel.app](https://switch-campushire-relay.vercel.app/), and join us in flipping the switch!
