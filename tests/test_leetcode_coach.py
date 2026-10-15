"""
Tests for utils/leetcode_coach.py and generate_leetcode_pdf()
Covers: 8-pillar scoring engine, radar normalization, weak-pattern diagnostics,
practice roadmap generation, code complexity heuristics, and PDF report export.
"""

import pytest
from utils.leetcode_coach import (
    audit_algorithmic_readiness,
    generate_practice_roadmap,
    analyze_code_complexity,
    ALGORITHMIC_PILLARS,
)
from utils.pdf_generator import generate_leetcode_pdf


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def strong_leetcode_stats():
    return {
        "username": "algo_master",
        "ranking": 45000,
        "reputation": 120,
        "total_solved": 320,
        "easy_solved": 90,
        "medium_solved": 180,
        "hard_solved": 50,
        "pillar_counts": {
            "Arrays & Hashing": 55,
            "Two Pointers & Sliding Window": 40,
            "Binary Search & Divide/Conquer": 30,
            "Trees & Binary Search Trees": 45,
            "Graphs, BFS & DFS": 38,
            "Dynamic Programming & Recursion": 42,
            "Heaps & Priority Queues": 25,
            "Backtracking & Greedy": 25,
        },
    }


@pytest.fixture
def weak_leetcode_stats():
    return {
        "username": "beginner_coder",
        "ranking": 950000,
        "reputation": 0,
        "total_solved": 25,
        "easy_solved": 22,
        "medium_solved": 3,
        "hard_solved": 0,
        "pillar_counts": {
            "Arrays & Hashing": 15,
            "Two Pointers & Sliding Window": 4,
            "Binary Search & Divide/Conquer": 2,
            "Trees & Binary Search Trees": 2,
            "Graphs, BFS & DFS": 1,
            "Dynamic Programming & Recursion": 1,
            "Heaps & Priority Queues": 0,
            "Backtracking & Greedy": 0,
        },
    }


# ─── 1. Algorithmic Readiness Scoring Tests ───────────────────────────────────

class TestAlgorithmicScoring:
    def test_strong_profile_scores_high(self, strong_leetcode_stats):
        result = audit_algorithmic_readiness(strong_leetcode_stats)
        assert result["total_score"] >= 75
        assert "FAANG" in result["grade"] or "Placement" in result["grade"]
        assert len(result["strengths"]) > 0

    def test_weak_profile_scores_low(self, weak_leetcode_stats):
        result = audit_algorithmic_readiness(weak_leetcode_stats)
        assert result["total_score"] <= 45
        assert len(result["blind_spots"]) > 0

    def test_score_never_exceeds_100(self, strong_leetcode_stats):
        result = audit_algorithmic_readiness(strong_leetcode_stats)
        assert 0 <= result["total_score"] <= 100

    def test_radar_data_has_all_8_pillars(self, strong_leetcode_stats):
        result = audit_algorithmic_readiness(strong_leetcode_stats)
        radar = result["radar_data"]
        assert len(radar) == 8
        pillars_in_radar = [item["pillar"] for item in radar]
        for p in ALGORITHMIC_PILLARS:
            assert p in pillars_in_radar

    def test_dimensions_have_5_components(self, strong_leetcode_stats):
        result = audit_algorithmic_readiness(strong_leetcode_stats)
        dims = result["dimensions"]
        assert len(dims) == 5
        for d in dims.values():
            assert "score" in d
            assert "max" in d
            assert 0 <= d["score"] <= d["max"]


# ─── 2. Practice Roadmap Generator Tests ──────────────────────────────────────

class TestRoadmapGenerator:
    def test_generates_non_empty_roadmap(self, weak_leetcode_stats):
        roadmap = generate_practice_roadmap(weak_leetcode_stats, track="FAANG / Big Tech 75")
        assert len(roadmap) > 0
        for prob in roadmap:
            assert "name" in prob
            assert "difficulty" in prob
            assert "pillar" in prob
            assert "pattern" in prob
            assert "url" in prob

    def test_prioritizes_weak_pillars_first(self, weak_leetcode_stats):
        # In weak_leetcode_stats, DP/Graphs/Heaps have 0-1 solved, while Arrays has 15
        roadmap = generate_practice_roadmap(weak_leetcode_stats, track="FAANG / Big Tech 75")
        # Top problem should NOT be Arrays
        top_problem = roadmap[0]
        assert top_problem["pillar"] in ["Heaps & Priority Queues", "Backtracking & Greedy", "Graphs, BFS & DFS", "Dynamic Programming & Recursion"]

    def test_supports_different_tracks(self, strong_leetcode_stats):
        for track in ["FAANG / Big Tech 75", "FinTech & Low-Latency", "Placement Sprint (Foundations)"]:
            roadmap = generate_practice_roadmap(strong_leetcode_stats, track=track)
            assert len(roadmap) > 0


# ─── 3. Code Complexity Analyzer Tests ────────────────────────────────────────

class TestCodeComplexityAnalyzer:
    def test_detects_nested_loops_quadratic(self):
        code = """
        def twoSum(nums, target):
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    if nums[i] + nums[j] == target:
                        return [i, j]
            return []
        """
        analysis = analyze_code_complexity(code)
        assert analysis["time_complexity"] == "O(N^2)"
        assert not analysis["is_optimal"]
        assert "O(N)" in analysis["optimization_tip"]

    def test_detects_two_pointers_linear(self):
        code = """
        def isPalindrome(s):
            left, right = 0, len(s) - 1
            while left < right:
                if s[left] != s[right]:
                    return False
                left += 1
                right -= 1
            return True
        """
        analysis = analyze_code_complexity(code)
        assert analysis["time_complexity"] == "O(N)"
        assert analysis["is_optimal"]

    def test_detects_sorting_n_log_n(self):
        code = """
        def findContentChildren(g, s):
            g.sort()
            s.sort()
            return 0
        """
        analysis = analyze_code_complexity(code)
        assert "log" in analysis["time_complexity"].lower()

    def test_empty_code_safe_fallback(self):
        analysis = analyze_code_complexity("")
        assert analysis["time_complexity"] == "N/A"
        assert analysis["is_optimal"]


# ─── 4. PDF Generation Tests ──────────────────────────────────────────────────

class TestLeetCodePDFGeneration:
    def test_generates_valid_pdf_bytes(self, strong_leetcode_stats):
        audit = audit_algorithmic_readiness(strong_leetcode_stats)
        roadmap = generate_practice_roadmap(strong_leetcode_stats)
        pdf_bytes = generate_leetcode_pdf(strong_leetcode_stats, audit, roadmap)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")
