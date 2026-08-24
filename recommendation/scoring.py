"""Component scores and the final weighted recommendation score.

All scores are on a 0-100 scale and every weight/rule is configurable
so the team can tune the ranking without rewriting the algorithm.
"""

from __future__ import annotations

from typing import Mapping

from recommendation.preprocessing import normalize_text

# Initial example weights from the project design document.
# These are a starting point, NOT a final decision — pass a custom
# mapping to calculate_final_score to experiment.
DEFAULT_WEIGHTS: dict[str, float] = {
    "skill": 0.50,
    "experience": 0.20,
    "location": 0.10,
    "salary": 0.10,
    "education": 0.10,
}

# Ordered education levels used for compatibility scoring (configurable).
DEFAULT_EDUCATION_LEVELS: dict[str, int] = {
    "high school": 1,
    "diploma": 2,
    "bachelor": 3,
    "btech": 3,
    "b.tech": 3,
    "bsc": 3,
    "bca": 3,
    "master": 4,
    "mtech": 4,
    "m.tech": 4,
    "msc": 4,
    "mca": 4,
    "phd": 5,
}


def calculate_experience_score(candidate_experience: float, required_experience: float) -> float:
    """Deterministic experience compatibility score (0-100).

    Rules:
    - Candidate meets or exceeds the requirement -> 100.
    - Candidate is below the requirement -> proportional partial credit:
      ``candidate / required * 100`` (so slightly below gives a high
      partial score and far below gives a low score).
    - Zero-experience jobs require nothing, so any candidate scores 100.
    """
    candidate = max(0.0, float(candidate_experience or 0))
    required = max(0.0, float(required_experience or 0))
    if required == 0 or candidate >= required:
        return 100.0
    return candidate / required * 100.0


def _education_level(text: str, levels: Mapping[str, int]) -> int | None:
    """Best-matching education level found in free text, or None."""
    normalized = normalize_text(text)
    if not normalized:
        return None
    found = [level for keyword, level in levels.items() if keyword in normalized]
    return max(found) if found else None


def calculate_education_score(
    candidate_education: str,
    required_education: str,
    levels: Mapping[str, int] | None = None,
) -> float:
    """Rule-based education compatibility score (0-100).

    - Job states no requirement -> 100.
    - Candidate level >= required level -> 100.
    - Candidate exactly one level below -> 50 (partially compatible).
    - More than one level below, or candidate education unknown -> 20.

    Args:
        levels: Optional keyword -> ordinal level map
            (defaults to DEFAULT_EDUCATION_LEVELS).
    """
    levels = DEFAULT_EDUCATION_LEVELS if levels is None else levels
    required_level = _education_level(required_education, levels)
    if required_level is None:
        return 100.0
    candidate_level = _education_level(candidate_education, levels)
    if candidate_level is None:
        return 20.0
    if candidate_level >= required_level:
        return 100.0
    if required_level - candidate_level == 1:
        return 50.0
    return 20.0


def calculate_location_score(candidate_location: str, job_location: str) -> float:
    """Simple location compatibility score (0-100).

    - Exact (case-insensitive) match -> 100.
    - Remote job, or job with no stated location -> 100.
    - Different location -> 30.
    """
    job = normalize_text(job_location)
    if not job or job == "remote":
        return 100.0
    candidate = normalize_text(candidate_location)
    return 100.0 if candidate == job else 30.0


def calculate_salary_score(salary_preference: float | None, job_salary: float | None) -> float:
    """Salary preference compatibility score (0-100).

    Salary is only an optional preference signal, not a suitability
    predictor. Rules:
    - No candidate preference or unknown job salary -> neutral 100.
    - Job salary >= preference -> 100.
    - Job salary below preference -> proportional: salary / preference * 100.
    """
    if salary_preference is None or salary_preference <= 0 or job_salary is None:
        return 100.0
    if job_salary >= salary_preference:
        return 100.0
    return max(0.0, job_salary / salary_preference * 100.0)


def validate_weights(weights: Mapping[str, float]) -> None:
    """Ensure weights cover the expected components and sum to 1.0.

    Raises:
        ValueError: On unknown/missing components, negative weights,
            or a sum that is not 1.0 (within a small tolerance).
    """
    expected = set(DEFAULT_WEIGHTS)
    if set(weights) != expected:
        raise ValueError(f"weights must have exactly these keys: {sorted(expected)}")
    if any(w < 0 for w in weights.values()):
        raise ValueError("weights must be non-negative")
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"weights must sum to 1.0 (got {total})")


def calculate_final_score(
    component_scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
) -> float:
    """Weighted combination of component scores on a 0-100 scale.

    Args:
        component_scores: Map with keys "skill", "experience", "location",
            "salary", "education" (each 0-100).
        weights: Optional weight map (defaults to DEFAULT_WEIGHTS);
            validated to sum to 1.0.

    Returns:
        Final score rounded to 2 decimal places.
    """
    weights = DEFAULT_WEIGHTS if weights is None else weights
    validate_weights(weights)
    missing = [k for k in weights if k not in component_scores]
    if missing:
        raise ValueError(f"component_scores missing components: {missing}")
    final = sum(weights[k] * float(component_scores[k]) for k in weights)
    return round(final, 2)
