"""Student repository managing candidate records and synthetic placement dataset."""

from typing import Dict, List, Optional
from campushire.models import Candidate


class StudentRepository:
    """Thread-safe in-memory repository for campus candidate profiles."""

    def __init__(self) -> None:
        self._students: Dict[str, Candidate] = {}

    def add_candidate(self, candidate: Candidate) -> None:
        """Add or update candidate record."""
        self._students[candidate.roll_no] = candidate

    def get_candidate(self, roll_no: str) -> Optional[Candidate]:
        """Fetch candidate by roll number."""
        return self._students.get(roll_no)

    # Alias for convenience
    get_candidate_by_roll = get_candidate

    def get_all_candidates(self) -> List[Candidate]:
        """Return all candidates in repository."""
        return list(self._students.values())

    def get_candidates_by_batch(self, batch_year: int) -> List[Candidate]:
        """Fetch all candidates belonging to a specific batch year."""
        return [c for c in self._students.values() if c.batch_year == batch_year]

    def load_synthetic_dataset(self) -> None:
        """Pre-populate repository with a diverse synthetic campus batch."""
        synthetic_records = [
            # Top CSE candidates
            Candidate(roll_no="23CS01", name="Aarav Sharma", email="aarav.s@college.edu", branch="CSE", cgpa=9.32, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23CS02", name="Diya Sen", email="diya.s@college.edu", branch="CSE", cgpa=8.85, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23CS03", name="Rohan Mehta", email="rohan.m@college.edu", branch="CSE", cgpa=8.10, active_backlogs=0, batch_year=2027),
            # Borderline CSE candidates (Cutoff 8.0)
            Candidate(roll_no="23CS04", name="Kunal Roy", email="kunal.r@college.edu", branch="CSE", cgpa=7.96, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23CS05", name="Neha Gupta", email="neha.g@college.edu", branch="CSE", cgpa=7.92, active_backlogs=0, batch_year=2027),
            # Ineligible CSE (Backlog or low CGPA)
            Candidate(roll_no="23CS06", name="Vikram Das", email="vikram.d@college.edu", branch="CSE", cgpa=8.50, active_backlogs=1, batch_year=2027),
            Candidate(roll_no="23CS07", name="Aditya Nair", email="aditya.n@college.edu", branch="CSE", cgpa=6.70, active_backlogs=0, batch_year=2027),

            # IT Candidates
            Candidate(roll_no="23IT01", name="Ananya Rao", email="ananya.r@college.edu", branch="IT", cgpa=8.90, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23IT02", name="Tanmay Jain", email="tanmay.j@college.edu", branch="IT", cgpa=8.25, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23IT03", name="Ishaan Verma", email="ishaan.v@college.edu", branch="IT", cgpa=7.98, active_backlogs=0, batch_year=2027),

            # ECE Candidates
            Candidate(roll_no="23EC01", name="Sneha Kulkarni", email="sneha.k@college.edu", branch="ECE", cgpa=8.60, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23EC02", name="Priya Patel", email="priya.p@college.edu", branch="ECE", cgpa=8.05, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23EC03", name="Rahul Joshi", email="rahul.j@college.edu", branch="ECE", cgpa=7.40, active_backlogs=0, batch_year=2027),

            # Other Branches (MECH / CIVIL / EE)
            Candidate(roll_no="23ME01", name="Gaurav Singh", email="gaurav.s@college.edu", branch="MECH", cgpa=8.45, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23EE01", name="Varun Iyer", email="varun.i@college.edu", branch="EE", cgpa=8.30, active_backlogs=0, batch_year=2027),
            Candidate(roll_no="23CE01", name="Meera Pillai", email="meera.p@college.edu", branch="CIVIL", cgpa=7.80, active_backlogs=0, batch_year=2027),

            # Different Batch Year (2026 Batch)
            Candidate(roll_no="22CS50", name="Siddharth Rao", email="sid.r@college.edu", branch="CSE", cgpa=9.10, active_backlogs=0, batch_year=2026),
        ]
        for student in synthetic_records:
            self.add_candidate(student)
