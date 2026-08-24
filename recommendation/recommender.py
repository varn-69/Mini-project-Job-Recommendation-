"""Top-level recommendation engine.

Public interface for the backend developer:

    from recommendation.recommender import recommend_jobs

    results = recommend_jobs(candidate=candidate, jobs=jobs, top_n=5)

Both ``candidate`` and each job may be a plain dict (JSON-friendly) or a
Candidate/Job dataclass. Results are plain Python types (str, float,
list, dict) so they serialize directly to JSON.

Note: the TF-IDF similarity score is reported in ``component_scores``
for explainability but is intentionally not part of the final weighted
score, whose weights (skill/experience/location/salary/education) come
from the project design document. Adding similarity as a weighted
component only requires extending the weights map in ``scoring.py``.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from recommendation.models import Candidate, Job
from recommendation.preprocessing import normalize_skill_list
from recommendation.scoring import (
    calculate_education_score,
    calculate_experience_score,
    calculate_final_score,
    calculate_location_score,
    calculate_salary_score,
)
from recommendation.similarity import calculate_text_similarity_batch
from recommendation.skill_matching import (
    calculate_basic_skill_score,
    calculate_weighted_skill_score,
)


def _as_candidate(candidate: Candidate | Mapping[str, Any]) -> Candidate:
    if isinstance(candidate, Candidate):
        return candidate
    if isinstance(candidate, Mapping):
        return Candidate.from_dict(candidate)
    raise ValueError("candidate must be a Candidate or a dict")


def _as_job(job: Job | Mapping[str, Any]) -> Job:
    if isinstance(job, Job):
        return job
    if isinstance(job, Mapping):
        return Job.from_dict(job)
    raise ValueError("each job must be a Job or a dict")


def _candidate_profile_text(candidate: Candidate) -> str:
    """Free-text representation of the candidate for TF-IDF comparison."""
    parts = [", ".join(candidate.skills), candidate.education, candidate.location]
    return " ".join(p for p in parts if p)


def recommend_jobs(
    candidate: Candidate | Mapping[str, Any],
    jobs: Sequence[Job | Mapping[str, Any]],
    top_n: int = 5,
    weights: Mapping[str, float] | None = None,
    skill_weights: Mapping[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Rank jobs for a candidate and return the top-N recommendations.

    Pipeline per job: normalize skills -> matched/missing skills ->
    skill score (weighted if ``skill_weights`` given) -> TF-IDF text
    similarity -> experience/education/location/salary scores ->
    final weighted score -> deterministic sort -> top-N.

    Args:
        candidate: Candidate profile (dict or Candidate).
        jobs: Job records (dicts or Job objects).
        top_n: Maximum number of recommendations to return.
        weights: Optional final-score weights (see scoring.DEFAULT_WEIGHTS).
        skill_weights: Optional per-skill importance weights.

    Returns:
        JSON-friendly list of result dicts sorted by final_score
        descending, with ties broken by number of matched skills
        (descending) then job title.

    Raises:
        ValueError: On invalid candidate/job data, invalid weights,
            or non-positive ``top_n``.
    """
    if top_n <= 0:
        raise ValueError("top_n must be a positive integer")
    cand = _as_candidate(candidate)
    job_objs = [_as_job(j) for j in jobs]

    candidate_skills = normalize_skill_list(cand.skills)
    candidate_text = _candidate_profile_text(cand)
    similarity_scores = calculate_text_similarity_batch(
        candidate_text, [job.description for job in job_objs]
    )

    results: list[dict[str, Any]] = []
    for job, similarity in zip(job_objs, similarity_scores):
        job_skills = normalize_skill_list(job.skills)
        matched = sorted(candidate_skills & job_skills)
        missing = sorted(job_skills - candidate_skills)
        if skill_weights is not None:
            skill_score = calculate_weighted_skill_score(
                candidate_skills, job_skills, skill_weights
            )
        else:
            skill_score = calculate_basic_skill_score(candidate_skills, job_skills)

        component_scores = {
            "skill": round(skill_score, 2),
            "similarity": round(similarity, 2),
            "experience": round(
                calculate_experience_score(cand.experience, job.experience_required), 2
            ),
            "education": round(
                calculate_education_score(cand.education, job.education_required), 2
            ),
            "location": round(calculate_location_score(cand.location, job.location), 2),
            "salary": round(calculate_salary_score(cand.salary_preference, job.salary), 2),
        }
        final_score = calculate_final_score(
            {k: component_scores[k] for k in ("skill", "experience", "location", "salary", "education")},
            weights,
        )
        results.append(
            {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "final_score": final_score,
                "component_scores": component_scores,
                "matched_skills": matched,
                "missing_skills": missing,
            }
        )

    results.sort(
        key=lambda r: (-r["final_score"], -len(r["matched_skills"]), r["job_title"], r["job_id"])
    )
    return results[:top_n]
