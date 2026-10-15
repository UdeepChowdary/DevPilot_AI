"""
Tests for utils/interview_coach.py and generate_interview_pdf()
Covers: question generation, communication analysis, rubric answer scoring,
session aggregation, and PDF generation.
"""

import pytest
from utils.interview_coach import (
    generate_interview_questions,
    analyze_communication_delivery,
    evaluate_candidate_answer,
    summarize_interview_session,
    _extract_tech_keywords_from_context,
)
from utils.pdf_generator import generate_interview_pdf


# ─── 1. Question Generation Tests ─────────────────────────────────────────────

class TestQuestionGeneration:
    def test_generates_requested_number_of_questions(self):
        questions = generate_interview_questions(num_questions=3)
        assert len(questions) == 3

    def test_question_schema_complete(self):
        questions = generate_interview_questions(num_questions=2)
        for q in questions:
            assert "id" in q
            assert "category" in q
            assert "question" in q
            assert "context_reason" in q
            assert "key_expectations" in q
            assert isinstance(q["key_expectations"], list)
            assert len(q["key_expectations"]) > 0

    def test_tech_slotting_from_resume_context(self):
        context = "Proficient in Go, React, and MongoDB for cloud microservices."
        tech_map = _extract_tech_keywords_from_context(context)
        assert tech_map["tech_lang"] == "Go"
        assert tech_map["tech_framework"] == "React"
        assert tech_map["tech_db"] == "Mongodb"

    def test_frontend_role_selects_frontend_questions(self):
        questions = generate_interview_questions(
            role="Frontend Engineer",
            category_focus="Deep Technical Architecture & System Design",
            num_questions=2,
        )
        assert any("frontend" in q["category"].lower() or "state" in q["question"].lower() or "performance" in q["question"].lower() for q in questions)

    def test_behavioral_focus_selects_behavioral_questions(self):
        questions = generate_interview_questions(
            category_focus="Behavioral & STAR Leadership Experience",
            num_questions=3,
        )
        assert all("behavioral" in q["category"].lower() or "leadership" in q["category"].lower() or "ownership" in q["category"].lower() or "impact" in q["category"].lower() for q in questions)


# ─── 2. Communication Delivery Analysis ───────────────────────────────────────

class TestCommunicationDelivery:
    def test_word_count_accurate(self):
        text = "Engineered a scalable microservice using FastAPI and Docker to reduce latency."
        result = analyze_communication_delivery(text)
        assert result["word_count"] == 11

    def test_filler_words_detected(self):
        text = "Um, basically, like, we actually decided to migrate the database, you know."
        result = analyze_communication_delivery(text)
        assert result["total_fillers"] >= 4
        assert "um" in result["filler_counts"]
        assert "basically" in result["filler_counts"]
        assert "like" in result["filler_counts"]

    def test_clean_speech_high_score(self):
        text = (
            "We observed high p99 latency during morning peak hours. "
            "I investigated the slow query log and discovered missing indexes on the users table. "
            "I added composite B-tree indexes and enabled connection pooling with PgBouncer. "
            "This decreased query latency by 45% and stabilized throughput at 12,000 requests per second."
        )
        result = analyze_communication_delivery(text)
        assert result["total_fillers"] == 0
        assert result["score"] >= 20

    def test_heavy_fillers_penalized(self):
        clean_text = "I designed the architecture to handle incoming traffic safely."
        filler_text = "Um like basically I uh like designed the architecture to basically like handle traffic."
        clean_res = analyze_communication_delivery(clean_text)
        filler_res = analyze_communication_delivery(filler_text)
        assert filler_res["score"] < clean_res["score"]


# ─── 3. Candidate Answer Evaluation Tests ─────────────────────────────────────

