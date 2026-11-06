#!/usr/bin/env python3
"""Interactive Switch Room Live Simulator for CampusHire Relay.

Simulates the WeMakeDevs "Flip the Switch" Hackathon workflow:
- Step 1: Placement Officer posts recruiter JD to #placement-drive-2027
- Step 2: @DriveCoordinator extracts criteria, generates announcement & milestone checklist
- Step 3: @EligibilityAuditor audits 2027 student dataset, identifies verified list and borderline queue
- Step 4: @PlacementOfficer approves borderline candidate waiver
- Step 5: Export verified shortlist CSV
"""

import re
import time

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    class _SimpleConsole:
        def clear(self):
            pass
        def rule(self, title=""):
            clean = re.sub(r'\[.*?\]', '', title)
            print(f"\n{'='*20} {clean} {'='*20}\n")
        def print(self, msg="", **kwargs):
            clean = re.sub(r'\[.*?\]', '', str(msg))
            print(clean)
    console = _SimpleConsole()

from campushire.storage.student_db import StudentRepository
from campushire.switch_room import SwitchRoom
from campushire.models import SwitchMessage


def print_message(sender: str, text: str):
    """Render room chat message with distinctive agent styling."""
    if HAS_RICH:
        if sender == "DriveCoordinator":
            console.print(Panel(text, title="🤖 [bold green]@DriveCoordinator (AI Agent)[/bold green]", border_style="green"))
        elif sender == "EligibilityAuditor":
            console.print(Panel(text, title="🔍 [bold cyan]@EligibilityAuditor (AI Agent)[/bold cyan]", border_style="cyan"))
        elif sender == "PlacementOfficer":
            console.print(Panel(text, title="👤 [bold yellow]@PlacementOfficer (Human Coordinator)[/bold yellow]", border_style="yellow"))
        else:
            console.print(Panel(text, title=f"[bold]{sender}[/bold]"))
    else:
        print(f"\n--- [{sender}] ---")
        print(text)
        print("-" * 40)
    time.sleep(0.4)


def run_demo():
    console.clear()
    console.rule("[bold magenta]⚡ CampusHire Relay · Switch Room Multi-Agent Simulator ⚡[/bold magenta]")
    console.print(
        "[dim]WeMakeDevs 'Flip the Switch' Hackathon Demo · Channel: #placement-drive-2027[/dim]\n"
    )

    repo = StudentRepository()
    repo.load_synthetic_dataset()
    room = SwitchRoom(student_repo=repo, room_name="#placement-drive-2027")

    # Step 1: Placement Officer posts JD
    sample_jd = """@DriveCoordinator Please process this campus recruitment drive:
Campus Recruitment Drive 2027 - Stripe Technologies
Role: Backend Platform Engineer
Compensation: 28 LPA
Eligibility Requirements:
- Minimum CGPA: 8.00 and above
- 0 active backlogs allowed
- Branches: CSE, IT, ECE
- Passing Batch: 2027
Key Dates:
- Registration Deadline: Nov 15, 2026, 6:00 PM
- Online Technical Assessment: Nov 18, 2026
"""
    print_message("PlacementOfficer", sample_jd)
    responses = room.handle_message(
        SwitchMessage(
            sender="PlacementOfficer",
            content=sample_jd,
            room="#placement-drive-2027",
            mentions=["@DriveCoordinator"],
        )
    )
    for r in responses:
        print_message(r.sender, r.content)

    console.rule("[bold blue]Agent Collaboration & Handoff[/bold blue]")

    # Step 2: Trigger Eligibility Audit
    audit_msg = "@EligibilityAuditor please execute eligibility verification on the 2027 batch"
    print_message("DriveCoordinator", audit_msg)
    responses = room.handle_message(
        SwitchMessage(
            sender="DriveCoordinator",
            content=audit_msg,
            room="#placement-drive-2027",
            mentions=["@EligibilityAuditor"],
        )
    )
    for r in responses:
        print_message(r.sender, r.content)

    console.rule("[bold yellow]Human-in-the-Loop Governance[/bold yellow]")

    # Step 3: Human Officer approves borderline waiver
    waiver_prompt = "@EligibilityAuditor approve waiver for 23CS04 - recommended by CSE HOD for notable open source contributions"
    print_message("PlacementOfficer", waiver_prompt)
    responses = room.handle_message(
        SwitchMessage(
            sender="PlacementOfficer",
            content=waiver_prompt,
            room="#placement-drive-2027",
            mentions=["@EligibilityAuditor"],
        )
    )
    for r in responses:
        print_message(r.sender, r.content)

    console.rule("[bold green]Final Verified Shortlist[/bold green]")

    # Step 4: Display final table
    if HAS_RICH:
        table = Table(title="Verified Candidate Shortlist (Ready for Recruiter Upload)", header_style="bold magenta")
        table.add_column("Roll No", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Branch", style="green")
        table.add_column("CGPA", style="bold yellow")
        table.add_column("Status", style="bold green")

        for c in room.active_report.eligible_candidates:
            status_note = "Waiver Approved" if c.roll_no == "23CS04" else "Eligible"
            table.add_row(c.roll_no, c.name, c.branch, f"{c.cgpa:.2f}", status_note)

        console.print(table)
    else:
        print("\nVerified Candidate Shortlist (Ready for Recruiter Upload):")
        print(f"{'Roll No':<10} {'Name':<20} {'Branch':<8} {'CGPA':<6} {'Status':<16}")
        print("-" * 65)
        for c in room.active_report.eligible_candidates:
            status_note = "Waiver Approved" if c.roll_no == "23CS04" else "Eligible"
            print(f"{c.roll_no:<10} {c.name:<20} {c.branch:<8} {c.cgpa:<6.2f} {status_note:<16}")

    console.print("\n[bold green]✔ Switch Relay run completed successfully![/bold green] Downloadable CSV exported at [cyan]/api/audit/export-csv[/cyan].\n")


if __name__ == "__main__":
    run_demo()
