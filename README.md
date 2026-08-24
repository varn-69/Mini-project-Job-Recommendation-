# AI Job Recommendation System — ML Recommendation Engine (Member 2)

This module is the **ML / recommendation engine** of the AI Job Recommendation
System. It takes a candidate profile and a structured job dataset and returns
ranked jobs with match scores, matched skills, missing skills and a full
score breakdown.

It is **independent of the frontend, FastAPI backend, database and LLM
layers** — those are owned by other team members. The ranking is fully
data/logic driven (no LLM is used to rank jobs).

## Architecture

```
Candidate Profile
       ↓
Preprocessing
       ↓
Skill Matching
       ↓
TF-IDF / Cosine Similarity
       ↓
Component Scores
       ↓
Weighted Final Score
       ↓
Ranking
       ↓
Top-N Jobs + Skill Gaps
```

## Environment setup

Requires Python 3.10+ (developed on 3.10; 3.12 also works).

**Windows**

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux**

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: pandas, numpy, scikit-learn, pytest. The `.venv/` folder is
git-ignored and must not be committed.

## Running the example

```
python examples/run_recommendation.py
```

This loads `data/jobs.csv`, scores every job for a demo candidate and prints
the top-5 recommendations with matched/missing skills and score breakdowns.

## Running the tests

```
pytest
```

## Dataset schema (`data/jobs.csv`)

> The bundled dataset is **small synthetic demo data**, not real job-market
> data. It exists so the engine can be developed and tested immediately.

| Column | Type | Description |
|---|---|---|
| `job_id` | str | Unique ID, e.g. `J001` (required) |
| `job_title` | str | Human-readable title |
| `skills` | str | Comma-separated skills, e.g. `Python, SQL, Excel` |
| `experience_required` | number | Minimum years of experience |
| `education_required` | str | e.g. `Bachelor`, `Master` |
| `location` | str | City, or `Remote` |
| `salary` | number | Annual salary (blank if unknown) |
| `description` | str | Free text used for TF-IDF similarity |

Missing values are handled: text fields default to `""`, experience to `0`,
salary to `None` (treated as neutral in scoring).

## Candidate schema

```python
candidate = {
    "skills": ["Python", "SQL", "Pandas"],   # list or comma-separated string
    "education": "BTech CSE",
    "experience": 0,                          # years
    "location": "Delhi",
    "salary_preference": 500000,              # or None
}
```

## How scoring works

### 1. Skill normalization (`recommendation/preprocessing.py`)

Skills are trimmed, lowercased, deduplicated and mapped through a
configurable alias table (`DEFAULT_SKILL_ALIASES`), e.g. `"py"` → `"python"`,
`"ml"` → `"machine learning"`, `"js"` → `"javascript"`. Pass a custom alias
map to `normalize_skill` / `normalize_skill_list` to extend it.

### 2. Baseline skill matching (`recommendation/skill_matching.py`)

- `get_matched_skills` / `get_missing_skills` compare normalized skill sets.
- Basic skill score = `matched required skills / required skills × 100`.
- Jobs with no listed skills score 0 (nothing to match against).

### 3. Weighted skill matching

Optionally pass per-skill importance weights (skills without an entry
default to weight 1.0):

```python
skill_weights = {"python": 0.30, "machine learning": 0.30, "tensorflow": 0.25, "git": 0.15}
```

Weighted score = `sum(weights of matched skills) / sum(weights of required
skills) × 100`, so matching the important skills contributes more. These
example values are illustrative, not a final project decision.

### 4. TF-IDF + cosine similarity (`recommendation/similarity.py`)

The candidate profile text (skills + education + location) is compared with
each job description using scikit-learn's `TfidfVectorizer` and
`cosine_similarity`, giving a 0–100 similarity score. Empty text safely
returns 0. This score is reported in `component_scores["similarity"]` for
explainability (it is not part of the final weighted score by default —
adding it only requires extending the weights map in `scoring.py`).

### 5. Other component scores (`recommendation/scoring.py`)

All deterministic and on a 0–100 scale:

- **Experience**: meets/exceeds requirement → 100; below → proportional
  `candidate / required × 100`; requirement of 0 → 100 for everyone.
- **Education**: keyword-based ordinal levels (configurable
  `DEFAULT_EDUCATION_LEVELS`); meets/exceeds → 100, one level below → 50,
  otherwise/unknown → 20; no requirement → 100.
- **Location**: exact match or remote/unspecified job → 100; different → 30.
- **Salary**: no preference or unknown salary → neutral 100; job salary ≥
  preference → 100; below → proportional. Salary is only an optional
  preference signal, not a suitability predictor.

### 6. Final score and ranking

```python
weights = {"skill": 0.50, "experience": 0.20, "location": 0.10, "salary": 0.10, "education": 0.10}
```

These initial example weights come from the project design document and are
fully configurable (pass `weights=` to `recommend_jobs`); they are validated
to sum to 1.0. The final score is the weighted combination on a 0–100 scale.
Jobs are sorted by final score descending with deterministic tie-breaking
(more matched skills first, then job title, then job id), and the top-N are
returned.

### 7. Skill-gap analysis

Every result includes `matched_skills` and `missing_skills` so a later LLM
layer (owned by another member) can generate explanations and learning
roadmaps from the structured output.

## Integration interface (for the backend developer)

```python
from recommendation.recommender import recommend_jobs
from recommendation.preprocessing import load_jobs_csv

jobs = load_jobs_csv("data/jobs.csv")   # or a list of dicts from the DB
results = recommend_jobs(candidate=candidate, jobs=jobs, top_n=5)
```

`candidate` and each job may be plain dicts (JSON-friendly) or the
`Candidate`/`Job` dataclasses in `recommendation/models.py`. The return value
contains only standard Python types (str, float, list, dict) and serializes
directly with `json.dumps`:

```python
{
    "job_id": "J001",
    "job_title": "Data Analyst",
    "final_score": 84.2,
    "component_scores": {
        "skill": 85.0, "similarity": 79.0, "experience": 100.0,
        "location": 100.0, "education": 100.0, "salary": 90.0
    },
    "matched_skills": ["python", "sql", "pandas"],
    "missing_skills": ["excel", "power bi"]
}
```

## Known limitations

- Skill matching is exact-match after normalization; semantically related
  skills (e.g. "postgresql" vs "databases") are not linked beyond the alias
  table.
- TF-IDF is a bag-of-words baseline; it does not capture meaning or synonyms.
- Education scoring is keyword-based and does not understand field of study.
- Location scoring is binary (match/remote vs different); no distance or
  hybrid handling.
- The demo dataset is tiny and synthetic.

## Possible future improvements

- Larger/real dataset ingestion and richer skill taxonomy.
- Semantic skill matching (embeddings) as an optional upgrade to TF-IDF.
- Learning-to-rank or feedback-driven weight tuning.
- Field-of-study-aware education scoring and geo-aware location scoring.
- Per-job skill importance weights sourced from the dataset.

## Git workflow (Member 2)

Work happens on the dedicated branch `member2-recommendation`:

```
git add <files>
git commit -m "Build ML recommendation engine"
git push -u origin member2-recommendation
```

Do not merge into `main` without team review.
