"""
Tests for utils/ats_scorer.py
Covers: keyword scoring, impact scoring, section scoring, length scoring,
formatting scoring, quantification detection, and total score capping.
"""

import pytest
from utils.ats_scorer import (
    score_resume,
    _score_keyword_match,
    _score_impact,
    _score_sections,
    _score_length,
    _score_formatting,
    _count_quantifications,
    _count_action_verbs,
    _count_weak_verbs,
)


# ─── _count_quantifications ───────────────────────────────────────────────────

class TestCountQuantifications:
    def test_percentage(self):
        assert _count_quantifications("improved performance by 45%") >= 1

    def test_dollar_amount(self):
        assert _count_quantifications("saved $50k in operational costs") >= 1

    def test_multiplier(self):
        assert _count_quantifications("scaled throughput by 3x") >= 1

    def test_milliseconds(self):
        assert _count_quantifications("reduced latency from 500ms to 120ms") >= 1

    def test_user_scale(self):
        assert _count_quantifications("serving 10k users daily") >= 1

    def test_multiple_metrics_no_double_count(self):
        # "reduced by 45%" should count as ONE metric, not two
        count = _count_quantifications("reduced response time by 45%")
        assert count >= 1
        assert count <= 2  # Should not be inflated

    def test_no_false_positives_year(self):
        # A year like "2023" should NOT count as a quantified metric
        # Years alone are not quantified achievements
        text = "B.Tech Computer Science 2020-2024"
        count = _count_quantifications(text)
        assert count == 0

    def test_empty_text(self):
        assert _count_quantifications("") == 0


# ─── _count_action_verbs / _count_weak_verbs ─────────────────────────────────

class TestVerbCounting:
    def test_strong_verbs_counted(self):
        text = "Engineered, Optimized, Spearheaded, Deployed, Architected the system"
        assert _count_action_verbs(text) >= 5

    def test_weak_verbs_counted(self):
        text = "Helped the team. Assisted with development. Worked on the project."
        assert _count_weak_verbs(text) >= 3

    def test_no_overlap(self):
        # A word should not count as both strong and weak
        strong = _count_action_verbs("implemented the feature")
        weak = _count_weak_verbs("implemented the feature")
        assert not (strong > 0 and weak > 0)


# ─── _score_keyword_match ─────────────────────────────────────────────────────

class TestScoreKeywordMatch:
    def test_with_matching_jd_scores_high(self):
        resume = "Developed REST APIs using FastAPI and Python with PostgreSQL database integration."
        jd = "Looking for Python developer with FastAPI, REST API, and PostgreSQL experience."
        result = _score_keyword_match(resume, jd)
        assert result["score"] >= 10  # Strong overlap should yield reasonable score
        assert result["max"] == 30

    def test_with_no_jd_returns_vocab_score(self):
        resume = "Developed REST APIs using FastAPI Python PostgreSQL Redis Docker Kubernetes AWS."
        result = _score_keyword_match(resume, None)
        assert result["max"] == 30
        assert result["score"] >= 10
        assert "Vocabulary" in result["label"] or "Keyword" in result["label"]

    def test_with_empty_jd_treated_as_no_jd(self):
        result = _score_keyword_match("some resume text", "")
        assert result["max"] == 30

    def test_score_never_exceeds_max(self):
        resume = "Python FastAPI PostgreSQL Docker Kubernetes AWS React TypeScript Go Rust Scala Haskell"
        jd = "Python FastAPI PostgreSQL Docker Kubernetes AWS React TypeScript Go Rust Scala Haskell"
        result = _score_keyword_match(resume, jd)
        assert result["score"] <= result["max"]


# ─── _score_impact ────────────────────────────────────────────────────────────

class TestScoreImpact:
    def test_strong_resume_scores_high(self, sample_resume_text):
        result = _score_impact(sample_resume_text)
        assert result["score"] > 10
        assert result["max"] == 25

    def test_weak_resume_scores_low(self, sample_resume_short):
        result = _score_impact(sample_resume_short)
        assert result["score"] < 15  # few verbs, no metrics

    def test_weak_verb_penalty_applied(self):
        text = "Helped the team. Assisted with development. Worked on the project."
        result = _score_impact(text)
        assert result["weak_verbs"] >= 3

    def test_quantification_counted(self, sample_resume_text):
        result = _score_impact(sample_resume_text)
        assert result["quantifications"] >= 3  # sample has %, x, users, etc.

    def test_action_verbs_counted(self, sample_resume_text):
        result = _score_impact(sample_resume_text)
        assert result["action_verbs"] >= 5

    def test_score_never_negative(self):
        result = _score_impact("helped assisted worked used")
        assert result["score"] >= 0

    def test_score_never_exceeds_25(self):
        text = " ".join(["Engineered Optimized Architected Deployed Built Spearheaded Automated"] * 10)
        text += " reduced by 90% saved $100k scaled to 1M users improved 3x latency 200ms"
        result = _score_impact(text)
        assert result["score"] <= 25


