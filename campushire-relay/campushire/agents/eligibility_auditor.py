"""@EligibilityAuditor agent: evaluates student records against placement criteria with explainable verdicts."""

import io
import csv
from typing import List
from campushire.models import (
    Candidate,
    PlacementCriteria,
    AuditVerdict,
    CandidateAudit,
    AuditReport,
)


class EligibilityAuditor:
    """Agent responsible for candidate eligibility verification, borderline appeal detection, and report generation."""

    def __init__(self, borderline_delta: float = 0.1) -> None:
        self.borderline_delta = borderline_delta

    def audit_candidate(self, candidate: Candidate, criteria: PlacementCriteria) -> CandidateAudit:
        """Evaluate an individual student against strict and borderline requirements."""
        reasons: List[str] = []
        is_hard_disqualified = False

        # 1. Check Batch Year
        if candidate.batch_year != criteria.batch_year:
            reasons.append(f"Graduation batch {candidate.batch_year} does not match target batch {criteria.batch_year}")
            is_hard_disqualified = True

        # 2. Check Department / Branch
        allowed_branches = [b.upper() for b in criteria.eligible_branches]
        if candidate.branch.upper() not in allowed_branches:
            reasons.append(f"Department '{candidate.branch}' is not in eligible branches ({', '.join(allowed_branches)})")
            is_hard_disqualified = True

        # 3. Check Active Backlogs
        if candidate.active_backlogs > criteria.max_active_backlogs:
            reasons.append(f"Has {candidate.active_backlogs} active backlogs (Maximum allowed is {criteria.max_active_backlogs})")
            is_hard_disqualified = True

        # 4. Check CGPA
        if candidate.cgpa >= criteria.min_cgpa:
            if not is_hard_disqualified:
                return CandidateAudit(candidate=candidate, verdict=AuditVerdict.ELIGIBLE, reasons=[])
        else:
            delta = criteria.min_cgpa - candidate.cgpa
            if not is_hard_disqualified and delta <= (self.borderline_delta + 1e-6):
                # Borderline candidate eligible for human waiver consideration
                reasons.append(
                    f"Borderline CGPA: {candidate.cgpa:.2f} (Cutoff: {criteria.min_cgpa:.2f}, Gap: -{delta:.2f}). Flagged for Placement Officer review."
                )
                return CandidateAudit(candidate=candidate, verdict=AuditVerdict.BORDERLINE, reasons=reasons)
            else:
                reasons.append(f"CGPA {candidate.cgpa:.2f} is below minimum requirement of {criteria.min_cgpa:.2f}")

        return CandidateAudit(candidate=candidate, verdict=AuditVerdict.INELIGIBLE, reasons=reasons)

    def audit_candidates(self, candidates: List[Candidate], criteria: PlacementCriteria) -> AuditReport:
        """Batch evaluate all candidates and build aggregate audit report."""
        eligible_candidates: List[Candidate] = []
        borderline_audits: List[CandidateAudit] = []
        ineligible_audits: List[CandidateAudit] = []

        for candidate in candidates:
            audit = self.audit_candidate(candidate, criteria)
            if audit.verdict == AuditVerdict.ELIGIBLE:
                eligible_candidates.append(candidate)
            elif audit.verdict == AuditVerdict.BORDERLINE:
                borderline_audits.append(audit)
            else:
                ineligible_audits.append(audit)

        # Sort eligible by CGPA descending
        eligible_candidates.sort(key=lambda c: c.cgpa, reverse=True)

        return AuditReport(
            criteria=criteria,
            total_evaluated=len(candidates),
            eligible_count=len(eligible_candidates),
            ineligible_count=len(ineligible_audits),
            borderline_count=len(borderline_audits),
            eligible_candidates=eligible_candidates,
            borderline_audits=borderline_audits,
            ineligible_audits=ineligible_audits,
        )

    def format_audit_summary_markdown(self, report: AuditReport) -> str:
        """Render a publication-ready Markdown audit report for team room display."""
        crit = report.criteria
        lines = [
            f"📊 ELIGIBILITY AUDIT REPORT: {crit.company_name} ({crit.role_title})",
            "══════════════════════════════════════════════════════",
            f"📋 Total Students Evaluated : {report.total_evaluated}",
            f"✅ Verified Eligible        : {report.eligible_count}",
            f"⚠️ Borderline Review Queue   : {report.borderline_count}",
            f"❌ Disqualified             : {report.ineligible_count}",
            "══════════════════════════════════════════════════════",
            "\n🎓 Verified Shortlisted Candidates (Top 5 preview):",
        ]

        preview_count = min(5, len(report.eligible_candidates))
        for c in report.eligible_candidates[:preview_count]:
            lines.append(f"  • {c.roll_no} | {c.name.ljust(18)} | {c.branch.ljust(5)} | CGPA: {c.cgpa:.2f}")
        if len(report.eligible_candidates) > preview_count:
            lines.append(f"  • ... and {len(report.eligible_candidates) - preview_count} more verified students")

        if report.borderline_audits:
            lines.append("\n⚠️ Borderline Review Queue (Action Required from @PlacementOfficer):")
            for b in report.borderline_audits:
                cand = b.candidate
                reason = b.reasons[0] if b.reasons else "Borderline CGPA"
                lines.append(f"  • {cand.roll_no} ({cand.name}, {cand.branch}) - {reason}")
            lines.append("\n💬 Reply '@PlacementOfficer approve [roll_no]' to grant waiver or '@PlacementOfficer reject [roll_no]'.")

        return "\n".join(lines)

    def export_shortlist_csv(self, report: AuditReport) -> str:
        """Export verified eligible candidates to CSV string for recruiter upload.
        
        Sanitizes cell contents against CSV injection (formula injection).
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["roll_no", "name", "email", "branch", "cgpa", "active_backlogs", "batch_year"])
        
        def _sanitize(val: object) -> object:
            s = str(val)
            if s.startswith(("=", "+", "-", "@", "\t", "\r")):
                return "'" + s
            return val

        for c in report.eligible_candidates:
            writer.writerow([
                _sanitize(c.roll_no),
                _sanitize(c.name),
                _sanitize(c.email),
                _sanitize(c.branch),
                c.cgpa,
                c.active_backlogs,
                c.batch_year,
            ])
        return output.getvalue()
