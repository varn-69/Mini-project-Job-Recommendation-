import pandas as pd
import numpy as np
from typing import List
import re

def transform_open_jobs_data(input_csv: str, output_csv: str, max_records: int = 1000):
    """
    Transform Open Jobs Data dataset to our application schema.

    Source: https://github.com/ConorsCode/open-jobs-data
    License: MIT License (free for academic and commercial use)

    Transformation:
    - company_name -> company
    - title -> job_title
    - locations -> location
    - jobId -> job_id
    - Generate synthetic skills based on title (since source doesn't have skills)
    - Generate synthetic experience based on title
    - Generate synthetic salary ranges (USD) based on title patterns
    - Generate synthetic education requirements
    - Use department/title for description
    """

    # Load data
    df = pd.read_csv(input_csv)

    # Limit to max_records
    df = df.head(max_records)

    # Create transformed dataframe
    transformed_data = []

    for idx, row in df.iterrows():
        job_id = idx + 1
        job_title = row.get('title', '')
        company = row.get('company', '')
        location = row.get('locations', '')
        department = row.get('department', '')
        is_remote = row.get('isRemote', False)

        # Handle location
        if pd.isna(location) or location == '':
            if is_remote:
                location = 'Remote'
            else:
                location = 'Various Locations'

        # Generate skills based on job title (heuristic approach)
        skills = generate_skills_from_title(job_title, department)

        # Generate experience requirement based on title
        experience_required = generate_experience_from_title(job_title)

        # Generate salary range based on title patterns (USD)
        salary_min, salary_max = generate_salary_from_title(job_title, is_remote)

        # Generate education requirement
        education = generate_education_from_title(job_title)

        # Generate description
        description = generate_description(job_title, company, department, location)

        transformed_data.append({
            'job_id': job_id,
            'job_title': job_title,
            'company': company,
            'skills': skills,
            'experience_required': experience_required,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'location': location,
            'education': education,
            'description': description
        })

    # Create dataframe
    result_df = pd.DataFrame(transformed_data)

    # Save to CSV
    result_df.to_csv(output_csv, index=False)
    print(f"Transformed {len(result_df)} records from {input_csv} to {output_csv}")
    print(f"Sample record:")
    print(result_df.iloc[0].to_dict())

    return result_df