# ─── _score_sections ─────────────────────────────────────────────────────────

class TestScoreSections:
    def test_all_sections_present_max_score(self):
        sections = {"experience", "education", "skills", "projects"}
        result = _score_sections(sections)
        assert result["score"] == 20
        assert result["missing"] == []

    def test_missing_sections_penalized(self):
        sections = {"experience", "education"}  # missing skills, projects
        result = _score_sections(sections)
        assert result["score"] < 20
        assert len(result["missing"]) == 2

    def test_empty_sections_zero_score(self):
        result = _score_sections(set())
        assert result["score"] == 0
        assert len(result["missing"]) == 4

    def test_extra_sections_not_penalized(self):
        # Having extra sections like "certifications" shouldn't hurt
        sections = {"experience", "education", "skills", "projects", "certifications", "summary"}
        result = _score_sections(sections)
        assert result["score"] == 20


# ─── _score_length ────────────────────────────────────────────────────────────

class TestScoreLength:
    def test_ideal_length_full_score(self):
        text = " ".join(["word"] * 500)  # 500 words = ideal
        result = _score_length(text)
        assert result["score"] == 15

    def test_too_short_reduced_score(self):
        text = " ".join(["word"] * 100)  # very short
        result = _score_length(text)
        assert result["score"] < 15

    def test_too_long_reduced_score(self):
        text = " ".join(["word"] * 1500)  # very long
        result = _score_length(text)
        assert result["score"] < 15

    def test_score_in_valid_range(self):
        for word_count in [50, 200, 350, 600, 850, 1000, 1200, 1600]:
            text = " ".join(["word"] * word_count)
            result = _score_length(text)
            assert 0 <= result["score"] <= 15


# ─── _score_formatting ───────────────────────────────────────────────────────

class TestScoreFormatting:
    def test_full_contact_info_and_bullets(self):
        text = (
            "John Doe | john@email.com | +1-555-123-4567 | linkedin.com/in/johndoe\n"
            "• Engineered a scalable system.\n"
            "• Deployed to AWS.\n"
        )
        result = _score_formatting(text)
        assert result["score"] >= 7  # email + phone/linkedin + bullets

    def test_no_contact_no_bullets_low_score(self):
        text = "just some plain text without any formatting or contact information here"
        result = _score_formatting(text)
        assert result["score"] <= 3

    def test_email_gives_points(self):
        text = "Contact: someone@example.com"
        result = _score_formatting(text)
        assert result["score"] >= 2

    def test_linkedin_gives_points(self):
        text = "linkedin.com/in/someone"
        result = _score_formatting(text)
        assert result["score"] >= 2

    def test_score_never_exceeds_10(self):
        text = (
            "john@email.com | +1-555-999-8888 | linkedin.com/in/john\n"
            "• Built things.\n• Deployed stuff.\n• Optimized performance by 40%.\n"
        )
        result = _score_formatting(text)
        assert result["score"] <= 10


# ─── score_resume (integration) ───────────────────────────────────────────────

class TestScoreResume:
    def test_returns_required_keys(self, sample_resume_text, sample_resume_sections):
        result = score_resume(sample_resume_text, None, sample_resume_sections)
        assert "total" in result
        assert "breakdown" in result
        assert "strengths" in result
        assert "weaknesses" in result

    def test_total_in_valid_range(self, sample_resume_text, sample_resume_sections):
        result = score_resume(sample_resume_text, None, sample_resume_sections)
        assert 0 <= result["total"] <= 100

    def test_strong_resume_scores_above_60(self, sample_resume_text, sample_resume_sections):
        result = score_resume(sample_resume_text, None, sample_resume_sections)
        assert result["total"] >= 60

    def test_weak_resume_scores_below_50(self, sample_resume_short):
        result = score_resume(sample_resume_short, None, {})
        assert result["total"] <= 50

    def test_with_jd_produces_keyword_label(self, sample_resume_text, sample_resume_sections):
        jd = "Python FastAPI PostgreSQL Docker Kubernetes engineer with REST API experience"
        result = score_resume(sample_resume_text, jd, sample_resume_sections)
        labels = [b["label"] for b in result["breakdown"]]
        assert any("JD" in l or "Keyword Alignment" in l for l in labels)

    def test_breakdown_has_5_components(self, sample_resume_text, sample_resume_sections):
        result = score_resume(sample_resume_text, None, sample_resume_sections)
        assert len(result["breakdown"]) == 5

    def test_total_never_exceeds_100(self, sample_resume_text, sample_resume_sections):
        # Even with a perfect resume + JD, cap is 100
        jd = sample_resume_text  # Identical text = max TF-IDF similarity
        result = score_resume(sample_resume_text, jd, sample_resume_sections)
        assert result["total"] <= 100

    def test_strengths_and_weaknesses_are_lists(self, sample_resume_text, sample_resume_sections):
        result = score_resume(sample_resume_text, None, sample_resume_sections)
        assert isinstance(result["strengths"], list)
        assert isinstance(result["weaknesses"], list)
