from sqlalchemy import Column, Integer, String, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Job(Base):
    """Job model for storing job postings."""
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    skills = Column(JSON, nullable=False)  # List of skills
    experience_required = Column(Float, default=0)
    salary_min = Column(Float, default=0)
    salary_max = Column(Float, default=0)
    location = Column(String(255))
    education = Column(String(255))
    description = Column(Text)


class CandidateProfile(Base):
    """Candidate profile model for storing candidate information."""
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    skills = Column(JSON, nullable=False)  # List of skills
    education = Column(String(255))
    experience = Column(Float, default=0)
    location = Column(String(255))
    expected_salary = Column(Float, default=0)
    resume_text = Column(Text, nullable=True)


class Recommendation(Base):
    """Recommendation result model for storing recommendation history."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=True)  # Optional foreign key to candidate_profiles
    job_id = Column(Integer, nullable=False)
    final_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    location_score = Column(Float, nullable=False)
    salary_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    matched_skills = Column(JSON, nullable=False)  # List of matched skills
    missing_skills = Column(JSON, nullable=False)  # List of missing skills
    created_at = Column(String(255), nullable=True)  # Timestamp as string for simplicity
