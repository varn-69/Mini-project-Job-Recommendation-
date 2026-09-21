import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import SCORING_WEIGHTS, SKILL_SCORE_WEIGHTS
from app.ml.preprocess import normalize_skill, parse_skills


class RecommendationEngine:
    def __init__(self, jobs_df: pd.DataFrame):
        """Initialize the recommendation engine with job data."""
        self.jobs_df = jobs_df.copy()
        self.tfidf_vectorizer = None
        self.job_tfidf_matrix = None
        self._initialize_tfidf()

    def _initialize_tfidf(self):
        """Initialize TF-IDF vectorizer with job descriptions."""
        # Combine job text for TF-IDF
        job_texts = []
        for _, job in self.jobs_df.iterrows():
            text = f"{job.get('job_title', '')} {' '.join(job.get('skills', []))} {job.get('description', '')}"
            job_texts.append(text)

        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.job_tfidf_matrix = self.tfidf_vectorizer.fit_transform(job_texts)

    def calculate_skill_match_score(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill match score based on explicit skill overlap."""
        if not job_skills:
            return 0.0

        # Normalize and convert to sets
        candidate_skills_normalized = set([normalize_skill(skill) for skill in candidate_skills])
        job_skills_normalized = set([normalize_skill(skill) for skill in job_skills])

        # Calculate overlap
        matched_skills = candidate_skills_normalized.intersection(job_skills_normalized)

        # Score = matched / total required skills
        score = len(matched_skills) / len(job_skills_normalized) if job_skills_normalized else 0.0

        return score, list(matched_skills)

    def calculate_tfidf_similarity(self, candidate_text: str, job_index: int) -> float:
        """Calculate TF-IDF cosine similarity between candidate and job."""
        if not candidate_text or self.tfidf_vectorizer is None:
            return 0.0

        # Vectorize candidate text
        candidate_tfidf = self.tfidf_vectorizer.transform([candidate_text])

        # Get job TF-IDF vector
        job_tfidf = self.job_tfidf_matrix[job_index]

        # Calculate cosine similarity
        similarity = cosine_similarity(candidate_tfidf, job_tfidf)[0][0]

        return similarity

    def calculate_experience_score(self, candidate_experience: float, job_experience_required: float) -> float:
        """Calculate experience match score."""
        if job_experience_required == 0:
            return 1.0  # No experience required

        if candidate_experience >= job_experience_required:
            return 1.0

        # If candidate has less experience, give partial score
        # Linear decay: if candidate has 0 experience but job requires 2 years, score = 0.5
        ratio = candidate_experience / job_experience_required
        return max(0.0, ratio)

    def calculate_location_score(self, candidate_location: str, job_location: str) -> float:
        """Calculate location match score."""
        if not candidate_location or not job_location:
            return 0.5  # Neutral score if location info missing

        candidate_location = candidate_location.lower().strip()
        job_location = job_location.lower().strip()

        # Exact match
        if candidate_location == job_location:
            return 1.0

        # Remote job
        if 'remote' in job_location or 'remote' in candidate_location:
            return 0.9

        # Partial match (e.g., "Bangalore" vs "Bangalore, India")
        if candidate_location in job_location or job_location in candidate_location:
            return 0.8

        # Different location
        return 0.3

    def calculate_salary_score(self, candidate_expected_salary: float, job_salary_min: float, job_salary_max: float) -> float:
        """Calculate salary match score."""
        if not candidate_expected_salary or (job_salary_min == 0 and job_salary_max == 0):
            return 0.5  # Neutral score if salary info missing

        # Use average if available, else use min
        job_salary = (job_salary_min + job_salary_max) / 2 if job_salary_max > 0 else job_salary_min

        if job_salary >= candidate_expected_salary:
            return 1.0

        # If job salary is below expectation, give partial score
        ratio = job_salary / candidate_expected_salary
        return max(0.0, ratio)

    def calculate_education_score(self, candidate_education: str, job_education: str) -> float:
        """Calculate education match score."""
        if not candidate_education or not job_education:
            return 0.5  # Neutral score if education info missing

        candidate_education = candidate_education.lower()
        job_education = job_education.lower()

        # Exact match
        if candidate_education == job_education:
            return 1.0

        # Check for degree level match
        candidate_has_btech = 'b.tech' in candidate_education or 'b.e' in candidate_education or 'bachelor' in candidate_education
        candidate_has_mtech = 'm.tech' in candidate_education or 'm.sc' in candidate_education or 'master' in candidate_education

        job_requires_btech = 'b.tech' in job_education or 'b.e' in job_education or 'bachelor' in job_education
        job_requires_mtech = 'm.tech' in job_education or 'm.sc' in job_education or 'master' in job_education

        # If job requires B.Tech and candidate has M.Tech, that's good
        if job_requires_btech and candidate_has_mtech:
            return 1.0

        # If job requires M.Tech and candidate has B.Tech, partial score
        if job_requires_mtech and candidate_has_btech:
            return 0.7

        # If both have B.Tech
        if job_requires_btech and candidate_has_btech:
            return 1.0

        # If both have M.Tech
        if job_requires_mtech and candidate_has_mtech:
            return 1.0

        # Default partial score
        return 0.5

    def calculate_overall_score(self, candidate_profile: Dict, job: pd.Series) -> Dict:
        """Calculate overall recommendation score for a job."""
        # Extract candidate information
        candidate_skills = parse_skills(candidate_profile.get('skills', ''))
        candidate_experience = float(candidate_profile.get('experience', 0))
        candidate_location = candidate_profile.get('location', '')
        candidate_expected_salary = float(candidate_profile.get('expected_salary', 0))
        candidate_education = candidate_profile.get('education', '')

        # Extract job information
        job_skills = job.get('skills', [])
        job_experience_required = float(job.get('experience_required', 0))
        job_location = job.get('location', '')
        job_salary_min = float(job.get('salary_min', 0))
        job_salary_max = float(job.get('salary_max', 0))
        job_education = job.get('education', '')

        # Calculate component scores
        skill_match_score, matched_skills = self.calculate_skill_match_score(candidate_skills, job_skills)

        # Build candidate text for TF-IDF
        candidate_text = f"{candidate_profile.get('skills', '')} {candidate_education} {candidate_experience} years {candidate_location}"

        # Get job index for TF-IDF
        job_index = job.name if hasattr(job, 'name') else 0
        tfidf_similarity = self.calculate_tfidf_similarity(candidate_text, job_index)

        # Combine skill scores
        skill_score = (SKILL_SCORE_WEIGHTS['explicit_match'] * skill_match_score +
                      SKILL_SCORE_WEIGHTS['tfidf_similarity'] * tfidf_similarity)

        experience_score = self.calculate_experience_score(candidate_experience, job_experience_required)
        location_score = self.calculate_location_score(candidate_location, job_location)
        salary_score = self.calculate_salary_score(candidate_expected_salary, job_salary_min, job_salary_max)
        education_score = self.calculate_education_score(candidate_education, job_education)

        # Calculate weighted final score
        final_score = (
            SCORING_WEIGHTS['skill'] * skill_score +
            SCORING_WEIGHTS['experience'] * experience_score +
            SCORING_WEIGHTS['location'] * location_score +
            SCORING_WEIGHTS['salary'] * salary_score +
            SCORING_WEIGHTS['education'] * education_score
        )

        # Calculate missing skills
        job_skills_normalized = set([normalize_skill(skill) for skill in job_skills])
        candidate_skills_normalized = set([normalize_skill(skill) for skill in candidate_skills])
        missing_skills = list(job_skills_normalized - candidate_skills_normalized)

        return {
            'final_score': final_score,
            'skill_score': skill_score,
            'experience_score': experience_score,
            'location_score': location_score,
            'salary_score': salary_score,
            'education_score': education_score,
            'matched_skills': sorted(list(matched_skills)),
            'missing_skills': sorted(missing_skills),
            'tfidf_similarity': tfidf_similarity,
        }

    def recommend_jobs(self, candidate_profile: Dict, top_n: int = 10) -> List[Dict]:
        """Generate job recommendations for a candidate."""
        recommendations = []

        for idx, job in self.jobs_df.iterrows():
            # Calculate scores
            scores = self.calculate_overall_score(candidate_profile, job)

            # Create recommendation entry
            recommendation = {
                'job_id': int(job.get('job_id', idx)),
                'job_title': job.get('job_title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'salary_min': float(job.get('salary_min', 0)),
                'salary_max': float(job.get('salary_max', 0)),
                'experience_required': float(job.get('experience_required', 0)),
                'education': job.get('education', ''),
                'description': job.get('description', ''),
                'skills': job.get('skills', []),
                **scores
            }

            recommendations.append(recommendation)

        # Sort by final score (descending)
        recommendations.sort(key=lambda x: x['final_score'], reverse=True)

        # Return top N
        return recommendations[:top_n]


if __name__ == "__main__":
    # Example usage
    from app.ml.preprocess import load_and_preprocess_data

    # Load data
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'jobs_sample.csv')
    df = load_and_preprocess_data(data_path)

    # Initialize engine
    engine = RecommendationEngine(df)

    # Example candidate
    candidate = {
        'name': 'Test Candidate',
        'skills': 'Python, SQL, Pandas, NumPy, Git, FastAPI',
        'education': 'B.Tech Computer Science',
        'experience': 0,
        'location': 'Noida',
        'expected_salary': 500000
    }

    # Get recommendations
    recommendations = engine.recommend_jobs(candidate, top_n=5)

    print("Top 5 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['job_title']} at {rec['company']}")
        print(f"   Score: {rec['final_score']:.2%}")
        print(f"   Matched Skills: {', '.join(rec['matched_skills'])}")
        print(f"   Missing Skills: {', '.join(rec['missing_skills'])}")
