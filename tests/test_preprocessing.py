import pandas as pd
import pytest

from recommendation.preprocessing import (
    REQUIRED_COLUMNS,
    load_jobs_csv,
    normalize_skill,
    normalize_skill_list,
    normalize_text,
)


def test_normalize_text_lowercases_and_trims():
    assert normalize_text("  Hello   World  ") == "hello world"
    assert normalize_text("") == ""


def test_normalize_skill_variants():
    assert normalize_skill(" Python ") == "python"
    assert normalize_skill("PYTHON") == "python"
    assert normalize_skill("python programming") == "python"
    assert normalize_skill("py") == "python"
    assert normalize_skill("ml") == "machine learning"
    assert normalize_skill("js") == "javascript"


def test_normalize_skill_custom_aliases():
    assert normalize_skill("pyt", aliases={"pyt": "python"}) == "python"


def test_normalize_skill_list_from_string_and_dedup():
    assert normalize_skill_list("Python, SQL , python, PY") == {"python", "sql"}


def test_normalize_skill_list_drops_empty():
    assert normalize_skill_list(["", "  ", "SQL"]) == {"sql"}


def _write_csv(path, rows):
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(path, index=False)


def test_load_jobs_csv_handles_missing_values(tmp_path):
    path = tmp_path / "jobs.csv"
    _write_csv(
        path,
        [
            {
                "job_id": "J001",
                "job_title": "Data Analyst",
                "skills": "Python, SQL",
                "experience_required": None,
                "education_required": None,
                "location": None,
                "salary": None,
                "description": None,
            }
        ],
    )
    jobs = load_jobs_csv(str(path))
    assert len(jobs) == 1
    job = jobs[0]
    assert job.experience_required == 0
    assert job.salary is None
    assert job.description == ""
    assert job.location == ""


def test_load_jobs_csv_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame([{"job_id": "J001"}]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_jobs_csv(str(path))
