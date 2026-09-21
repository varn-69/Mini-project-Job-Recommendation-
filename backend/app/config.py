from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/job_recommendation"
    openai_api_key: str = ""
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()


# Scoring weights - these are initial project weights and can be tuned
SCORING_WEIGHTS = {
    "skill": 0.50,
    "experience": 0.20,
    "location": 0.10,
    "salary": 0.10,
    "education": 0.10,
}

# Skill score composition
SKILL_SCORE_WEIGHTS = {
    "explicit_match": 0.70,
    "tfidf_similarity": 0.30,
}

# Recommendation settings
TOP_N_RECOMMENDATIONS = 10
