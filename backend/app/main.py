from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import recommend, jobs, health

app = FastAPI(title="Job Recommendation API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommend.router, prefix="/api", tags=["recommendations"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/")
def root():
    return {"message": "Job Recommendation API", "version": "1.0.0"}