def generate_skills_from_title(title: str, department: str) -> str:
    """Generate skills based on job title and department."""
    title_lower = title.lower()
    department_lower = str(department).lower() if pd.notna(department) else ''

    skills = []

    # More comprehensive tech skills mapping
    skill_mapping = {
        'software engineer': ['Python', 'Java', 'Git', 'Algorithms', 'Data Structures', 'System Design', 'Software Development'],
        'frontend': ['React', 'JavaScript', 'CSS', 'HTML', 'TypeScript', 'Web Development', 'UI Development'],
        'backend': ['Python', 'Java', 'Node.js', 'APIs', 'Databases', 'REST', 'Server Development'],
        'full stack': ['React', 'Node.js', 'Python', 'JavaScript', 'SQL', 'Web Development', 'API Development'],
        'data scientist': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'Pandas', 'NumPy', 'Data Analysis'],
        'data engineer': ['Python', 'Spark', 'SQL', 'ETL', 'Hadoop', 'Data Pipelines', 'Big Data'],
        'machine learning': ['Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'NLP', 'AI'],
        'devops': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Infrastructure', 'Cloud Computing'],
        'security': ['Security', 'Penetration Testing', 'Network Security', 'Python', 'Cybersecurity', 'Information Security'],
        'mobile': ['Swift', 'Kotlin', 'Mobile Development', 'iOS', 'Android', 'React Native', 'Mobile Apps'],
        'cloud': ['AWS', 'Azure', 'GCP', 'Cloud Computing', 'DevOps', 'Infrastructure', 'Cloud Services'],
        'product': ['Product Management', 'Agile', 'Analytics', 'Communication', 'Strategy', 'Roadmap'],
        'design': ['Figma', 'UI Design', 'UX Design', 'Prototyping', 'User Research', 'Design Systems'],
        'qa': ['Testing', 'Selenium', 'Quality Assurance', 'Automation', 'Test Automation', 'Manual Testing'],
        'database': ['SQL', 'Database Administration', 'MySQL', 'PostgreSQL', 'NoSQL', 'Database Design'],
        'api': ['REST APIs', 'GraphQL', 'API Design', 'Documentation', 'Integration', 'Microservices'],
        'engineer': ['Problem Solving', 'Algorithms', 'Software Development', 'Git', 'Agile', 'Programming'],
        'developer': ['Programming', 'Debugging', 'Code Review', 'Git', 'Software Development', 'Coding'],
        'analyst': ['SQL', 'Excel', 'Data Analysis', 'Communication', 'Reporting', 'Business Intelligence'],
        'manager': ['Leadership', 'Project Management', 'Communication', 'Strategy', 'Agile', 'Team Management'],
        'investigator': ['Investigation', 'Analysis', 'Communication', 'Problem Solving', 'Research', 'Documentation'],
        'research': ['Research', 'Analysis', 'Data Analysis', 'Communication', 'Academic Writing', 'Statistics'],
    }

    # Match skills based on title and department
    for key, value in skill_mapping.items():
        if key in title_lower or key in department_lower:
            skills.extend(value)

    # Add common skills for tech roles
    if any(term in title_lower for term in ['engineer', 'developer', 'architect']):
        if 'Git' not in skills:
            skills.append('Git')
        if 'Agile' not in skills:
            skills.append('Agile')
        if 'Problem Solving' not in skills:
            skills.append('Problem Solving')
        if 'Programming' not in skills and 'Software Development' not in skills:
            skills.append('Programming')

    # Add language-specific skills
    if 'python' in title_lower or 'python' in department_lower:
        if 'Python' not in skills:
            skills.append('Python')
    if 'java' in title_lower or 'java' in department_lower:
        if 'Java' not in skills:
            skills.append('Java')
    if 'javascript' in title_lower or 'js' in title_lower:
        if 'JavaScript' not in skills:
            skills.append('JavaScript')
    if 'react' in title_lower or 'react' in department_lower:
        if 'React' not in skills:
            skills.append('React')

    # If no skills matched, add generic ones
    if not skills:
        skills = ['Communication', 'Problem Solving', 'Teamwork', 'Collaboration']

    # Remove duplicates and sort
    skills = sorted(list(set(skills)))

    return ', '.join(skills)


def generate_experience_from_title(title: str) -> float:
    """Generate experience requirement based on job title."""
    title_lower = title.lower()

    if any(term in title_lower for term in ['senior', 'lead', 'principal', 'staff']):
        return 5.0
    elif any(term in title_lower for term in ['junior', 'associate', 'entry']):
        return 1.0
    elif any(term in title_lower for term in ['intern', 'co-op']):
        return 0.0
    elif any(term in title_lower for term in ['manager', 'director', 'head']):
        return 7.0
    elif any(term in title_lower for term in ['architect']):
        return 6.0
    else:
        return 3.0  # Default for mid-level


def generate_salary_from_title(title: str, is_remote: bool) -> tuple:
    """Generate salary range based on job title patterns (USD)."""
    title_lower = title.lower()

    # Base salary ranges (annual USD)
    if any(term in title_lower for term in ['intern', 'co-op']):
        base_min, base_max = 30000, 60000
    elif any(term in title_lower for term in ['junior', 'associate', 'entry']):
        base_min, base_max = 70000, 100000
    elif any(term in title_lower for term in ['senior', 'lead', 'principal', 'staff']):
        base_min, base_max = 150000, 250000
    elif any(term in title_lower for term in ['manager', 'director', 'head']):
        base_min, base_max = 180000, 300000
    elif any(term in title_lower for term in ['architect']):
        base_min, base_max = 160000, 280000
    elif any(term in title_lower for term in ['engineer', 'developer']):
        base_min, base_max = 100000, 180000
    elif any(term in title_lower for term in ['data scientist', 'machine learning']):
        base_min, base_max = 120000, 200000
    elif any(term in title_lower for term in ['product manager']):
        base_min, base_max = 140000, 220000
    elif any(term in title_lower for term in ['designer']):
        base_min, base_max = 90000, 150000
    else:
        base_min, base_max = 80000, 140000

    # Adjust for remote work (typically higher for remote tech roles)
    if is_remote:
        base_min = int(base_min * 1.1)
        base_max = int(base_max * 1.1)

    return base_min, base_max


