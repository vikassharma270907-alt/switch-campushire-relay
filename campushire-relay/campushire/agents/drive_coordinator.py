"""@DriveCoordinator agent: parses recruiter JDs, generates student announcements & checklists."""

import re
from typing import List
from campushire.models import PlacementCriteria


class DriveCoordinator:
    """Agent responsible for JD intake, requirement extraction, and broadcast formatting."""

    def parse_job_description(self, raw_text: str) -> PlacementCriteria:
        """Extract structured placement criteria from unstructured recruiter text."""
        # 1. Company Name
        company = "Partner Company"
        # Check explicit dash separator: "Drive 2027 - NexaCorp" or "Drive - Stripe"
        dash_match = re.search(r"(?:Campus Recruitment.*?-\s*|-\s*)([A-Z][A-Za-z0-9_]+(?:\s+[A-Z][A-Za-z0-9_]+)?)", raw_text)
        if dash_match and dash_match.group(1).strip() not in {"Nov", "Dec", "Jan", "Feb"}:
            company = dash_match.group(1).strip()
        else:
            comp_match = re.search(
                r"(?:Campus Recruitment(?: Drive)?\s+(?:for|at)\s+|Welcome to\s+|Team,\s*|hiring at\s+)([A-Z][A-Za-z0-9_]+(?:\s+[A-Z][A-Za-z0-9_]+)?)",
                raw_text,
                re.IGNORECASE,
            )
            if comp_match:
                company = comp_match.group(1).strip()
            else:
                first_words = [w for w in re.findall(r"\b([A-Z][a-zA-Z0-9]+)\b", raw_text) if w not in {"DriveCoordinator", "Campus", "Recruitment", "Drive", "Role", "CTC", "Batch"}]
                if first_words:
                    company = first_words[0]

        # 2. Role Title
        role = "Software Engineer"
        role_match = re.search(r"(?:hiring for the role of|role of|position of|hiring for:?)\s+([A-Za-z0-9\s/-]+?)(?=\s+(?:with|at|for|\.|\n))", raw_text, re.IGNORECASE)
        if role_match:
            role = re.sub(r"^(?:the\s+role\s+of\s+|the\s+position\s+of\s+)", "", role_match.group(1).strip(), flags=re.IGNORECASE)

        # 3. Package / CTC
        package = "Industry Standard"
        pkg_match = re.search(r"(\d+(?:\.\d+)?\s*(?:LPA|Lakhs?|CTC|k/month|INR))", raw_text, re.IGNORECASE)
        if pkg_match:
            package = pkg_match.group(1).strip()

        # 4. Minimum CGPA
        min_cgpa = 7.0
        cgpa_match = re.search(r"(?:CGPA|GPA)[:\s]*([0-9](?:\.[0-9]+)?)", raw_text, re.IGNORECASE)
        if cgpa_match:
            min_cgpa = float(cgpa_match.group(1))

        # 5. Backlogs
        max_backlogs = 0
        if re.search(r"(?:no active backlogs|0 backlogs|zero backlogs|without active backlogs)", raw_text, re.IGNORECASE):
            max_backlogs = 0
        else:
            bl_match = re.search(r"(?:max|maximum|upto)?\s*([0-9])\s*(?:active\s*)?backlog", raw_text, re.IGNORECASE)
            if bl_match:
                max_backlogs = int(bl_match.group(1))

        # 6. Eligible Branches
        branches: List[str] = []
        branch_patterns = ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL", "CS", "AI", "DS"]
        for b in branch_patterns:
            if re.search(rf"\b{b}\b", raw_text, re.IGNORECASE):
                branches.append(b.upper())
        if not branches:
            branches = ["CSE", "IT", "ECE"]

        # 7. Batch Year
        batch_year = 2027
        batch_match = re.search(r"\b(202[4-9])\b", raw_text)
        if batch_match:
            batch_year = int(batch_match.group(1))

        # 8. Deadline & Drive Date
        deadline = "TBD"
        dl_match = re.search(r"(?:Deadline|Register by)[:\s]*([A-Za-z0-9,\s:]+?)(?=\n|$)", raw_text, re.IGNORECASE)
        if dl_match:
            deadline = dl_match.group(1).strip()

        drive_date = "TBD"
        dd_match = re.search(r"(?:Assessment|Drive Date|Interview Date)[:\s]*([A-Za-z0-9,\s:]+?)(?=\n|$)", raw_text, re.IGNORECASE)
        if dd_match:
            drive_date = dd_match.group(1).strip()

        return PlacementCriteria(
            company_name=company,
            role_title=role,
            package_ctc=package,
            min_cgpa=min_cgpa,
            max_active_backlogs=max_backlogs,
            eligible_branches=branches,
            batch_year=batch_year,
            deadline=deadline,
            drive_date=drive_date,
        )

    def generate_announcement(self, criteria: PlacementCriteria) -> str:
        """Format an official student broadcast announcement."""
        branches_str = ", ".join(criteria.eligible_branches)
        return (
            f"📢 CAMPUS PLACEMENT DRIVE: {criteria.company_name.upper()}\n"
            f"══════════════════════════════════════════════════════\n"
            f"🏢 Company       : {criteria.company_name}\n"
            f"💼 Role          : {criteria.role_title}\n"
            f"💰 CTC Package   : {criteria.package_ctc}\n"
            f"🎓 Target Batch  : {criteria.batch_year} Graduating Class\n"
            f"📚 Branches      : {branches_str}\n"
            f"📊 Cut-off       : CGPA: {criteria.min_cgpa:.2f}+ (Max Active Backlogs: {criteria.max_active_backlogs})\n"
            f"⏰ Deadline      : {criteria.deadline}\n"
            f"📅 Drive Date    : {criteria.drive_date}\n"
            f"══════════════════════════════════════════════════════\n"
            f"👉 Eligible students must register via portal before deadline.\n"
            f"⚠️ Verification in progress by @EligibilityAuditor."
        )

    def generate_timeline_checklist(self, criteria: PlacementCriteria) -> List[str]:
        """Generate administrative milestone checklist for placement officers."""
        return [
            f"[ ] Step 1: Broadcast announcement for {criteria.company_name} ({criteria.role_title})",
            f"[ ] Step 2: Trigger @EligibilityAuditor to filter registered candidates",
            f"[ ] Step 3: Review borderline candidates (< 0.1 CGPA delta) with HOD",
            f"[ ] Step 4: Submit verified candidate shortlist to {criteria.company_name} HR before {criteria.deadline}",
            f"[ ] Step 5: Coordinate test lab infrastructure for Assessment on {criteria.drive_date}",
        ]
