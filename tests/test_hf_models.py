"""
Unit tests for utils/hf_models.py
Tests the Hugging Face Local Neural Engine across all 5 sub-apps:
1. Resume Bullet Enhancer (T5)
2. GitHub Profile Reviewer (Neural Elevator Pitch & Bullets)
3. AI Mock Interview (Neural Question Generation & Rubric Evaluation)
4. LeetCode Coach (Complexity & Asymptotic Optimizer)
5. Placement Readiness (AI Career Strategist & 4-Week Sprint Roadmap)
"""

import pytest
from utils.hf_models import (
    hf_enhance_bullet,
    hf_enhance_bullets_batch,
    hf_generate_github_critique,
    hf_generate_interview_questions,
    hf_evaluate_interview_answer,
    hf_analyze_code_complexity,
    hf_generate_placement_strategy,
    is_hf_available,
)


# ─── 1. Environment & Availability Tests ──────────────────────────────────────

def test_hf_availability():
    """Verify Hugging Face transformers/torch availability flag."""
    avail = is_hf_available()
    assert isinstance(avail, bool)


def test_hf_pipeline_lock_exists():
    """Verify thread-safe lock exists for Hugging Face pipeline caching."""
    import threading
    from utils.hf_models import _PIPELINE_LOCK
    assert isinstance(_PIPELINE_LOCK, type(threading.Lock()))


# ─── 2. Sub-App 1: Resume Bullet Enhancement Tests ────────────────────────────

class TestResumeBulletEnhancement:
    def test_enhance_bullet_improves_weak_bullet(self):
        weak_bullet = "Worked on Python backend and fixed some bugs."
        enhanced = hf_enhance_bullet(weak_bullet)
        assert isinstance(enhanced, str)
        assert len(enhanced) > len(weak_bullet)
        # Should start with a strong action verb
        first_word = enhanced.split()[0].lower()
        assert first_word in [
            "engineered", "architected", "accelerated", "spearheaded",
            "developed", "deployed", "scaled", "automated", "optimized"
        ] or any(c.isdigit() for c in enhanced)

    def test_enhance_bullet_handles_empty_or_short(self):
        assert hf_enhance_bullet("") == ""
        assert hf_enhance_bullet("Hi") == "Hi"

    def test_enhance_bullets_batch(self):
        bullets = [
            "Made an API for user authentication.",
            "Helped with database migration to PostgreSQL.",
            "Wrote unit tests for frontend components.",
        ]
        results = hf_enhance_bullets_batch(bullets)
        assert len(results) == len(bullets)
        for res in results:
            assert isinstance(res, str)
            assert len(res) > 10


# ─── 3. Sub-App 2: GitHub Profile Neural Critique Tests ───────────────────────

class TestGitHubNeuralCritique:
    @pytest.fixture
    def sample_gh_profile(self):
        return {
            "username": "octocat",
            "name": "Octo Cat",
            "bio": "Building distributed systems in Rust and Python.",
            "public_repos": 14,
            "followers": 45,
            "top_languages": [
                {"language": "Python", "bytes": 120000, "percentage": 60.0},
                {"language": "TypeScript", "bytes": 80000, "percentage": 40.0},
            ],
            "repos": [
                {
                    "name": "distributed-cache",
                    "description": "High throughput in-memory cache with Raft consensus",
                    "language": "Python",
                    "stars": 18,
                    "forks": 4,
                    "has_readme": True,
                    "has_license": True,
                },
                {
                    "name": "devpilot-ui",
                    "description": "Interactive developer analytics dashboard",
                    "language": "TypeScript",
                    "stars": 9,
                    "forks": 1,
                    "has_readme": True,
                    "has_license": True,
                },
            ],
        }

    def test_generate_github_critique_schema(self, sample_gh_profile):
        critique = hf_generate_github_critique(sample_gh_profile)
        assert isinstance(critique, dict)
        assert "elevator_pitch" in critique
        assert "top_repo_bullets" in critique
        assert "capstone_recommendations" in critique
        assert "interview_talking_points" in critique
        assert "ai_engine" in critique
        assert "Hugging Face" in critique["ai_engine"]
        assert critique.get("is_ai_generated") is True

    def test_critique_contains_repo_bullets(self, sample_gh_profile):
        critique = hf_generate_github_critique(sample_gh_profile)
        bullets = critique["top_repo_bullets"]
        assert len(bullets) >= 1
        assert "distributed-cache" in bullets[0] or "cache" in bullets[0].lower()

    def test_critique_fallback_on_empty_profile(self):
        critique = hf_generate_github_critique({})
        assert isinstance(critique, dict)
        assert "elevator_pitch" in critique
        assert len(critique["elevator_pitch"]) > 20


# ─── 4. Sub-App 3: Mock Interview Neural Evaluation Tests ────────────────────

