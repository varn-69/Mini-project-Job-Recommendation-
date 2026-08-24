import pytest

from recommendation.scoring import (
    DEFAULT_WEIGHTS,
    calculate_education_score,
    calculate_experience_score,
    calculate_final_score,
    calculate_location_score,
    calculate_salary_score,
    validate_weights,
)


class TestExperienceScore:
    def test_zero_vs_zero(self):
        assert calculate_experience_score(0, 0) == 100.0

    def test_zero_vs_one(self):
        assert calculate_experience_score(0, 1) == 0.0

    def test_two_vs_one(self):
        assert calculate_experience_score(2, 1) == 100.0

    def test_five_vs_three(self):
        assert calculate_experience_score(5, 3) == 100.0

    def test_partial_below_requirement(self):
        assert calculate_experience_score(1, 2) == pytest.approx(50.0)

    def test_missing_values(self):
        assert calculate_experience_score(None, None) == 100.0


class TestEducationScore:
    def test_meets_requirement(self):
        assert calculate_education_score("BTech CSE", "Bachelor") == 100.0

    def test_exceeds_requirement(self):
        assert calculate_education_score("MTech", "Bachelor") == 100.0

    def test_one_level_below(self):
        assert calculate_education_score("BTech", "Master") == 50.0

    def test_unknown_candidate_education(self):
        assert calculate_education_score("", "Bachelor") == 20.0

    def test_no_requirement(self):
        assert calculate_education_score("anything", "") == 100.0


class TestLocationScore:
    def test_exact_match(self):
        assert calculate_location_score("Delhi", "delhi") == 100.0

    def test_remote(self):
        assert calculate_location_score("Delhi", "Remote") == 100.0

    def test_different(self):
        assert calculate_location_score("Delhi", "Mumbai") == 30.0

    def test_missing_job_location(self):
        assert calculate_location_score("Delhi", "") == 100.0


class TestSalaryScore:
    def test_no_preference(self):
        assert calculate_salary_score(None, 500000) == 100.0

    def test_unknown_job_salary(self):
        assert calculate_salary_score(500000, None) == 100.0

    def test_meets_preference(self):
        assert calculate_salary_score(500000, 600000) == 100.0

    def test_below_preference(self):
        assert calculate_salary_score(500000, 250000) == pytest.approx(50.0)


class TestFinalScore:
    def test_all_100_gives_100(self):
        scores = {k: 100.0 for k in DEFAULT_WEIGHTS}
        assert calculate_final_score(scores) == 100.0

    def test_weighted_combination(self):
        scores = {"skill": 80, "experience": 100, "location": 100, "salary": 100, "education": 100}
        # 0.5*80 + 0.5*100 = 90
        assert calculate_final_score(scores) == pytest.approx(90.0)

    def test_custom_weights(self):
        weights = {"skill": 1.0, "experience": 0.0, "location": 0.0, "salary": 0.0, "education": 0.0}
        scores = {"skill": 42, "experience": 0, "location": 0, "salary": 0, "education": 0}
        assert calculate_final_score(scores, weights) == pytest.approx(42.0)

    def test_weights_must_sum_to_one(self):
        bad = dict(DEFAULT_WEIGHTS)
        bad["skill"] = 0.9
        with pytest.raises(ValueError, match="sum to 1.0"):
            validate_weights(bad)

    def test_weights_unknown_key(self):
        with pytest.raises(ValueError, match="exactly these keys"):
            validate_weights({"skill": 1.0, "bogus": 0.0})
