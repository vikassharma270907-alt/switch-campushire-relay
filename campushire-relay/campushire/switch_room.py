"""Switch Room relay: manages multi-agent coordination, handoffs, and human-in-the-loop approvals."""

import datetime
import re
from typing import List, Optional, Set
from campushire.models import (
    SwitchMessage,
    PlacementCriteria,
    AuditReport,
)
from campushire.agents.drive_coordinator import DriveCoordinator
from campushire.agents.eligibility_auditor import EligibilityAuditor
from campushire.storage.student_db import StudentRepository
from campushire.governance import ArmorGovernanceEngine, IntentDeclaration


AUTHORIZED_OFFICERS: Set[str] = {
    "PlacementOfficer",
    "Coordinator",
    "Dean",
    "DeanAcademics",
    "HOD",
    "Admin",
}


class SwitchRoom:
    """Collaboration room coordinator facilitating message passing between human officers and AI agents."""

    def __init__(
        self,
        student_repo: Optional[StudentRepository] = None,
        room_name: str = "#placement-drive",
        borderline_delta: float = 0.1,
    ) -> None:
        self.room_name = room_name
        self.repo = student_repo or StudentRepository()
        if not self.repo.get_all_candidates():
            self.repo.load_synthetic_dataset()

        self.drive_coordinator = DriveCoordinator()
        self.eligibility_auditor = EligibilityAuditor(borderline_delta=borderline_delta)
        self.governance = ArmorGovernanceEngine()

        self.history: List[SwitchMessage] = []
        self.active_criteria: Optional[PlacementCriteria] = None
        self.active_report: Optional[AuditReport] = None

    def post_message(self, sender: str, content: str, mentions: Optional[List[str]] = None) -> SwitchMessage:
        """Create, log, and return a room message."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        msg = SwitchMessage(
            sender=sender,
            content=content,
            room=self.room_name,
            mentions=mentions or [],
            timestamp=timestamp,
        )
        self.history.append(msg)
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        return msg

    def handle_message(self, message: SwitchMessage) -> List[SwitchMessage]:
        """Dispatch incoming room message to target agent based on mentions and content."""
        self.history.append(message)
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        responses: List[SwitchMessage] = []
        content = message.content

        # 1. DriveCoordinator Dispatch
        if "@DriveCoordinator" in message.mentions or "@DriveCoordinator" in content:
            criteria = self.drive_coordinator.parse_job_description(content)
            self.active_criteria = criteria

            # Generate Announcement
            announcement = self.drive_coordinator.generate_announcement(criteria)
            responses.append(self.post_message("DriveCoordinator", announcement))

            # Generate Administrative Checklist & Hand-off to EligibilityAuditor
            checklist = self.drive_coordinator.generate_timeline_checklist(criteria)
            checklist_text = (
                f"📋 **Milestone Checklist for {criteria.company_name}**:\n"
                + "\n".join(checklist)
                + f"\n\n🤝 Handoff: @EligibilityAuditor, please audit the {criteria.batch_year} batch against these criteria."
            )
            responses.append(
                self.post_message(
                    "DriveCoordinator",
                    checklist_text,
                    mentions=["@EligibilityAuditor"],
                )
            )
            return responses

        # 2. EligibilityAuditor Dispatch
        if "@EligibilityAuditor" in message.mentions or "@EligibilityAuditor" in content:
            # Check for Human-in-the-loop waiver approval
            if "approve" in content.lower() or "waiver" in content.lower():
                if message.sender not in AUTHORIZED_OFFICERS:
                    responses.append(
                        self.post_message(
                            "EligibilityAuditor",
                            f"⛔ **Permission Denied**: Sender '{message.sender}' is not authorized to grant academic placement waivers. Only verified placement officers can approve borderline candidates.",
                        )
                    )
                    return responses

                roll_matches = re.findall(r"\b(2[0-9][A-Z]{2,4}[0-9]{2,3})\b", content)
                if roll_matches and self.active_report:
                    target_roll = roll_matches[0].upper()
                    # Find candidate in borderline
                    matching_borderline = [
                        b for b in self.active_report.borderline_audits if b.candidate.roll_no == target_roll
                    ]
                    if matching_borderline:
                        cand = matching_borderline[0].candidate
                        cutoff = self.active_criteria.min_cgpa if self.active_criteria else 8.0
                        intent = IntentDeclaration(
                            intent_id=f"INT-WAIVER-{target_roll}",
                            action="approve_borderline_waiver",
                            target=f"candidate:{target_roll}",
                            parameters={
                                "cgpa": cand.cgpa,
                                "cutoff": cutoff,
                                "active_backlogs": cand.active_backlogs,
                            },
                        )
                        token = self.governance.generate_intent_token(intent)
                        decision = self.governance.verify_and_authorize(intent, token)
                        if decision.decision != "ALLOW":
                            responses.append(
                                self.post_message(
                                    "EligibilityAuditor",
                                    f"🛑 **ArmorIQ Governance Block**: Waiver denied for {cand.roll_no}. {decision.reason} [Policy: {decision.policy_id}]",
                                )
                            )
                            return responses

                        # Move to eligible
                        updated_eligible = list(self.active_report.eligible_candidates) + [cand]
                        updated_borderline = [
                            b for b in self.active_report.borderline_audits if b.candidate.roll_no != target_roll
                        ]
                        self.active_report = self.active_report.model_copy(
                            update={
                                "eligible_candidates": updated_eligible,
                                "borderline_audits": updated_borderline,
                                "eligible_count": len(updated_eligible),
                                "borderline_count": len(updated_borderline),
                            }
                        )
                        responses.append(
                            self.post_message(
                                "EligibilityAuditor",
                                f"✅ **Waiver granted for {cand.roll_no} ({cand.name})**.\n"
                                f"Candidate added to verified shortlist under ArmorIQ Policy {decision.policy_id}. Total eligible now: {self.active_report.eligible_count}.",
                            )
                        )
                        return responses

            # Regular audit execution
            if self.active_criteria is None:
                responses.append(
                    self.post_message(
                        "EligibilityAuditor",
                        "⚠️ No active placement criteria found. Please provide a JD to @DriveCoordinator first.",
                    )
                )
                return responses

            candidates = self.repo.get_all_candidates()
            report = self.eligibility_auditor.audit_candidates(candidates, self.active_criteria)
            self.active_report = report

            report_md = self.eligibility_auditor.format_audit_summary_markdown(report)
            report_md += (
                f"\n\n📢 @PlacementOfficer: Please review the audit summary above. "
                "Reply with approvals for borderline candidates or '@DriveCoordinator finalize' to dispatch notifications."
            )
            responses.append(
                self.post_message(
                    "EligibilityAuditor",
                    report_md,
                    mentions=["@PlacementOfficer"],
                )
            )
            return responses

        return responses
