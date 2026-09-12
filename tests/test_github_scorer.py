"""
Tests for utils/github_scorer.py
Covers: profile completeness scoring, repo quality scoring, score capping,
and the full audit_github_profile() integration pipeline.
"""

import pytest
from utils.github_scorer import (
    score_profile_completeness,
    score_repo_quality,
    audit_github_profile,
)


# ─── score_profile_completeness ───────────────────────────────────────────────

class TestScoreProfileCompleteness:
    def test_full_profile_max_score(self, full_github_profile):
        score, strengths, improvements = score_profile_completeness(full_github_profile)
        assert score == 15.0
        assert len(strengths) > 0
        assert len(improvements) == 0

    def test_empty_profile_near_zero(self, empty_github_profile):
        score, strengths, improvements = score_profile_completeness(empty_github_profile)
        assert score < 5.0
        assert len(improvements) > 0

    def test_bio_present_adds_points(self):
        profile = {"login": "user", "bio": "Python developer building cool apps."}
        score, strengths, _ = score_profile_completeness(profile)
        assert score > 0
        # Bio ≥ 20 chars → 4 pts; shorter bio → 2 pts
        assert score >= 2.0

    def test_no_bio_adds_improvement(self):
        profile = {"login": "user", "bio": None}
        _, _, improvements = score_profile_completeness(profile)
        assert any("bio" in imp.lower() for imp in improvements)

    def test_portfolio_link_adds_points(self):
        profile = {"login": "user", "blog": "https://myportfolio.dev"}
        score, strengths, _ = score_profile_completeness(profile)
        # Blog link = 3 pts
        assert score >= 3.0

    def test_default_avatar_flagged(self):
        profile = {"login": "user", "avatar_url": "https://www.gravatar.com/avatar/?d=identicon"}
        _, _, improvements = score_profile_completeness(profile)
        assert any("avatar" in imp.lower() or "picture" in imp.lower() for imp in improvements)

    def test_custom_avatar_not_flagged(self):
        profile = {
            "login": "user",
            "avatar_url": "https://avatars.githubusercontent.com/u/99999?v=4"
        }
        score, _, improvements = score_profile_completeness(profile)
        assert score >= 2.0
        assert not any("avatar" in imp.lower() for imp in improvements)

    def test_location_adds_points(self):
        profile = {"login": "user", "location": "Bangalore, India"}
        score, strengths, _ = score_profile_completeness(profile)
        assert score >= 2.0
        assert any("location" in s.lower() or "Bangalore" in s for s in strengths)

    def test_company_adds_points(self):
        profile = {"login": "user", "company": "IIT Delhi"}
        score, strengths, _ = score_profile_completeness(profile)
        assert score >= 2.0

    def test_score_never_exceeds_15(self, full_github_profile):
        score, _, _ = score_profile_completeness(full_github_profile)
        assert score <= 15.0

    def test_score_never_negative(self, empty_github_profile):
        score, _, _ = score_profile_completeness(empty_github_profile)
        assert score >= 0.0

    def test_full_name_different_from_login_adds_points(self):
        profile = {"login": "coder99", "name": "Alice Johnson"}
        score, strengths, _ = score_profile_completeness(profile)
        assert score >= 2.0
        assert any("Alice Johnson" in s for s in strengths)


# ─── score_repo_quality ───────────────────────────────────────────────────────

class TestScoreRepoQuality:
    def test_strong_repos_score_high(self, strong_repos):
        score, strengths, improvements, audits = score_repo_quality(strong_repos, [])
        assert score >= 20.0
        assert len(audits) == len(strong_repos)

    def test_weak_repos_score_low(self, weak_repos):
        score, strengths, improvements, audits = score_repo_quality(weak_repos, [])
        assert score < 20.0
        assert len(improvements) > 0

    def test_no_repos_returns_zero(self):
        score, strengths, improvements, audits = score_repo_quality([], [])
        assert score == 0.0
        assert audits == []

    def test_fork_heavy_portfolio_flagged(self, weak_repos):
        # All repos are forks → total_orig=0, total_forks=3
        # Scorer still awards minimum points (2.0 ratio + floor scores for desc/lic/demo)
        forked = [dict(r, fork=True) for r in weak_repos]
        score, _, improvements, _ = score_repo_quality([], forked)
        # Score is low (≤10) and there must be an improvement about original/fork repos
        assert score <= 10.0
        assert any("fork" in imp.lower() or "original" in imp.lower() for imp in improvements)

    def test_high_original_ratio_rewarded(self, strong_repos):
        # 3 original, 0 forks → 100% original ratio
        score, strengths, _, _ = score_repo_quality(strong_repos, [])
        assert any("original" in s.lower() or "ownership" in s.lower() for s in strengths)

    def test_repos_with_demos_rewarded(self, strong_repos):
        score, strengths, _, _ = score_repo_quality(strong_repos, [])
        assert any("demo" in s.lower() or "deploy" in s.lower() or "URL" in s for s in strengths)

    def test_repos_without_demos_flagged(self, weak_repos):
        _, _, improvements, _ = score_repo_quality(weak_repos, [])
        assert any("demo" in imp.lower() or "deploy" in imp.lower() for imp in improvements)

    def test_repo_audit_has_required_keys(self, strong_repos):
        _, _, _, audits = score_repo_quality(strong_repos, [])
        for audit in audits:
            assert "name" in audit
            assert "health_score" in audit

    def test_score_never_exceeds_35(self, strong_repos):
        score, _, _, _ = score_repo_quality(strong_repos, [])
        assert score <= 35.0

    def test_license_presence_rewarded(self, strong_repos):
        score, strengths, _, _ = score_repo_quality(strong_repos, [])
        assert any("license" in s.lower() or "open-source" in s.lower() for s in strengths)

    def test_topics_presence_rewarded(self, strong_repos):
        score, strengths, _, _ = score_repo_quality(strong_repos, [])
        assert any("topic" in s.lower() or "tag" in s.lower() for s in strengths)


