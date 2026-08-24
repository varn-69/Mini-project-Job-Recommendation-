"""Dataset loading, cleaning and skill normalization.

Responsibilities:
- Load the jobs CSV with pandas and validate required columns.
- Handle missing values sensibly.
- Normalize free text and skill names (lowercase, trimmed, alias-mapped).
"""

from __future__ import annotations

import re
from typing import Iterable, Mapping

import pandas as pd

from recommendation.models import Job

REQUIRED_COLUMNS: tuple[str, ...] = (
    "job_id",
    "job_title",
    "skills",
    "experience_required",
    "education_required",
    "location",
    "salary",
    "description",
)

# Configurable alias map: variant -> canonical skill name.
# Extend this dictionary (or pass a custom one) to handle more variations.
DEFAULT_SKILL_ALIASES: dict[str, str] = {
    "py": "python",
    "python programming": "python",
    "python3": "python",
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "dl": "deep learning",
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "powerbi": "power bi",
    "nlp": "natural language processing",
    "aws cloud": "aws",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "ci-cd": "ci/cd",
    "cicd": "ci/cd",
}

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase a string and collapse internal whitespace."""
    if not isinstance(text, str):
        return ""
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def normalize_skill(skill: str, aliases: Mapping[str, str] | None = None) -> str:
    """Normalize a single skill name.

    Trims whitespace, lowercases, collapses internal whitespace and maps
    known aliases (e.g. "py" -> "python") to a canonical name.

    Args:
        skill: Raw skill string.
        aliases: Optional alias map; defaults to DEFAULT_SKILL_ALIASES.

    Returns:
        The canonical, lowercase skill name ("" for empty input).
    """
    aliases = DEFAULT_SKILL_ALIASES if aliases is None else aliases
    cleaned = normalize_text(skill)
    return aliases.get(cleaned, cleaned)


def normalize_skill_list(
    skills: Iterable[str] | str,
    aliases: Mapping[str, str] | None = None,
) -> set[str]:
    """Normalize a collection of skills into a deduplicated set.

    Accepts either an iterable of skill strings or a single
    comma-separated string ("Python, SQL, Pandas").

    Args:
        skills: Skills to normalize.
        aliases: Optional alias map; defaults to DEFAULT_SKILL_ALIASES.

    Returns:
        Set of canonical skill names with empty entries removed.
    """
    if isinstance(skills, str):
        skills = skills.split(",")
    normalized = {normalize_skill(s, aliases) for s in skills}
    normalized.discard("")
    return normalized


def load_jobs_csv(path: str) -> list[Job]:
    """Load and clean a jobs dataset from a CSV file.

    Validates that all required columns are present, fills missing
    values with sensible defaults, and returns a list of Job objects.

    Args:
        path: Path to the CSV file.

    Returns:
        List of Job records.

    Raises:
        ValueError: If required columns are missing or the file is empty.
    """
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"jobs CSV is missing required columns: {missing}")
    if df.empty:
        raise ValueError("jobs CSV contains no rows")

    df = df.copy()
    for col in ("job_title", "skills", "education_required", "location", "description"):
        df[col] = df[col].fillna("")
    df["experience_required"] = pd.to_numeric(df["experience_required"], errors="coerce").fillna(0)
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

    jobs: list[Job] = []
    for row in df.to_dict(orient="records"):
        if pd.isna(row["salary"]):
            row["salary"] = None
        jobs.append(Job.from_dict(row))
    return jobs
