"""TF-IDF / cosine-similarity text comparison.

Compares candidate profile text with a job description using
scikit-learn's TfidfVectorizer and cosine similarity, returning a
0-100 score. This is an interpretable NLP baseline — no neural nets.
"""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(candidate_text: str, job_text: str) -> float:
    """Cosine similarity between two texts on a 0-100 scale.

    Fits a TF-IDF vectorizer on the two texts and returns their cosine
    similarity multiplied by 100. Empty or non-string inputs safely
    return 0.0.
    """
    if not isinstance(candidate_text, str) or not isinstance(job_text, str):
        return 0.0
    candidate_text = candidate_text.strip()
    job_text = job_text.strip()
    if not candidate_text or not job_text:
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([candidate_text, job_text])
    except ValueError:
        # Both texts contained only stop words / no valid tokens.
        return 0.0
    score = float(cosine_similarity(matrix[0], matrix[1])[0][0])
    return max(0.0, min(score * 100.0, 100.0))


def calculate_text_similarity_batch(candidate_text: str, job_texts: list[str]) -> list[float]:
    """Cosine similarity of one candidate text against many job texts.

    Fitting a single vectorizer over the whole corpus gives consistent
    IDF statistics across jobs and is faster than pairwise calls.

    Returns a list of 0-100 scores aligned with ``job_texts``
    (all zeros when the candidate text or corpus is empty).
    """
    if not isinstance(candidate_text, str) or not candidate_text.strip() or not job_texts:
        return [0.0] * len(job_texts)
    cleaned = [t.strip() if isinstance(t, str) else "" for t in job_texts]
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([candidate_text.strip()] + cleaned)
    except ValueError:
        return [0.0] * len(job_texts)
    sims = cosine_similarity(matrix[0], matrix[1:])[0]
    return [max(0.0, min(float(s) * 100.0, 100.0)) for s in sims]
