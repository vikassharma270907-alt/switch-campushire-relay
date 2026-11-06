"""Skill Gap & Hands-on Project Recommendation Engine.

Bridges student skill deficiencies identified during placement audits with curated,
hands-on open source projects from the external_500_ai_projects repository.
"""
from __future__ import annotations
import os
import re
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_README = os.path.join(PROJECT_ROOT, "external_500_ai_projects", "README.md")

# Default curated fallback projects across core domains
CURATED_FALLBACK_PROJECTS: List[Dict[str, str]] = [
    {
        "sr": "1",
        "name": "365 Days Computer Vision Learning",
        "link": "https://github.com/ashishpatel26/365-Days-Computer-Vision-Learning-Linkedin-Post",
        "domain": "computer vision",
    },
    {
        "sr": "2",
        "name": "125+ NLP Language Models Treasure of Transformers",
        "link": "https://github.com/ashishpatel26/Treasure-of-Transformers",
        "domain": "nlp",
    },
    {
        "sr": "4",
        "name": "10 Machine Learning Projects on Time Series Forecasting",
        "link": "https://medium.com/coders-camp/10-machine-learning-projects-on-time-series-forecasting-ee0368420ccd",
        "domain": "time series",
    },
    {
        "sr": "5",
        "name": "20 Deep Learning Projects Solved and Explained with Python",
        "link": "https://thecleverprogrammer.com/2020/11/22/deep-learning-projects-with-python/",
        "domain": "deep learning",
    },
    {
        "sr": "7",
        "name": "30 Python Project Solved and Explained",
        "link": "https://amankharwal.medium.com/30-python-projects-solved-and-explained-563fd7473003",
        "domain": "python",
    },
    {
        "sr": "11",
        "name": "4 Chatbot Project With Python",
        "link": "https://amankharwal.medium.com/4-chatbot-projects-with-python-5b32fd84af37",
        "domain": "chatbots",
    },
    {
        "sr": "14",
        "name": "10 Machine learning Projects for Regression Analysis",
        "link": "https://amankharwal.medium.com/10-machine-learning-projects-on-regression-with-python-e5494615a0d0",
        "domain": "machine learning",
    },
    {
        "sr": "15",
        "name": "10 Machine learning Project for Classification with Python",
        "link": "https://medium.datadriveninvestor.com/10-machine-learning-projects-on-classification-with-python-9261add2e8a7",
        "domain": "classification",
    },
    {
        "sr": "16",
        "name": "6 Sentimental Analysis Projects with python",
        "link": "https://amankharwal.medium.com/6-sentiment-analysis-projects-with-python-1fdd3d43d90f",
        "domain": "nlp",
    },
    {
        "sr": "31",
        "name": "27 Django Projects with Source Code",
        "link": "https://data-flair.training/blogs/django-project-ideas/",
        "domain": "web development",
    },
    {
        "sr": "44",
        "name": "100 + Production Machine learning Projects",
        "link": "https://github.com/EthicalML/awesome-production-machine-learning",
        "domain": "mlops",
    },
    {
        "sr": "51",
        "name": "Awesome Chatbot Projects",
        "link": "https://github.com/fendouai/Awesome-Chatbot",
        "domain": "chatbots",
    },
]

SKILL_TO_DOMAIN_MAP: Dict[str, List[str]] = {
    "nlp": ["nlp", "transformers", "language models", "sentiment", "text"],
    "computer vision": ["computer vision", "vision", "opencv", "image", "video"],
    "deep learning": ["deep learning", "neural network", "pytorch", "tensorflow"],
    "machine learning": ["machine learning", "regression", "classification", "automl"],
    "python": ["python", "django", "fastapi", "flask"],
    "chatbots": ["chatbot", "conversational", "dialogue"],
    "time series": ["time series", "forecasting", "predictive"],
    "data structures": ["python", "machine learning"],
    "algorithms": ["machine learning", "deep learning"],
    "sql": ["database", "python", "data science"],
    "system design": ["production", "mlops", "django", "web development"],
    "distributed systems": ["production", "mlops"],
}


class SkillGapProjectEngine:
    """Indexes and recommends concrete open-source projects to eliminate skill gaps."""

    def __init__(self, readme_path: str = PROJECTS_README):
        self.readme_path = readme_path
        self._projects_catalog: List[Dict[str, str]] = []
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Parses the 500 AI projects markdown table."""
        if not os.path.exists(self.readme_path):
            self._projects_catalog = list(CURATED_FALLBACK_PROJECTS)
            return

        projects = []
        try:
            with open(self.readme_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            row_pattern = re.compile(r"\|\s*(\d+[\.]?)\s*\|\s*([^|]+)\s*\|\s*\[[^\]]*\]\((https?://[^)]+)\)\s*\|")
            for match in row_pattern.finditer(content):
                sr, name, link = match.groups()
                clean_name = name.strip()
                projects.append({
                    "sr": sr.strip("."),
                    "name": clean_name,
                    "link": link.strip(),
                    "domain": self._infer_domain(clean_name),
                })
        except Exception:
            projects = []

        self._projects_catalog = projects if len(projects) >= 5 else list(CURATED_FALLBACK_PROJECTS)

    def _infer_domain(self, title: str) -> str:
        """Infers the core domain tag from a project title."""
        t = title.lower()
        if any(k in t for k in ["nlp", "transformer", "sentence", "text", "sentiment"]):
            return "nlp"
        if any(k in t for k in ["computer vision", "vision", "opencv", "image"]):
            return "computer vision"
        if any(k in t for k in ["deep learning", "neural network", "coreml"]):
            return "deep learning"
        if any(k in t for k in ["time series", "forecasting"]):
            return "time series"
        if any(k in t for k in ["chatbot"]):
            return "chatbots"
        if any(k in t for k in ["django", "web", "gui"]):
            return "web development"
        if any(k in t for k in ["production", "automl", "mlops"]):
            return "mlops"
        return "machine learning"

    def recommend_for_skills(
        self,
        missing_skills: List[str],
        limit_per_skill: int = 2
    ) -> List[Dict[str, Any]]:
        """Recommends specific projects targeting candidate's missing skills."""
        recommendations: List[Dict[str, Any]] = []
        seen_links = set()

        for skill in missing_skills:
            normalized_skill = skill.lower().strip()
            keywords = SKILL_TO_DOMAIN_MAP.get(normalized_skill, [normalized_skill])

            matches = []
            for p in self._projects_catalog:
                if p["link"] in seen_links:
                    continue
                name_lower = p["name"].lower()
                domain_lower = p["domain"].lower()

                if any(kw in name_lower or kw in domain_lower for kw in keywords):
                    matches.append(p)
                    if len(matches) >= limit_per_skill:
                        break

            # Fallback if specific search gave zero results
            if not matches and self._projects_catalog:
                fallback = self._projects_catalog[len(recommendations) % len(self._projects_catalog)]
                if fallback["link"] not in seen_links:
                    matches.append(fallback)

            for match in matches:
                seen_links.add(match["link"])
                recommendations.append({
                    "skill_addressed": skill,
                    "project_title": match["name"],
                    "project_url": match["link"],
                    "domain": match["domain"],
                    "estimated_effort": "3-Day Sprint (15 Hours)",
                    "difficulty": "Intermediate",
                    "action_item": f"Complete hands-on implementation of '{match['name']}' to showcase on GitHub and resume.",
                })

        return recommendations


PROJECT_ENGINE = SkillGapProjectEngine()
