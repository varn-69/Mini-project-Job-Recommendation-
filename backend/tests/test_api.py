import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data


def test_get_jobs_endpoint():
    """Test get jobs endpoint."""
    response = client.get("/api/jobs")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check that job has required fields
    job = data[0]
    assert "job_id" in job
    assert "job_title" in job
    assert "company" in job
    assert "skills" in job


def test_recommend_endpoint():
    """Test recommendation endpoint."""
    candidate = {
        "name": "Test Candidate",
        "skills": "Python, SQL, Pandas, Git",
        "education": "B.Tech Computer Science",
        "experience": 0,
        "location": "Noida",
        "expected_salary": 500000
    }

    response = client.post("/api/recommend", json={"candidate": candidate})
    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data
    assert "candidate_name" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0

    # Check that recommendation has required fields
    rec = data["recommendations"][0]
    assert "job_id" in rec
    assert "job_title" in rec
    assert "final_score" in rec
    assert "matched_skills" in rec
    assert "missing_skills" in rec


def test_recommend_endpoint_invalid_data():
    """Test recommendation endpoint with invalid data."""
    candidate = {
        "name": "Test",
        # Missing required fields
    }

    response = client.post("/api/recommend", json={"candidate": candidate})
    assert response.status_code == 422  # Validation error


def test_explain_endpoint():
    """Test explanation endpoint."""
    candidate = {
        "name": "Test Candidate",
        "skills": "Python, SQL, Pandas, Git",
        "education": "B.Tech Computer Science",
        "experience": 0,
        "location": "Noida",
        "expected_salary": 500000
    }

    job = {
        "job_id": 1,
        "job_title": "Python Developer",
        "company": "TechCorp",
        "location": "Bangalore",
        "salary_min": 600000,
        "salary_max": 1200000,
        "experience_required": 2,
        "education": "B.Tech Computer Science",
        "description": "Develop web applications",
        "skills": ["python", "django", "git"],
        "final_score": 0.75,
        "skill_score": 0.8,
        "experience_score": 0.5,
        "location_score": 0.3,
        "salary_score": 1.0,
        "education_score": 1.0,
        "matched_skills": ["python", "git"],
        "missing_skills": ["django"],
        "tfidf_similarity": 0.6
    }

    response = client.post("/api/explain", json={
        "candidate_profile": candidate,
        "job": job
    })

    # Should return 200 even without OpenAI API key (returns placeholder message)
    assert response.status_code == 200

    data = response.json()
    assert "explanation" in data
    assert "learning_roadmap" in data
