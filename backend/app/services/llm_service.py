import openai
from typing import Dict
from app.config import settings

# Initialize OpenAI client (will be None if no API key)
client = None
if settings.openai_api_key:
    client = openai.OpenAI(api_key=settings.openai_api_key)


def generate_explanation(candidate_profile: Dict, job: Dict) -> str:
    """Generate an explanation for why a job is recommended using OpenAI."""
    if not client:
        return "OpenAI API key not configured. Explanation feature unavailable."

    # Build prompt
    prompt = f"""
You are a career advisor helping a student understand why a job is recommended for them.

Candidate Profile:
- Name: {candidate_profile.get('name', 'Student')}
- Skills: {candidate_profile.get('skills', '')}
- Education: {candidate_profile.get('education', '')}
- Experience: {candidate_profile.get('experience', 0)} years
- Location: {candidate_profile.get('location', '')}
- Expected Salary: {candidate_profile.get('expected_salary', 0)}

Job Details:
- Title: {job.get('job_title', '')}
- Company: {job.get('company', '')}
- Required Skills: {', '.join(job.get('skills', []))}
- Experience Required: {job.get('experience_required', 0)} years
- Location: {job.get('location', '')}
- Salary Range: {job.get('salary_min', 0)} - {job.get('salary_max', 0)}
- Education: {job.get('education', '')}

Match Information:
- Overall Match Score: {job.get('final_score', 0):.1%}
- Skill Match: {job.get('skill_score', 0):.1%}
- Experience Match: {job.get('experience_score', 0):.1%}
- Location Match: {job.get('location_score', 0):.1%}
- Salary Match: {job.get('salary_score', 0):.1%}
- Education Match: {job.get('education_score', 0):.1%}
- Matched Skills: {', '.join(job.get('matched_skills', []))}
- Missing Skills: {', '.join(job.get('missing_skills', []))}

Please provide a concise explanation (3-4 sentences) explaining:
1. Why this role matches the candidate
2. The candidate's key strengths for this role
3. Any skill gaps that need addressing

Keep it encouraging and specific to the student.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful career advisor for students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating explanation: {str(e)}"


def generate_learning_roadmap(candidate_profile: Dict, job: Dict) -> str:
    """Generate a learning roadmap for missing skills using OpenAI."""
    if not client:
        return "OpenAI API key not configured. Learning roadmap feature unavailable."

    missing_skills = job.get('missing_skills', [])

    if not missing_skills:
        return "Great news! You have all the required skills for this role."

    prompt = f"""
You are a career advisor helping a student create a learning plan.

Candidate Profile:
- Name: {candidate_profile.get('name', 'Student')}
- Skills: {candidate_profile.get('skills', '')}
- Education: {candidate_profile.get('education', '')}
- Experience: {candidate_profile.get('experience', 0)} years

Job Details:
- Title: {job.get('job_title', '')}
- Company: {job.get('company', '')}

Missing Skills: {', '.join(missing_skills)}

Please provide a concise learning roadmap (3-5 bullet points) for acquiring these missing skills.
For each skill, suggest:
- What to learn
- How long it might take (estimate)
- One resource or method to learn it

Keep it practical and suitable for a student.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful career advisor for students."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating learning roadmap: {str(e)}"
