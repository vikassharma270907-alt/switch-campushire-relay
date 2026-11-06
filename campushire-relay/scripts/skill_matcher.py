#!/usr/bin/env python3
"""
Semantic Skill Matcher & Gap Analysis Engine for CampusHire Relay.
Adapted from NLP Sentence Embeddings & Recommendation Systems (500+ AI Projects).

Analyzes student skill profiles against recruiter job requirements, computes
readiness match indices, isolates skill gaps, and synthesizes personalized
multi-day preparation roadmaps for Track 02 (#student-prep-studio).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Default canonical skill mappings by engineering branch (extensible via student profiles)
BRANCH_CANONICAL_SKILLS: Dict[str, List[str]] = {
    "CSE": [
        "python", "data structures", "algorithms", "sql", "git",
        "object-oriented programming", "operating systems", "computer networks"
    ],
    "IT": [
        "python", "rest apis", "sql", "web development", "git",
        "database management", "cloud fundamentals", "data structures"
    ],
    "ECE": [
        "c++", "embedded systems", "microcontrollers", "python",
        "digital signal processing", "git", "computer architecture"
    ],
    "ME": [
        "solidworks", "cad", "matlab", "thermodynamics", "python basics", "mechanics"
    ],
}

# Default target skills for Graduate Engineer Trainee roles
DEFAULT_ROLE_SKILLS: Dict[str, List[str]] = {
    "graduate engineer trainee": [
        "python", "data structures", "algorithms", "sql", "rest apis", "git", "system design"
    ],
    "software engineer": [
        "python", "algorithms", "data structures", "sql", "rest apis", "docker", "system design", "git"
    ],
    "data engineer": [
        "python", "sql", "database management", "pandas", "data structures", "etl pipelines", "git"
    ],
}


def normalize_skill(skill: str) -> str:
    """Normalize skill string for resilient token matching."""
    s = skill.lower().replace("&", "#").strip()
    return re.sub(r"[^a-z0-9+#]", "", s)


def extract_skills_from_text(text: str) -> List[str]:
    """Scan recruiter notice or curriculum text for software engineering skill keywords."""
    catalog = {
        "python", "c++", "java", "sql", "rest apis", "data structures", "algorithms",
        "system design", "git", "docker", "web development", "cloud fundamentals",
        "operating systems", "computer networks", "database management", "microservices"
    }
    lower = text.lower()
    found = []
    for skill in catalog:
        if skill in lower:
            found.append(skill)
    return sorted(found)


def compute_skill_overlap(
    candidate_skills: List[str],
    job_skills: List[str],
) -> Dict[str, Any]:
    """Calculate Jaccard and containment match indices, matched skills, and gaps."""
    cand_norm = {normalize_skill(s): s for s in candidate_skills}
    job_norm = {normalize_skill(s): s for s in job_skills}

    cand_keys = set(cand_norm.keys())
    job_keys = set(job_norm.keys())

    if not job_keys:
        return {
            "match_score": 100.0,
            "matched_skills": list(candidate_skills),
            "missing_skills": [],
            "coverage_ratio": 1.0,
        }

    intersection = cand_keys.intersection(job_keys)
    missing = job_keys - cand_keys

    # Containment score: percentage of job requirements candidate fulfills
    coverage = len(intersection) / float(len(job_keys))
    # Jaccard index
    union = cand_keys.union(job_keys)
    jaccard = len(intersection) / float(len(union)) if union else 1.0

    # Composite readiness score (70% coverage weight + 30% Jaccard)
    readiness = round((0.70 * coverage + 0.30 * jaccard) * 100.0, 1)

    return {
        "match_score": readiness,
        "matched_skills": sorted([job_norm[k] for k in intersection]),
        "missing_skills": sorted([job_norm[k] for k in missing]),
        "coverage_ratio": round(coverage, 3),
    }


def synthesize_gap_roadmap(
    student_id: str,
    branch: str,
    match_result: Dict[str, Any],
    stages: List[str],
) -> str:
    """Generate a high-yield 3-day targeted sprint roadmap addressing specific skill gaps."""
    score = match_result["match_score"]
    matched = ", ".join(f"`{s}`" for s in match_result["matched_skills"]) or "None identified"
    missing = match_result["missing_skills"]

    roadmap = f"""### Skill Readiness Audit: {score}% Match
- **Verified Competencies:** {matched}
- **Critical Skill Gaps:** {", ".join(f"`{s}`" for s in missing) if missing else "None (Full baseline coverage)"}

#### 🎯 3-Day Rapid Gap-Closing Sprint
"""
    if not missing:
        roadmap += """- **Day 1 (Core Drills):** Speed-run 5 timed LeetCode medium questions on Arrays, HashMaps, and Trees.
- **Day 2 (System Design):** Review architectural trade-offs: SQL vs NoSQL, Caching strategies, and REST API conventions.
- **Day 3 (Mock Execution):** Conduct two 20-minute voice STAR behavioral drills using Wispr Flow.
"""
    else:
        roadmap += f"""- **Day 1 (Gap Remediation):** Deep-dive into primary missing skill: **{missing[0].upper()}**. Complete hands-on coding exercises.
"""
        if len(missing) > 1:
            roadmap += f"- **Day 2 (Secondary Gaps):** Review **{', '.join(missing[1:]).upper()}** fundamentals and common placement interview questions.\n"
        else:
            roadmap += "- **Day 2 (Integration):** Combine core skills into a mini end-to-end architecture walkthrough.\n"
        roadmap += "- **Day 3 (Live Simulation):** Practice spoken STAR explanations of project challenges via Wispr Flow in `#student-prep-studio`.\n"

    return roadmap


def evaluate_student_skills(
    student_id: str,
    branch: str,
    role: str = "Graduate Engineer Trainee",
    custom_job_skills: List[str] | None = None,
    custom_student_skills: List[str] | None = None,
) -> Dict[str, Any]:
    """Top-level evaluation pipeline for a candidate."""
    cand_skills = custom_student_skills or BRANCH_CANONICAL_SKILLS.get(branch.upper(), ["problem solving", "python"])
    job_skills = custom_job_skills or DEFAULT_ROLE_SKILLS.get(role.lower(), DEFAULT_ROLE_SKILLS["graduate engineer trainee"])

    overlap = compute_skill_overlap(cand_skills, job_skills)
    roadmap = synthesize_gap_roadmap(
        student_id=student_id,
        branch=branch,
        match_result=overlap,
        stages=["Online Test", "Technical Interview", "HR Interview"],
    )

    return {
        "student_id": student_id,
        "branch": branch,
        "role": role,
        "match_score": overlap["match_score"],
        "coverage_ratio": overlap["coverage_ratio"],
        "matched_skills": overlap["matched_skills"],
        "missing_skills": overlap["missing_skills"],
        "roadmap_markdown": roadmap,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/skill_matcher.py <student_id> <branch> [role]")
        sys.exit(1)

    sid = sys.argv[1]
    br = sys.argv[2]
    rl = sys.argv[3] if len(sys.argv) >= 4 else "Graduate Engineer Trainee"

    res = evaluate_student_skills(sid, br, rl)
    print(json.dumps(res, indent=2))
    print("\n--- ROADMAP PREVIEW ---")
    print(res["roadmap_markdown"])
