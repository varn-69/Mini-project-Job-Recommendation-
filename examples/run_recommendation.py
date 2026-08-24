"""Example: load the demo dataset and print top-5 recommendations.

Run from the repository root:

    python examples/run_recommendation.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation.preprocessing import load_jobs_csv
from recommendation.recommender import recommend_jobs

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "jobs.csv")


def main() -> None:
    """Run the demo recommendation flow and print a readable report."""
    candidate = {
        "skills": ["Python", "SQL", "Pandas"],
        "education": "BTech CSE",
        "experience": 0,
        "location": "Delhi",
        "salary_preference": 500000,
    }

    jobs = load_jobs_csv(DATA_PATH)
    results = recommend_jobs(candidate=candidate, jobs=jobs, top_n=5)

    print("Candidate:")
    print(", ".join(candidate["skills"]))
    print(f"Experience: {candidate['experience']}")
    print(f"Location: {candidate['location']}")
    print()
    print("TOP RECOMMENDATIONS")
    print("-------------------")
    print()
    for rank, result in enumerate(results, start=1):
        print(f"{rank}. {result['job_title']}")
        print(f"   Score: {result['final_score']}")
        print(f"   Matched: {', '.join(result['matched_skills']) or '(none)'}")
        print(f"   Missing: {', '.join(result['missing_skills']) or '(none)'}")
        components = ", ".join(f"{k}={v}" for k, v in result["component_scores"].items())
        print(f"   Components: {components}")
        print()


if __name__ == "__main__":
    main()
