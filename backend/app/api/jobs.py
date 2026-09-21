from fastapi import APIRouter
from app.schemas.schemas import Job
from app.ml.recommendation import RecommendationEngine
from app.ml.preprocess import load_and_preprocess_data
import os

router = APIRouter()

# Load job data
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'jobs_real.csv')
jobs_df = load_and_preprocess_data(data_path)


@router.get("/jobs", response_model=list[Job])
def get_jobs():
    """Get all available jobs."""
    jobs = []
    for _, row in jobs_df.iterrows():
        job = Job(
            job_id=int(row['job_id']),
            job_title=row['job_title'],
            company=row['company'],
            location=row['location'],
            salary_min=float(row['salary_min']),
            salary_max=float(row['salary_max']),
            experience_required=float(row['experience_required']),
            education=row['education'],
            description=row['description'],
            skills=row['skills']
        )
        jobs.append(job)
    return jobs