class TestCandidateAnswerEvaluation:
    @pytest.fixture
    def sample_question(self):
        return {
            "id": 1,
            "category": "Technical Architecture",
            "question": "How would you optimize high write latency in PostgreSQL during peak load?",
            "context_reason": "Evaluates database tuning and concurrency under load.",
            "key_expectations": [
                "Profiling slow queries",
                "Index optimization",
                "Connection pooling or buffering",
            ],
            "suggested_framework": "Diagnostics → Mitigations → Architectural Scalability",
        }

    def test_empty_answer_returns_safe_low_score(self, sample_question):
        result = evaluate_candidate_answer(sample_question, "")
        assert result["overall_score"] <= 20
        assert "areas_to_improve" in result
        assert len(result["areas_to_improve"]) > 0

    def test_strong_answer_scores_high(self, sample_question):
        answer = (
            "Initially, our database was experiencing write contention during peak sales. "
            "Tasked with stabilizing the pipeline, I first used EXPLAIN ANALYZE to identify unindexed foreign keys "
            "and lock timeouts. I implemented Redis as a write buffer with Celery workers for asynchronous bulk inserts. "
            "As a result, write latency dropped by 55% from 400ms to 180ms, scaling our pipeline to 25k concurrent users. "
            "The main tradeoff was eventual consistency, which was acceptable for this analytics payload."
        )
        result = evaluate_candidate_answer(sample_question, answer)
        assert result["overall_score"] >= 75
        assert result["dimension_scores"]["technical_depth"] >= 15
        assert result["dimension_scores"]["structure"] >= 15
        assert result["dimension_scores"]["tradeoffs_metrics"] >= 15
        assert len(result["strengths"]) > 0

    def test_dimension_scores_sum_correctly(self, sample_question):
        answer = "I developed the service and added redis cache to optimize response times."
        result = evaluate_candidate_answer(sample_question, answer)
        dims = result["dimension_scores"]
        total = dims["technical_depth"] + dims["structure"] + dims["communication"] + dims["tradeoffs_metrics"]
        assert result["overall_score"] == min(max(total, 0), 100)

    def test_scores_never_exceed_bounds(self, sample_question):
        long_answer = "Architecture and database query cache latency redis scale index docker testing " * 20
        long_answer += " reduced by 50% from 200ms to 100ms for 10k users. Tradeoff was memory usage."
        result = evaluate_candidate_answer(sample_question, long_answer)
        assert 0 <= result["overall_score"] <= 100
        for dim_val in result["dimension_scores"].values():
            assert 0 <= dim_val <= 25


# ─── 4. Session Aggregation Tests ─────────────────────────────────────────────

class TestSessionAggregation:
    def test_empty_evaluations_handled(self):
        summary = summarize_interview_session([])
        assert summary["total_score"] == 0
        assert summary["questions_completed"] == 0

    def test_summarizes_multiple_evaluations(self):
        evals = [
            {
                "question_id": 1,
                "question": "Question 1",
                "candidate_answer": "Answer 1",
                "overall_score": 80,
                "verdict": "Hire",
                "dimension_scores": {
                    "technical_depth": 20,
                    "structure": 20,
                    "communication": 20,
                    "tradeoffs_metrics": 20,
                },
                "strengths": ["Clear technical articulation"],
                "areas_to_improve": ["Add metrics"],
                "ideal_answer": "Ideal 1",
            },
            {
                "question_id": 2,
                "question": "Question 2",
                "candidate_answer": "Answer 2",
                "overall_score": 90,
                "verdict": "Strong Hire",
                "dimension_scores": {
                    "technical_depth": 24,
                    "structure": 22,
                    "communication": 22,
                    "tradeoffs_metrics": 22,
                },
                "strengths": ["Excellent STAR structure"],
                "areas_to_improve": ["Elaborate on edge cases"],
                "ideal_answer": "Ideal 2",
            },
        ]
        summary = summarize_interview_session(evals, role="Backend Engineer")
        assert summary["total_score"] == 85
        assert summary["questions_completed"] == 2
        assert "Offer Caliber" in summary["grade"]
        assert len(summary["all_strengths"]) >= 2


# ─── 5. PDF Generation Tests ──────────────────────────────────────────────────

class TestInterviewPDFGeneration:
    def test_generates_valid_pdf_bytes(self):
        evals = [
            {
                "question_id": 1,
                "question": "How would you handle caching invalidation?",
                "candidate_answer": "I used Redis cache-aside with a 5-minute TTL and event-driven invalidation.",
                "overall_score": 84,
                "verdict": "Strong Hire",
                "dimension_scores": {
                    "technical_depth": 22,
                    "structure": 21,
                    "communication": 21,
                    "tradeoffs_metrics": 20,
                },
                "strengths": ["Good cache-aside explanation"],
                "areas_to_improve": ["Mention thundering herd problem"],
                "ideal_answer": "Ideal cache invalidation approach using pub-sub.",
            }
        ]
        summary = summarize_interview_session(evals, role="Backend Engineer", company_style="FAANG")
        pdf_bytes = generate_interview_pdf(summary)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")
