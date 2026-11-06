# Room Briefing: Campus Placement Drive Coordination (campus-hire-drive)

This Switch room coordinates end-to-end campus recruitment drives. Humans and AI agents share this persistent room log, room documents, and references.

## 1. Dual-Process Architecture: System 1 (Laya) & System 2 (Switch Agents)

CampusHire Relay pairs **Laya's sub-50ms local neural reflex engine (System 1)** with **Switch AI's multi-agent deliberative collaboration (System 2)**:
- **System 1 Reflex Gate (Laya):** Audits every incoming recruiter notice and message for prompt injections and adversarial overrides before passing to LLMs; routes intents and evaluates candidate mock answers in milliseconds.
- **System 2 Deliberative Teams (Switch Agents):** Coordinates complex reasoning, extraction, human approval gates, deterministic validation, and operations pack publication.

## 2. Workflow Protocol & Roles

- **Human Placement Coordinator (`@coordinator`):** Posts incoming recruiter notices, clarifies missing rules, approves `drive_brief.json`, resolves `NEEDS_REVIEW` student records, and signs off on outgoing announcements.
- **Drive Coordinator (`@campus-hire-drive-coordinator` | Role: `@coordinator-agent`):** Audits notice safety via Laya, extracts structured eligibility rules into `outputs/drive_brief.json`, enforces the human approval gate, delegates verification to the auditor, and compiles the operations pack (`draft_announcement.md`, `attendance_sheet.csv`, `drive_checklist.md`).
- **Eligibility Auditor (`@campus-hire-eligibility-auditor` | Role: `@auditor-agent`):** Restricted via `addressing: owner-agents`. Executes deterministic Python verification (`scripts/validate_eligibility.py`) against `data/sample_students.csv` and issues a cryptographic SHA-256 receipt (`outputs/audit_receipt.json`).
- **Career Coach (`@campus-hire-career-coach` | Role: `@coach-agent`):** Generates personalized preparation kits (`outputs/student_prep/`) for verified eligible students via `scripts/generate_student_prep.py` and conducts voice-dictated STAR mock interviews evaluated instantly via Laya in `#student-prep-studio`.

## 3. Mandatory Governance & Safety Rules (Switch Three-Factor Security Compliance)

1. **System 1 Pre-Screening:** No recruiter notice is ingested into agent context until verified safe by `scripts/laya_gate.py audit-notice`.
2. **No Unapproved Execution:** No agent may trigger the student database audit until the human coordinator explicitly replies `Approved` to the extracted criteria JSON in this room.
3. **Communicative Dehallucination:** If a recruiter notice omits graduation year, eligible branches, minimum CGPA, or backlog policy, `@campus-hire-drive-coordinator` must halt and ask the human coordinator to supply the missing value.
4. **Deterministic Math Only:** Eligibility classification must be performed exclusively via `scripts/validate_eligibility.py`. Never estimate or hallucinate student eligibility in free text.
5. **PII Minimization:** Room posts and generated CSV reports must reference students by `student_id` (e.g., `STU001`) rather than exposing personal phone numbers or raw email addresses in public channel logs.
6. **Durable Room Documents:** Attach approved `drive_brief.json` and `audit_receipt.json` as Switch Room Documents (`!list-documents`) so future team members can audit the exact rules and SHA-256 checksums used for the shortlist.