class TestInterviewNeuralCoach:
    def test_generate_interview_questions(self):
        resume_ctx = "Full-stack engineer with React, Python, PostgreSQL, and AWS deployment experience."
        questions = hf_generate_interview_questions(
            resume_text=resume_ctx,
            target_tier="FAANG / Tier-1 Tech",
            role="Backend Engineer / Systems",
            num_questions=3,
        )
        assert len(questions) == 3
        for q in questions:
            assert "id" in q
            assert "category" in q
            assert "question" in q
            assert "context_reason" in q
            assert "key_expectations" in q
            assert isinstance(q["key_expectations"], list)
            assert len(q["key_expectations"]) > 0

    def test_evaluate_interview_answer_good(self):
        q_obj = {
            "id": 1,
            "question": "How do you design a resilient caching layer for high read throughput?",
            "key_expectations": ["Cache invalidation", "Latency tradeoffs", "Redis clusters"],
        }
        good_answer = (
            "In our payment service, we faced 45,000 read QPS on product metadata. "
            "I architected a multi-tier caching strategy using local in-memory Guava cache combined with a Redis cluster. "
            "We implemented a Cache-Aside pattern with TTL and asynchronous write-through queues. "
            "This decreased database load by 78% and reduced p99 latency from 140ms down to 18ms."
        )
        result = hf_evaluate_interview_answer(q_obj, good_answer, role="Backend Engineer")
        assert result["overall_score"] >= 70
        assert result["dimension_scores"]["technical_depth"] >= 15
        assert result["dimension_scores"]["tradeoffs_metrics"] >= 15
        assert len(result["strengths"]) > 0
        assert "ai_engine" in result
        assert "Hugging Face" in result["ai_engine"]

    def test_evaluate_interview_answer_short_or_empty(self):
        q_obj = {"id": 1, "question": "Explain consistency models."}
        res_empty = hf_evaluate_interview_answer(q_obj, "")
        assert res_empty["overall_score"] <= 30
        assert "Incomplete" in res_empty["verdict"]


# ─── 5. Sub-App 4: LeetCode Complexity & Pattern Optimizer Tests ──────────────

class TestLeetCodeNeuralOptimizer:
    def test_analyze_quadratic_solution(self):
        nested_code = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
        analysis = hf_analyze_code_complexity(nested_code)
        assert analysis["time_complexity"] == "O(N^2)"
        assert "Nested" in analysis["detected_pattern"] or "Quadratic" in analysis["detected_pattern"]
        assert analysis["is_optimal"] is False
        assert "Hugging Face" in analysis["ai_engine"]

    def test_analyze_linear_two_pointer_solution(self):
        two_pointers = """
def maxArea(height):
    left, right = 0, len(height) - 1
    max_w = 0
    while left < right:
        max_w = max(max_w, min(height[left], height[right]) * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_w
"""
        analysis = hf_analyze_code_complexity(two_pointers)
        assert analysis["time_complexity"] == "O(N)"
        assert "Two Pointer" in analysis["detected_pattern"] or "Linear" in analysis["detected_pattern"]
        assert analysis["is_optimal"] is True


# ─── 6. Sub-App 5: Placement Strategy & Sprint Roadmap Tests ──────────────────

class TestPlacementNeuralStrategist:
    @pytest.fixture
    def sample_placement_data(self):
        return {
            "composite_score": 76,
            "target_tier": "Tier-1 (FAANG / Quant / Top Unicorn)",
            "pillars": {
                "resume": {"name": "Resume ATS", "score": 84, "tested": True},
                "github": {"name": "GitHub Portfolio", "score": 78, "tested": True},
                "interview": {"name": "Mock Interview", "score": 68, "tested": True},
                "leetcode": {"name": "LeetCode DSA", "score": 74, "tested": True},
            },
        }

    def test_generate_placement_strategy_schema(self, sample_placement_data):
        strategy = hf_generate_placement_strategy(sample_placement_data)
        assert isinstance(strategy, dict)
        assert "executive_verdict" in strategy
        assert "strongest_pillar" in strategy
        assert "priority_gap" in strategy
        assert "sprint_plan" in strategy
        assert "recruiter_advice" in strategy
        assert "ai_engine" in strategy
        assert "Hugging Face" in strategy["ai_engine"]
        assert strategy.get("is_ai_generated") is True

    def test_sprint_plan_has_four_weeks(self, sample_placement_data):
        strategy = hf_generate_placement_strategy(sample_placement_data)
        sprint = strategy["sprint_plan"]
        assert len(sprint) == 4
        for idx, week_item in enumerate(sprint, 1):
            assert f"Week {idx}" in week_item["week"]
            assert "focus" in week_item
            assert "action" in week_item
            assert len(week_item["action"]) > 15

    def test_diagnoses_correct_strongest_and_gap(self, sample_placement_data):
        strategy = hf_generate_placement_strategy(sample_placement_data)
        assert "Resume" in strategy["strongest_pillar"]
        assert "Interview" in strategy["priority_gap"]
