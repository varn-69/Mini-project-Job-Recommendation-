import pandas as pd
import numpy as np
import re
from typing import Dict, List
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def normalize_skill(skill: str) -> str:
    """Normalize a skill name to a standard form."""
    if not skill or not isinstance(skill, str):
        return ""

    skill = skill.strip().lower()

    # Remove common punctuation
    skill = re.sub(r'[.,;:!?()]', '', skill)

    # Skill normalization mapping
    skill_aliases = {
        'js': 'javascript',
        'reactjs': 'react',
        'react.js': 'react',
        'nodejs': 'node.js',
        'node.js': 'node.js',
        'node': 'node.js',
        'py': 'python',
        'postgres': 'postgresql',
        'postgre': 'postgresql',
        'gitlab': 'git',
        'github': 'git',
        'typescript': 'typescript',
        'ts': 'typescript',
        'angularjs': 'angular',
        'vuejs': 'vue',
        'vue.js': 'vue',
        'docker': 'docker',
        'k8s': 'kubernetes',
        'k8': 'kubernetes',
        'aws': 'aws',
        'azure': 'azure',
        'gcp': 'gcp',
        'ml': 'machine learning',
        'deep learning': 'deep learning',
        'dl': 'deep learning',
        'nlp': 'nlp',
        'natural language processing': 'nlp',
        'cv': 'computer vision',
        'computer vision': 'computer vision',
        'ai': 'artificial intelligence',
        'artificial intelligence': 'artificial intelligence',
        'scikit-learn': 'scikit-learn',
        'sklearn': 'scikit-learn',
        'tf': 'tensorflow',
        'torch': 'pytorch',
        'pytorch': 'pytorch',
        'sql': 'sql',
        'nosql': 'nosql',
        'mongo': 'mongodb',
        'mongodb': 'mongodb',
        'mysql': 'mysql',
        'api': 'api',
        'rest': 'rest api',
        'restful': 'rest api',
        'graphql': 'graphql',
        'ci/cd': 'cicd',
        'cicd': 'cicd',
        'devops': 'devops',
        'agile': 'agile',
        'scrum': 'scrum',
        'ui/ux': 'ui/ux',
        'ux': 'ui/ux',
        'ui': 'ui/ux',
    }

    return skill_aliases.get(skill, skill)


def parse_skills(skills_str: str) -> List[str]:
    """Parse skills from a comma-separated string and normalize them."""
    if not skills_str or not isinstance(skills_str, str):
        return []

    # Split by comma and normalize each skill
    skills = [normalize_skill(skill) for skill in skills_str.split(',')]
    # Remove empty strings and duplicates
    skills = list(set([skill for skill in skills if skill]))
    return sorted(skills)


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and special characters."""
    if not text or not isinstance(text, str):
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)

    return text


def preprocess_job_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the job dataset."""
    df = df.copy()

    # Handle missing values
    df = df.dropna(subset=['job_id', 'job_title', 'company'])

    # Normalize skills
    df['skills'] = df['skills'].apply(parse_skills)

    # Clean text fields
    text_columns = ['job_title', 'company', 'location', 'education', 'description']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # Ensure numeric fields are numeric
    numeric_columns = ['experience_required', 'salary_min', 'salary_max']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Calculate average salary if both min and max exist
    if 'salary_min' in df.columns and 'salary_max' in df.columns:
        df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

    return df


def load_and_preprocess_data(input_path: str, output_path: str = None) -> pd.DataFrame:
    """Load and preprocess job data from CSV."""
    # Load data
    df = pd.read_csv(input_path)

    # Preprocess
    df_processed = preprocess_job_data(df)

    # Save processed data if output path is provided
    if output_path:
        df_processed.to_csv(output_path, index=False)
        print(f"Processed data saved to {output_path}")

    return df_processed


if __name__ == "__main__":
    # Example usage
    input_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'jobs_sample.csv')
    output_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'jobs_processed.csv')

    if os.path.exists(input_csv):
        df = load_and_preprocess_data(input_csv, output_csv)
        print(f"Preprocessed {len(df)} jobs")
        print("\nSample processed job:")
        print(df.iloc[0].to_dict())
    else:
        print(f"Input file not found: {input_csv}")
