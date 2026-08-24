import pytest

from recommendation.skill_matching import (
    calculate_basic_skill_score,
    calculate_weighted_skill_score,
    get_matched_skills,
    get_missing_skills,
)


def test_matched_and_missing():
    candidate = ["Python", "SQL"]
    job = ["Python", "SQL", "Excel"]
    assert get_matched_skills(candidate, job) == ["python", "sql"]
    assert get_missing_skills(candidate, job) == ["excel"]


def test_matching_uses_normalization_and_aliases():
    assert get_matched_skills(["PY", " sql "], ["Python", "SQL"]) == ["python", "sql"]


def test_matching_handles_duplicates():
    assert get_matched_skills(["python", "Python", "PYTHON"], ["python"]) == ["python"]


def test_basic_skill_score_value():
    score = calculate_basic_skill_score(["Python", "SQL", "Pandas"], ["Python", "SQL", "Pandas", "Excel", "Power BI"])
    assert score == pytest.approx(60.0)


def test_basic_skill_score_no_job_skills():
    assert calculate_basic_skill_score(["python"], []) == 0.0


def test_weighted_skill_score_reflects_importance():
    weights = {"python": 0.30, "machine learning": 0.30, "tensorflow": 0.25, "git": 0.15}
    job = ["python", "machine learning", "tensorflow", "git"]
    # Candidate with the two heavy skills beats one with two light skills.
    heavy = calculate_weighted_skill_score(["python", "machine learning"], job, weights)
    light = calculate_weighted_skill_score(["tensorflow", "git"], job, weights)
    assert heavy == pytest.approx(60.0)
    assert light == pytest.approx(40.0)
    assert heavy > light


def test_weighted_skill_score_defaults_to_basic():
    candidate = ["python"]
    job = ["python", "sql"]
    assert calculate_weighted_skill_score(candidate, job) == pytest.approx(
        calculate_basic_skill_score(candidate, job)
    )
