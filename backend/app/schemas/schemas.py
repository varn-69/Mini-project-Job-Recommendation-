from pydantic import BaseModel, Field
from typing import List, Optional


class CandidateProfile(BaseModel):
    """Candidate profile schema."""
    name: str = Field(..., description="Candidate name")
    skills: str = Field(..., description="Comma-separated skills")
    education: str = Field(..., description="Education qualification")
    experience: float = Field(..., description="Years of experience")
    location: str = Field(..., description="Preferred location")
    expected_salary: float = Field(..., description="Expected minimum salary")
    resume_text: Optional[str] = Field(None, description="Resume text (optional)")


class JobRecommendation(BaseModel):
    """Job recommendation schema."""
    job_id: int
    job_title: str
    company: str
    location: str
    salary_min: float
    salary_max: float
    experience_required: float
    education: str
    description: str
    skills: List[str]
    final_score: float
    skill_score: float
    experience_score: float
    location_score: float
    salary_score: float
    education_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    tfidf_similarity: float


class RecommendationRequest(BaseModel):
    """Recommendation request schema."""
    candidate: CandidateProfile


class RecommendationResponse(BaseModel):
    """Recommendation response schema."""
    recommendations: List[JobRecommendation]
    candidate_name: str


class ExplainRequest(BaseModel):
    """Explanation request schema."""
    candidate_profile: CandidateProfile
    job: JobRecommendation


class ExplainResponse(BaseModel):
    """Explanation response schema."""
    explanation: str
    learning_roadmap: str


class Job(BaseModel):
    """Job schema."""
    job_id: int
    job_title: str
    company: str
    location: str
    salary_min: float
    salary_max: float
    experience_required: float
    education: str
    description: str
    skills: List[str]


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    message: str
