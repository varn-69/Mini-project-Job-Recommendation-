import json
import os

import pytest

from recommendation.preprocessing import load_jobs_csv
from recommendation.recommender import recommend_jobs

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.csv")

CANDIDATE = {
    "skills": ["Python", "SQL", "Pandas"],
    "education": "BTech CSE",
    "experience": 0,
    "location": "Delhi",
    "salary_preference": 500000,
}


def _make_jobs(n: int) -> list[dict]:
    return [
        {
            "job_id": f"J{i:03d}",
            "job_title": f"Job {i}",
            "skills": ["Python"],
            "experience_required": 0,
            "education_required": "Bachelor",
            "location": "Delhi",
            "salary": 500000,
            "description": "python role",
        }
        for i in range(1, n + 1)
    ]


def test_top_n_limits_results():
    results = recommend_jobs(CANDIDATE, _make_jobs(10), top_n=5)
    assert len(results) == 5


def test_best_matching_job_ranks_first():
    jobs = [
        {
            "job_id": "GOOD",
            "job_title": "Data Analyst",
            "skills": ["Python", "SQL", "Pandas"],
            "experience_required": 0,
            "education_required": "Bachelor",
            "location": "Delhi",
            "salary": 500000,
            "description": "Analyze data using Python, SQL and pandas.",
        },
        {
            "job_id": "BAD",
            "job_title": "Frontend Developer",
            "skills": ["JavaScript", "React", "CSS"],
            "experience_required": 3,
            "education_required": "Bachelor",
            "location": "Mumbai",
            "salary": 300000,
            "description": "Build UIs with React and CSS.",
        },
    ]
    results = recommend_jobs(CANDIDATE, jobs, top_n=2)
    assert results[0]["job_id"] == "GOOD"
    assert results[0]["final_score"] > results[1]["final_score"]


def test_result_structure_and_skill_gap():
    jobs = [
        {
            "job_id": "J001",
            "job_title": "Data Analyst",
            "skills": ["Python", "SQL", "Excel", "Power BI"],
            "experience_required": 0,
            "education_required": "Bachelor",
            "location": "Delhi",
            "salary": 500000,
            "description": "Analyze data.",
        }
    ]
    result = recommend_jobs(CANDIDATE, jobs, top_n=1)[0]
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["excel", "power bi"]
    assert set(result["component_scores"]) == {
        "skill",
        "similarity",
        "experience",
        "education",
        "location",
        "salary",
    }


def test_results_are_json_friendly():
    results = recommend_jobs(CANDIDATE, load_jobs_csv(DATA_PATH), top_n=5)
    # Raises TypeError if any numpy/pandas types leak through.
    json.dumps(results)


def test_invalid_top_n():
    with pytest.raises(ValueError, match="top_n"):
        recommend_jobs(CANDIDATE, _make_jobs(3), top_n=0)


def test_deterministic_tie_break_by_title():
    jobs = _make_jobs(3)
    for i, title in enumerate(["Charlie", "Alpha", "Bravo"]):
        jobs[i]["job_title"] = title
    results = recommend_jobs(CANDIDATE, jobs, top_n=3)
    assert [r["job_title"] for r in results] == ["Alpha", "Bravo", "Charlie"]


def test_regression_ranking_on_demo_dataset():
    """Known candidate + demo dataset: ranking must not silently change."""
    results = recommend_jobs(CANDIDATE, load_jobs_csv(DATA_PATH), top_n=5)
    assert [r["job_id"] for r in results] == ["J001", "J010", "J004", "J002", "J005"]
