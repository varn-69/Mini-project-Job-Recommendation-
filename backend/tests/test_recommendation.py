import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.ml.recommendation import RecommendationEngine
from app.ml.preprocess import preprocess_job_data


def test_recommendation_engine_initialization():
    """Test recommendation engine initialization."""
    # Create sample job data
    data = {
        'job_id': [1, 2],
        'job_title': ['Python Developer', 'React Developer'],
        'company': ['TechCorp', 'WebSolutions'],
        'skills': [['python', 'django', 'git'], ['react', 'javascript', 'css']],
        'experience_required': [2, 1],
        'salary_min': [600000, 500000],
        'salary_max': [1200000, 900000],
        'location': ['Bangalore', 'Noida'],
        'education': ['B.Tech Computer Science', 'B.Tech/B.E. Computer Science'],
        'description': ['Develop web applications', 'Build user interfaces']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    assert engine is not None
    assert engine.tfidf_vectorizer is not None
    assert engine.job_tfidf_matrix is not None


def test_skill_match_score():
    """Test skill match score calculation."""
    data = {
        'job_id': [1],
        'job_title': ['Python Developer'],
        'company': ['TechCorp'],
        'skills': [['python', 'django', 'git']],
        'experience_required': [2],
        'salary_min': [600000],
        'salary_max': [1200000],
        'location': ['Bangalore'],
        'education': ['B.Tech Computer Science'],
        'description': ['Develop web applications']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    # Test with matching skills
    score, matched = engine.calculate_skill_match_score(['python', 'django'], ['python', 'django', 'git'])
    assert score == 2/3  # 2 out of 3 skills matched
    assert 'python' in matched
    assert 'django' in matched

    # Test with no matching skills
    score, matched = engine.calculate_skill_match_score(['javascript'], ['python', 'django'])
    assert score == 0.0
    assert len(matched) == 0


def test_experience_score():
    """Test experience score calculation."""
    data = {
        'job_id': [1],
        'job_title': ['Python Developer'],
        'company': ['TechCorp'],
        'skills': [['python']],
        'experience_required': [2],
        'salary_min': [600000],
        'salary_max': [1200000],
        'location': ['Bangalore'],
        'education': ['B.Tech Computer Science'],
        'description': ['Develop web applications']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    # Test with sufficient experience
    score = engine.calculate_experience_score(3, 2)
    assert score == 1.0

    # Test with insufficient experience
    score = engine.calculate_experience_score(1, 2)
    assert score == 0.5  # 1/2


def test_location_score():
    """Test location score calculation."""
    data = {
        'job_id': [1],
        'job_title': ['Python Developer'],
        'company': ['TechCorp'],
        'skills': [['python']],
        'experience_required': [2],
        'salary_min': [600000],
        'salary_max': [1200000],
        'location': ['Bangalore'],
        'education': ['B.Tech Computer Science'],
        'description': ['Develop web applications']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    # Test exact match
    score = engine.calculate_location_score('Bangalore', 'Bangalore')
    assert score == 1.0

    # Test different location
    score = engine.calculate_location_score('Noida', 'Bangalore')
    assert score < 1.0


def test_salary_score():
    """Test salary score calculation."""
    data = {
        'job_id': [1],
        'job_title': ['Python Developer'],
        'company': ['TechCorp'],
        'skills': [['python']],
        'experience_required': [2],
        'salary_min': [600000],
        'salary_max': [1200000],
        'location': ['Bangalore'],
        'education': ['B.Tech Computer Science'],
        'description': ['Develop web applications']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    # Test salary meets expectation
    score = engine.calculate_salary_score(500000, 600000, 1200000)
    assert score == 1.0

    # Test salary below expectation
    score = engine.calculate_salary_score(800000, 600000, 700000)
    assert score < 1.0


def test_overall_score_calculation():
    """Test overall score calculation."""
    data = {
        'job_id': [1],
        'job_title': ['Python Developer'],
        'company': ['TechCorp'],
        'skills': [['python', 'django', 'git']],
        'experience_required': [2],
        'salary_min': [600000],
        'salary_max': [1200000],
        'location': ['Bangalore'],
        'education': ['B.Tech Computer Science'],
        'description': ['Develop web applications using Python and Django']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    candidate = {
        'name': 'Test',
        'skills': 'Python, Django',
        'education': 'B.Tech Computer Science',
        'experience': 2,
        'location': 'Bangalore',
        'expected_salary': 500000
    }

    scores = engine.calculate_overall_score(candidate, df.iloc[0])

    # Check that all scores are present
    assert 'final_score' in scores
    assert 'skill_score' in scores
    assert 'experience_score' in scores
    assert 'location_score' in scores
    assert 'salary_score' in scores
    assert 'education_score' in scores
    assert 'matched_skills' in scores
    assert 'missing_skills' in scores

    # Check that scores are between 0 and 1
    assert 0 <= scores['final_score'] <= 1
    assert 0 <= scores['skill_score'] <= 1
    assert 0 <= scores['experience_score'] <= 1


def test_recommend_jobs():
    """Test job recommendation."""
    data = {
        'job_id': [1, 2, 3],
        'job_title': ['Python Developer', 'React Developer', 'Data Scientist'],
        'company': ['TechCorp', 'WebSolutions', 'DataMinds'],
        'skills': [['python', 'django', 'git'], ['react', 'javascript', 'css'], ['python', 'pandas', 'numpy']],
        'experience_required': [2, 1, 3],
        'salary_min': [600000, 500000, 800000],
        'salary_max': [1200000, 900000, 1500000],
        'location': ['Bangalore', 'Noida', 'Bangalore'],
        'education': ['B.Tech Computer Science', 'B.Tech/B.E. Computer Science', 'M.Tech Computer Science'],
        'description': ['Develop web applications', 'Build user interfaces', 'Analyze data']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    candidate = {
        'name': 'Test',
        'skills': 'Python, Django',
        'education': 'B.Tech Computer Science',
        'experience': 2,
        'location': 'Bangalore',
        'expected_salary': 500000
    }

    recommendations = engine.recommend_jobs(candidate, top_n=2)

    # Check that we get recommendations
    assert len(recommendations) == 2

    # Check that recommendations are sorted by score
    assert recommendations[0]['final_score'] >= recommendations[1]['final_score']

    # Check that all required fields are present
    assert 'job_id' in recommendations[0]
    assert 'job_title' in recommendations[0]
    assert 'final_score' in recommendations[0]
    assert 'matched_skills' in recommendations[0]
    assert 'missing_skills' in recommendations[0]


def test_skill_gap_detection():
    """Test skill gap detection."""
    data = {
        'job_id': [1],
        'job_title': ['Python Developer'],
        'company': ['TechCorp'],
        'skills': [['python', 'django', 'git', 'docker']],
        'experience_required': [2],
        'salary_min': [600000],
        'salary_max': [1200000],
        'location': ['Bangalore'],
        'education': ['B.Tech Computer Science'],
        'description': ['Develop web applications']
    }

    df = pd.DataFrame(data)
    engine = RecommendationEngine(df)

    candidate = {
        'name': 'Test',
        'skills': 'Python, Django',
        'education': 'B.Tech Computer Science',
        'experience': 2,
        'location': 'Bangalore',
        'expected_salary': 500000
    }

    scores = engine.calculate_overall_score(candidate, df.iloc[0])

    # Check that matched skills are detected
    assert 'python' in scores['matched_skills']
    assert 'django' in scores['matched_skills']

    # Check that missing skills are detected
    assert 'git' in scores['missing_skills']
    assert 'docker' in scores['missing_skills']
