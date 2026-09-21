# AI Job Recommendation System

A college mini-project that recommends suitable jobs to students/candidates by comparing their profile with a real job dataset using machine learning techniques.

## 📋 Problem Statement

Students and job seekers often struggle to find jobs that match their skills, experience, and preferences. Traditional job search platforms require manual filtering through hundreds of listings. This project aims to automate job recommendations using ML-powered matching algorithms.

## 🎯 Objective

Build a web application that:
- Accepts candidate profiles (skills, education, experience, location, salary expectations)
- Matches candidates against a job dataset using ML techniques
- Provides explainable, ranked job recommendations
- Highlights skill gaps and suggests learning paths
- Uses LLM only for explanation (not for ranking)

## ✨ Features

- **Skill-Based Matching**: Compares candidate skills with job requirements using normalization and matching
- **TF-IDF Similarity**: Uses TF-IDF vectorization and cosine similarity for text-based matching
- **Weighted Scoring**: Combines multiple factors (skills, experience, location, salary, education) into a comprehensive score
- **Skill Gap Analysis**: Shows matched and missing skills for each recommendation
- **Explainable Recommendations**: Provides detailed score breakdown for transparency
- **AI-Powered Explanations**: Uses OpenAI API to explain why a job matches and generate learning roadmaps
- **Responsive UI**: Clean, modern React interface built with Vite
- **REST API**: FastAPI backend with automatic Swagger documentation

## 🏗️ Architecture

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────┐
│  FastAPI    │
│  Backend    │
└──────┬──────┘
       │
       ├──────────────────┐
       ↓                  ↓
┌─────────────┐   ┌─────────────┐
│ ML Engine   │   │ PostgreSQL  │
│ (Scikit-    │   │  Database   │
│  Learn)     │   └─────────────┘
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  OpenAI API │
│ (Optional)  │
└─────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS** - Styling

### Backend
- **Python 3.8+** - Programming language
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server

### ML/NLP
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - ML library (TF-IDF, cosine similarity)
- **TF-IDF** - Text vectorization
- **Cosine Similarity** - Text similarity metric

### Database
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM

### LLM
- **OpenAI API** - For explanation and roadmap generation (optional)

### Dataset
- Real public dataset from Open Jobs Data (ConorsCode/open-jobs-data)
- 1,000 tech job records from ~380 companies
- Includes job titles, companies, skills, experience, salary, location, education, descriptions

## 🧠 Recommendation Methodology

### 1. Skill Matching
- Normalizes skills (e.g., "JS" → "javascript", "ReactJS" → "react")
- Calculates explicit skill overlap: `matched_skills / total_required_skills`
- Handles common skill variations and aliases

### 2. TF-IDF + Cosine Similarity
- Combines candidate profile text (skills, education, experience, location)
- Combines job text (title, skills, description, education, experience)
- Uses TF-IDF vectorization to convert text to numerical vectors
- Calculates cosine similarity between candidate and job vectors

### 3. Component Scores

**Skill Score** (50% weight):
```
Skill Score = 0.70 × explicit_skill_match + 0.30 × tfidf_cosine_similarity
```

**Experience Score** (20% weight):
- Candidate experience ≥ required: 1.0
- Candidate experience < required: partial score based on ratio

**Location Score** (10% weight):
- Exact match: 1.0
- Remote job: 0.9
- Partial match: 0.8
- Different location: 0.3

**Salary Score** (10% weight):
- Job salary ≥ expected: 1.0
- Job salary < expected: partial score based on ratio

**Education Score** (10% weight):
- Exact match: 1.0
- Higher qualification than required: 1.0
- Lower qualification: partial score

### 4. Final Score
```
Final Score = 0.50 × Skill Score
            + 0.20 × Experience Score
            + 0.10 × Location Score
            + 0.10 × Salary Score
            + 0.10 × Education Score
```

**Note**: These are initial project weights and can be tuned for better results.

## 📊 Skill Gap Analysis

For each recommended job, the system calculates:
- **Matched Skills**: Skills the candidate has that match job requirements
- **Missing Skills**: Skills required by the job that the candidate lacks

Example:
```
Candidate Skills: Python, SQL, Pandas, Git
Job Skills: Python, SQL, Pandas, FastAPI, Docker, Git

Matched: Python, SQL, Pandas, Git
Missing: FastAPI, Docker
```

## 🤖 LLM Role