def generate_education_from_title(title: str) -> str:
    """Generate education requirement based on job title."""
    title_lower = title.lower()

    if any(term in title_lower for term in ['data scientist', 'machine learning', 'research']):
        return "Master's in Computer Science or related field"
    elif any(term in title_lower for term in ['engineer', 'developer', 'architect']):
        return "Bachelor's in Computer Science or related field"
    elif any(term in title_lower for term in ['manager', 'director', 'head']):
        return "Bachelor's or Master's in Business or related field"
    elif any(term in title_lower for term in ['intern', 'co-op']):
        return "Currently pursuing Bachelor's degree"
    elif any(term in title_lower for term in ['designer']):
        return "Bachelor's in Design or related field"
    else:
        return "Bachelor's degree or equivalent experience"


def generate_description(title: str, company: str, department: str, location: str) -> str:
    """Generate job description."""
    location_str = f" in {location}" if location and location != 'Various Locations' else ""
    dept_str = f" in the {department} department" if pd.notna(department) and department else ""

    description = f"{title} role at {company}{dept_str}{location_str}. "

    title_lower = title.lower()

    if 'engineer' in title_lower or 'developer' in title_lower:
        description += "Design, develop, and maintain software solutions. Work with cross-functional teams to deliver high-quality products and features."
    elif 'data' in title_lower:
        description += "Analyze data to extract insights and build data-driven solutions. Work with stakeholders to meet business requirements and drive decision-making."
    elif 'manager' in title_lower:
        description += "Lead and manage teams to achieve strategic objectives. Drive project success through effective planning, execution, and team development."
    elif 'designer' in title_lower:
        description += "Create user-centered designs and experiences. Collaborate with product and engineering teams to deliver intuitive and accessible products."
    elif 'investigator' in title_lower:
        description += "Investate complex cases and ensure compliance with policies and regulations. Work with cross-functional teams to resolve issues and improve processes."
    elif 'analyst' in title_lower:
        description += "Analyze business processes and data to identify opportunities for improvement. Provide insights and recommendations to drive business growth."
    elif 'security' in title_lower:
        description += "Implement and maintain security measures to protect systems and data. Monitor for threats and respond to security incidents."
    elif 'product' in title_lower:
        description += "Define product strategy and roadmap. Work with engineering, design, and business teams to deliver products that meet customer needs."
    elif 'marketing' in title_lower:
        description += "Develop and execute marketing strategies to promote products and services. Analyze market trends and customer behavior to optimize campaigns."
    elif 'sales' in title_lower:
        description += "Drive sales growth by identifying and pursuing new business opportunities. Build relationships with clients and close deals to meet revenue targets."
    elif 'support' in title_lower:
        description += "Provide excellent customer support and resolve issues efficiently. Work with technical teams to address customer concerns and improve satisfaction."
    else:
        description += "Contribute to team success through expertise and collaboration. Drive innovation and excellence in daily work to achieve organizational goals."

    return description


if __name__ == "__main__":
    import os

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    input_csv = os.path.join(script_dir, 'jobs_raw.csv')
    output_csv = os.path.join(script_dir, 'jobs_real.csv')

    if os.path.exists(input_csv):
        transform_open_jobs_data(input_csv, output_csv, max_records=1000)
    else:
        print(f"Input file not found: {input_csv}")
        print("Please download the dataset first from: https://github.com/ConorsCode/open-jobs-data")
