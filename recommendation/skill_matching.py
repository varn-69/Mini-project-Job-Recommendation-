"""Candidate-job skill matching and skill scores.

Provides interpretable matching:
- matched / missing skills
- basic skill score  = matched / required * 100
- weighted skill score = sum(weights of matched) / sum(weights of required) * 100
"""

from __future__ import annotations

from typing import Iterable, Mapping

from recommendation.preprocessing import normalize_skill, normalize_skill_list


def get_matched_skills(
    candidate_skills: Iterable[str] | str,
    job_skills: Iterable[str] | str,
) -> list[str]:
    """Return skills required by the job that the candidate has (sorted)."""
    candidate = normalize_skill_list(candidate_skills)
    job = normalize_skill_list(job_skills)
    return sorted(candidate & job)


def get_missing_skills(
    candidate_skills: Iterable[str] | str,
    job_skills: Iterable[str] | str,
) -> list[str]:
    """Return skills required by the job that the candidate lacks (sorted)."""
    candidate = normalize_skill_list(candidate_skills)
    job = normalize_skill_list(job_skills)
    return sorted(job - candidate)


def calculate_basic_skill_score(
    candidate_skills: Iterable[str] | str,
    job_skills: Iterable[str] | str,
) -> float:
    """Percentage of the job's required skills that the candidate has.

    Formula: matched_required_skills / required_skills * 100.

    Returns 0.0 when the job lists no skills (nothing to match against).
    """
    job = normalize_skill_list(job_skills)
    if not job:
        return 0.0
    candidate = normalize_skill_list(candidate_skills)
    return len(candidate & job) / len(job) * 100.0


def calculate_weighted_skill_score(
    candidate_skills: Iterable[str] | str,
    job_skills: Iterable[str] | str,
    skill_weights: Mapping[str, float] | None = None,
) -> float:
    """Skill score where each required skill can carry a different weight.

    Each required skill gets a weight from ``skill_weights`` (default 1.0
    when absent, which makes this equivalent to the basic score). The score
    is the weight of matched skills divided by the total weight of required
    skills, scaled to 0-100.

    Args:
        candidate_skills: Candidate's skills (raw; normalized internally).
        job_skills: Job's required skills.
        skill_weights: Optional map of canonical skill name -> weight.

    Returns:
        Weighted skill score on a 0-100 scale (0.0 if the job has no skills).
    """
    job = normalize_skill_list(job_skills)
    if not job:
        return 0.0
    candidate = normalize_skill_list(candidate_skills)
    weights = {normalize_skill(k): float(v) for k, v in (skill_weights or {}).items()}
    total = sum(weights.get(skill, 1.0) for skill in job)
    if total <= 0:
        return 0.0
    matched = sum(weights.get(skill, 1.0) for skill in job & candidate)
    return matched / total * 100.0