**Important**: The LLM is NOT used for job ranking. Ranking is done entirely by our recommendation engine.

The OpenAI API is used only for:
1. **Explanation**: Explaining why a recommended job matches the candidate
2. **Learning Roadmap**: Generating a personalized learning plan for missing skills

The recommendation engine remains fully functional even without an OpenAI API key.

## 📁 Dataset Source

This project uses a real public job dataset transformed for the application schema.

**Dataset**: Open Jobs Data (ConorsCode/open-jobs-data)  
**Source URL**: https://github.com/ConorsCode/open-jobs-data  
**License**: MIT License (free for academic and commercial use)  
**Retrieval Date**: September 21, 2026  
**Downloaded From**: https://raw.githubusercontent.com/ConorsCode/open-jobs-data/main/data/jobs.csv

**Dataset Description**:
A free, daily-updated dataset of open job postings from ~380 well-known tech companies, pulled directly from nine applicant tracking systems (ATS) including Greenhouse, Lever, Ashby, Workday, SmartRecruiters, and others. The data is normalized into a consistent schema and includes job titles, companies, locations, and posting information.

**Subset Used**: 1,000 job records (from ~38,000 total records in the source dataset)  
**Attribution**: Data sourced from ConorsCode/open-jobs-data GitHub repository under MIT License

**Preprocessing/Transformation Performed**:
The original dataset was transformed to match our application schema through the following process:
1. **Source Fields Mapped**:
   - `company` → company
   - `title` → job_title
   - `locations` → location
   - `jobId` → job_id (generated sequentially)

2. **Generated Fields** (heuristic-based for demonstration):
   - **skills**: Generated from job title and department using keyword matching against a comprehensive tech skills mapping
   - **experience_required**: Generated from job title (senior=5y, junior=1y, intern=0y, manager=7y, architect=6y, default=3y)
   - **salary_min/salary_max**: Generated from job title patterns in USD (remote jobs get 10% premium)
   - **education**: Generated from job title (ML roles require Master's, engineering roles require Bachelor's, etc.)
   - **description**: Generated from job title, company, department, and location

3. **Schema Preservation**:
   All required fields preserved: job_id, job_title, company, skills, experience_required, salary_min, salary_max, location, education, description

4. **Currency Normalization**:
   All salaries in USD (annual) for consistency. Original dataset does not include salary information, so values are generated based on role patterns.

5. **Missing Value Handling**:
   - Missing locations defaulted to "Remote" if job is remote, else "Various Locations"
   - Missing departments handled gracefully in skill generation
   - No fake data created - values are derived from role patterns and documented as such

**Transformation Script**: `backend/data/transform_dataset.py` (reproducible transformation process)

**Note**: The source dataset does not include salary information, experience requirements, education requirements, or skills fields. These are generated using documented heuristics based on job titles and departments for demonstration purposes. For production use, consider using datasets that include these fields natively.

## 📂 Project Structure

```
Mini-project-Job-Recommendation-/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProfileForm.jsx
│   │   │   ├── RecommendationResults.jsx
│   │   │   ├── JobCard.jsx
│   │   │   └── JobDetails.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── recommend.py
│   │   │   ├── jobs.py
│   │   │   └── health.py
│   │   ├── models/
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   └── llm_service.py
│   │   ├── ml/
│   │   │   ├── preprocess.py
│   │   │   └── recommendation.py
│   │   └── database/
│   │       ├── models.py
│   │       ├── connection.py
│   │       └── init_db.py
│   ├── data/
│   │   └── jobs_sample.csv
│   ├── tests/
│   │   ├── test_preprocess.py
│   │   ├── test_recommendation.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── .env.example
│
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (optional - system works without it)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
```

5. Initialize database (optional):
```bash
python -m app.database.init_db
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env if needed (default should work)
```

## ▶️ How to Run

### Backend

1. Activate virtual environment (if not already active)
2. Run the server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
Swagger documentation at `http://localhost:8000/docs`

### Frontend

1. In a new terminal:
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🗄️ Database Setup (Optional)

The system works with CSV data and doesn't require PostgreSQL for basic functionality. To use PostgreSQL:

1. Install PostgreSQL and create a database:
```sql
CREATE DATABASE job_recommendation;
```

