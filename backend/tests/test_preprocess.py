import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.ml.preprocess import normalize_skill, parse_skills, clean_text, preprocess_job_data


def test_normalize_skill():
    """Test skill normalization."""
    assert normalize_skill("JS") == "javascript"
    assert normalize_skill("ReactJS") == "react"
    assert normalize_skill("Postgres") == "postgresql"
    assert normalize_skill("Python") == "python"
    assert normalize_skill("") == ""
    assert normalize_skill(None) == ""


def test_parse_skills():
    """Test skill parsing."""
    skills = parse_skills("Python, SQL, Pandas, Git")
    assert "python" in skills
    assert "sql" in skills
    assert "pandas" in skills
    assert "git" in skills

    # Test with skill aliases
    skills = parse_skills("JS, ReactJS, Postgres")
    assert "javascript" in skills
    assert "react" in skills
    assert "postgresql" in skills

    # Test empty input
    assert parse_skills("") == []
    assert parse_skills(None) == []


def test_clean_text():
    """Test text cleaning."""
    assert clean_text("  Hello  World  ") == "Hello World"
    assert clean_text("Hello, World!") == "Hello, World!"
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_preprocess_job_data():
    """Test job data preprocessing."""
    # Create sample data
    data = {
        'job_id': [1, 2],
        'job_title': ['Python Developer', '  React Developer  '],
        'company': ['TechCorp', 'WebSolutions'],
        'skills': ['Python, Django, Git', 'React, JavaScript, CSS'],
        'experience_required': [2, 1],
        'salary_min': [600000, 500000],
        'salary_max': [1200000, 900000],
        'location': ['Bangalore', 'Noida'],
        'education': ['B.Tech Computer Science', 'B.Tech/B.E. Computer Science'],
        'description': ['Develop web applications', 'Build user interfaces']
    }

    df = pd.DataFrame(data)
    df_processed = preprocess_job_data(df)

    # Check that skills are parsed
    assert isinstance(df_processed.iloc[0]['skills'], list)
    assert 'python' in df_processed.iloc[0]['skills']

    # Check that text is cleaned
    assert df_processed.iloc[1]['job_title'] == 'React Developer'

    # Check that numeric fields are numeric
    assert df_processed.iloc[0]['experience_required'] == 2.0
    assert df_processed.iloc[0]['salary_min'] == 600000.0
