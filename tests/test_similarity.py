from recommendation.similarity import (
    calculate_text_similarity,
    calculate_text_similarity_batch,
)


def test_similar_texts_score_higher_than_unrelated():
    candidate = "python sql pandas data analysis"
    similar_job = "analyze data using python sql and pandas"
    unrelated_job = "design marketing campaigns and manage social media"
    assert calculate_text_similarity(candidate, similar_job) > calculate_text_similarity(
        candidate, unrelated_job
    )


def test_identical_texts_score_100():
    text = "python machine learning engineer"
    assert calculate_text_similarity(text, text) == 100.0


def test_empty_text_is_safe():
    assert calculate_text_similarity("", "python developer") == 0.0
    assert calculate_text_similarity("python developer", "   ") == 0.0
    assert calculate_text_similarity(None, "x") == 0.0  # type: ignore[arg-type]


def test_stopword_only_text_is_safe():
    assert calculate_text_similarity("the and of", "a an the") == 0.0


def test_batch_matches_range_and_order():
    candidate = "python sql pandas"
    jobs = ["python sql pandas analytics", "react javascript frontend", ""]
    scores = calculate_text_similarity_batch(candidate, jobs)
    assert len(scores) == 3
    assert all(0.0 <= s <= 100.0 for s in scores)
    assert scores[0] > scores[1]
    assert scores[2] == 0.0