2. Update `.env` with your database URL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/job_recommendation
```

3. Initialize the database:
```bash
python -m app.database.init_db
```

## 📡 API Endpoints

### POST /api/recommend
Generate job recommendations for a candidate.

**Request:**
```json
{
  "candidate": {
    "name": "John Doe",
    "skills": "Python, SQL, Pandas, Git",
    "education": "B.Tech Computer Science",
    "experience": 0,
    "location": "Noida",
    "expected_salary": 500000
  }
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "job_id": 1,
      "job_title": "Python Developer",
      "company": "TechCorp",
      "location": "Bangalore",
      "salary_min": 600000,
      "salary_max": 1200000,
      "experience_required": 2,
      "education": "B.Tech Computer Science",
      "description": "...",
      "skills": ["python", "django", "git"],
      "final_score": 0.75,
      "skill_score": 0.8,
      "experience_score": 0.5,
      "location_score": 0.3,
      "salary_score": 1.0,
      "education_score": 1.0,
      "matched_skills": ["python", "git"],
      "missing_skills": ["django"],
      "tfidf_similarity": 0.6
    }
  ],
  "candidate_name": "John Doe"
}
```

### POST /api/explain
Generate AI explanation and learning roadmap for a job.

**Request:**
```json
{
  "candidate_profile": { ... },
  "job": { ... }
}
```

**Response:**
```json
{
  "explanation": "This role matches because...",
  "learning_roadmap": "To acquire the missing skills..."
}
```

### GET /api/jobs
Get all available jobs.

### GET /api/health
Health check endpoint.

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_recommendation.py
```

Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## 📝 Example Recommendation Workflow

1. **User Profile Input**:
   - Name: Student
   - Skills: Python, SQL, Pandas, NumPy, Git, FastAPI
   - Education: B.Tech Computer Science
   - Experience: 0 years
   - Location: Noida
   - Expected Salary: 500000 (Note: Dataset uses USD, so this would be $500,000 for consistency)

2. **Backend Processing**:
   - Parse and normalize skills
   - Load job dataset (1,000 real job records from Open Jobs Data)
   - Initialize TF-IDF vectorizer

3. **Recommendation Engine**:
   - Calculate skill match for each job
   - Calculate TF-IDF similarity
   - Calculate experience, location, salary, education scores
   - Compute weighted final score
   - Rank jobs by score

4. **Output**:
   - Top 10 recommended jobs
   - Each with match percentage and score breakdown
   - Matched and missing skills

5. **Explanation** (optional):
   - User clicks "Explain Recommendation"
   - Backend sends job details to OpenAI
   - Returns explanation and learning roadmap

**Note**: The job dataset contains real job postings from companies like Stripe, Google, Amazon, etc., sourced from the Open Jobs Data repository. Skills, experience, salary, and education fields are generated from job titles using documented heuristics.

## ⚠️ Limitations

- **Dataset Size**: Uses 1,000 job records from the Open Jobs Data dataset (subset of ~38,000 total records)
- **Skill Generation**: Skills are generated from job titles using heuristic matching (source dataset doesn't include skills)
- **Salary/Experience/Education**: These fields are generated from job title patterns (source dataset doesn't include these fields)
- **Skill Normalization**: Limited to common skill aliases
- **Location Matching**: Simple string matching (no geolocation)
- **Salary Score**: Basic comparison without cost-of-living adjustment
- **Education Score**: Simple degree-level matching
- **No User Authentication**: System doesn't track user sessions
- **No Real-time Updates**: Dataset is static
- **LLM Dependency**: Explanation feature requires OpenAI API key

## 🔮 Future Scope

- **PDF Resume Parsing**: Extract skills and experience from PDF resumes
- **Mock Interview**: Generate interview questions based on job requirements
- **Live Job APIs**: Integrate with real-time job posting APIs
- **Career Path Recommendation**: Suggest career progression paths
- **Personalization**: Learn from user likes/dislikes
- **Market Trends**: Analyze job market trends and salary insights
- **Advanced Learning Roadmap**: More detailed, time-bound learning plans
- **User Accounts**: Save profiles and recommendation history
- **Job Application Tracking**: Track application status
- **Collaborative Filtering**: Use other users' preferences for recommendations

## 📄 License

This is a college mini-project for educational purposes.

## 👨‍💻 Author

5th Semester College Mini Project

## 🙏 Acknowledgments

- Scikit-learn for ML algorithms
- FastAPI for the web framework
- OpenAI for LLM capabilities
- React community for the UI library
