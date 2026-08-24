"""Typed data models for candidates and jobs.

These dataclasses are the internal representation used by the
recommendation engine. They can be built from plain dictionaries
(JSON-friendly), which keeps the module easy to integrate with a
FastAPI backend later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass
class Candidate:
    """A candidate profile.

    Attributes:
        skills: Raw skill names (normalization happens in preprocessing).
        education: Free-text education, e.g. "BTech CSE".
        experience: Years of professional experience.
        location: Preferred / current location.
        salary_preference: Desired annual salary (same currency/units as jobs),
            or None if the candidate has no preference.
    """

    skills: list[str] = field(default_factory=list)
    education: str = ""
    experience: float = 0.0
    location: str = ""
    salary_preference: float | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Candidate":
        """Build a Candidate from a plain dictionary.

        Raises:
            ValueError: If ``skills`` is present but not a sequence of strings.
        """
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [s for s in skills.split(",")]
        elif not isinstance(skills, Sequence):
            raise ValueError("candidate 'skills' must be a list or comma-separated string")
        experience = data.get("experience", 0) or 0
        salary = data.get("salary_preference")
        return cls(
            skills=[str(s) for s in skills],
            education=str(data.get("education", "") or ""),
            experience=float(experience),
            location=str(data.get("location", "") or ""),
            salary_preference=float(salary) if salary is not None else None,
        )


@dataclass
class Job:
    """A job posting.

    Attributes:
        job_id: Unique identifier, e.g. "J001".
        job_title: Human-readable title.
        skills: Raw required skill names.
        experience_required: Minimum years of experience.
        education_required: Required education level, e.g. "Bachelor".
        location: Job location ("Remote" is treated specially).
        salary: Offered annual salary, or None if unknown.
        description: Free-text job description (used for TF-IDF similarity).
    """

    job_id: str
    job_title: str
    skills: list[str] = field(default_factory=list)
    experience_required: float = 0.0
    education_required: str = ""
    location: str = ""
    salary: float | None = None
    description: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Job":
        """Build a Job from a plain dictionary (e.g. a CSV row).

        Raises:
            ValueError: If ``job_id`` is missing.
        """
        job_id = data.get("job_id")
        if job_id is None or str(job_id).strip() == "":
            raise ValueError("job record is missing required field 'job_id'")
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = skills.split(",")
        experience = data.get("experience_required", 0) or 0
        salary = data.get("salary")
        return cls(
            job_id=str(job_id),
            job_title=str(data.get("job_title", "") or ""),
            skills=[str(s) for s in skills],
            experience_required=float(experience),
            education_required=str(data.get("education_required", "") or ""),
            location=str(data.get("location", "") or ""),
            salary=float(salary) if salary is not None and str(salary).strip() != "" else None,
            description=str(data.get("description", "") or ""),
        )
