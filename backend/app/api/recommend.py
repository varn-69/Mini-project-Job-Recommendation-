from fastapi import APIRouter, HTTPException
from app.schemas.schemas import RecommendationRequest, RecommendationResponse, ExplainRequest, ExplainResponse
from app.ml.recommendation import RecommendationEngine
from app.ml.preprocess import load_and_preprocess_data
from app.services.llm_service import generate_explanation, generate_learning_roadmap
import pandas as pd
import os

router = APIRouter()

# Load job data
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'jobs_sample.csv')
jobs_df = load_and_preprocess_data(data_path)

# Initialize recommendation engine
recommendation_engine = RecommendationEngine(jobs_df)


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_jobs(request: RecommendationRequest):
    """Generate job recommendations for a candidate."""
    try:
        # Convert candidate profile to dict
        candidate_dict = request.candidate.model_dump()

        # Get recommendations
        recommendations = recommendation_engine.recommend_jobs(candidate_dict, top_n=10)

        return RecommendationResponse(
            recommendations=recommendations,
            candidate_name=request.candidate.name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=ExplainResponse)
def explain_recommendation(request: ExplainRequest):
    """Generate an explanation and learning roadmap for a job recommendation."""
    try:
        # Convert to dicts
        candidate_dict = request.candidate_profile.model_dump()
        job_dict = request.job.model_dump()

        # Generate explanation
        explanation = generate_explanation(candidate_dict, job_dict)

        # Generate learning roadmap
        learning_roadmap = generate_learning_roadmap(candidate_dict, job_dict)

        return ExplainResponse(
            explanation=explanation,
            learning_roadmap=learning_roadmap
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