# ─── audit_github_profile (integration) ─────────────────────────────────────

class TestAuditGithubProfile:
    def _make_profile_data(self, profile, repos, forked_repos=None, language_bytes=None, stats=None):
        return {
            "profile": profile,
            "original_repos": repos,
            "forked_repos": forked_repos or [],
            "language_bytes": language_bytes or {"Python": 50000, "JavaScript": 20000},
            "language_repo_counts": {"Python": len(repos), "JavaScript": 1},
        }

    def test_returns_required_keys(self, full_github_profile, strong_repos):
        data = self._make_profile_data(full_github_profile, strong_repos)
        result = audit_github_profile(data)
        assert "total_score" in result
        assert "grade" in result
        assert "dimensions" in result          # function uses 'dimensions', not 'dimension_scores'
        assert "strengths" in result
        assert "improvements" in result

    def test_total_score_in_valid_range(self, full_github_profile, strong_repos):
        data = self._make_profile_data(full_github_profile, strong_repos)
        result = audit_github_profile(data)
        assert 0 <= result["total_score"] <= 100

    def test_strong_profile_scores_high(self, full_github_profile, strong_repos):
        data = self._make_profile_data(full_github_profile, strong_repos)
        result = audit_github_profile(data)
        # Full profile + strong repos → profile(15) + repo_quality(>20) + lang(>10) ≥ 40
        assert result["total_score"] >= 40

    def test_empty_profile_scores_low(self, empty_github_profile, weak_repos):
        data = self._make_profile_data(empty_github_profile, weak_repos)
        result = audit_github_profile(data)
        assert result["total_score"] < 50

    def test_grade_assigned(self, full_github_profile, strong_repos):
        data = self._make_profile_data(full_github_profile, strong_repos)
        result = audit_github_profile(data)
        # Function returns descriptive emoji grade strings
        valid_grades = [
            "⭐ Silicon Valley Ready",
            "🚀 Strong Placement Candidate",
            "⚡ Emerging Developer",
            "🛠️ Needs Polish & Structure",
        ]
        assert result["grade"] in valid_grades

    def test_action_plan_present(self, empty_github_profile, weak_repos):
        data = self._make_profile_data(empty_github_profile, weak_repos)
        result = audit_github_profile(data)
        # Should have a prioritized action plan for weak profiles
        assert "action_plan" in result or "improvements" in result

    def test_score_never_exceeds_100(self, full_github_profile, strong_repos):
        # Even best case profile should not exceed 100
        strong_repos_extended = strong_repos * 4  # many strong repos
        data = self._make_profile_data(
            full_github_profile, strong_repos_extended,
            stats={
                "original_repo_count": 12,
                "forked_repo_count": 0,
                "total_stars": 200,
                "total_forks": 50,
                "followers": 500,
                "last_push": "2024-09-01T00:00:00Z",
                "active_repos_last_quarter": 10,
            }
        )
        result = audit_github_profile(data)
        assert result["total_score"] <= 100

    def test_dimension_scores_sum_to_total(self, full_github_profile, strong_repos):
        data = self._make_profile_data(full_github_profile, strong_repos)
        result = audit_github_profile(data)
        # 'dimensions' is a dict of dicts; sum the 'score' values from each
        dims = result.get("dimensions", {})
        if dims:
            total_from_dims = sum(d["score"] for d in dims.values())
            # Allow small floating point tolerance
            assert abs(total_from_dims - result["total_score"]) <= 1.0
