"""
Tests for utils/placement_tracker.py and Placement Dossier PDF generation.
"""

import pytest
import json
from utils.placement_tracker import (
    calculate_placement_readiness,
    calculate_milestone_progress,
    calculate_pipeline_analytics,
    get_sample_pipeline,
    DEFAULT_MILESTONES,
    export_pipeline_json,
    import_pipeline_json,
    export_pipeline_csv,
    COMPANY_TIERS,
)
from utils.pdf_generator import generate_placement_dossier_pdf


class TestPlacementScoring:
    """Test unified placement readiness scoring and tier matching."""

    def test_all_strong_scores_yield_elite_grade(self):
        res = calculate_placement_readiness(
            resume_score=92,
            github_score=88,
            interview_score=90,
            leetcode_score=95,
        )
        assert res["composite_score"] >= 90
        assert res["grade"] == "A+"
        assert "Elite" in res["grade_label"]
        assert res["tested_count"] == 4
        assert len(res["strengths"]) > 0

    def test_low_scores_yield_developing_or_risk_grade(self):
        res = calculate_placement_readiness(
            resume_score=45,
            github_score=40,
            interview_score=50,
            leetcode_score=35,
        )
        assert res["composite_score"] < 50
        assert res["grade"] == "D"
        assert len(res["bottlenecks"]) > 0

    def test_untested_modules_fallback_to_baseline(self):
        res = calculate_placement_readiness(
            resume_score=85,
            github_score=None,
            interview_score=None,
            leetcode_score=None,
        )
        assert res["tested_count"] == 1
        assert res["pillars"]["resume"]["tested"] is True
        assert res["pillars"]["github"]["tested"] is False
        assert res["pillars"]["github"]["score"] == 50
        assert 0 <= res["composite_score"] <= 100

    def test_custom_weights_affect_composite_score(self):
        # Heavy weight on LeetCode (80%) vs balanced
        res_heavy_lc = calculate_placement_readiness(
            resume_score=50,
            github_score=50,
            interview_score=50,
            leetcode_score=100,
            custom_weights={"resume": 0.05, "github": 0.05, "interview": 0.1, "leetcode": 0.8},
        )
        assert res_heavy_lc["composite_score"] >= 85

    def test_score_never_exceeds_100_or_below_0(self):
        res_max = calculate_placement_readiness(100, 100, 100, 100)
        assert res_max["composite_score"] == 100

        res_min = calculate_placement_readiness(0, 0, 0, 0)
        assert res_min["composite_score"] == 0

    def test_tier_benchmarks_properly_evaluated(self):
        tier_faang = "Tier-1 (FAANG / Quant / HFT / Top Unicorn)"
        res_t1 = calculate_placement_readiness(85, 80, 85, 90, target_tier=tier_faang)
        assert "READY" in res_t1["tier_verdict"]

        tier_t3 = "Tier-3 (Enterprise IT / Tech Services / Scaleups)"
        res_t3 = calculate_placement_readiness(65, 55, 60, 55, target_tier=tier_t3)
        assert "READY" in res_t3["tier_verdict"]


class TestMilestonePlanner:
    """Test milestone completion tracking and category breakdowns."""

    def test_empty_milestones_handled(self):
        res = calculate_milestone_progress([])
        assert res["total"] == 0
        assert res["completed"] == 0
        assert res["pct"] == 0

    def test_milestone_progress_calculation(self):
        milestones = [
            {"id": "1", "category": "Resume", "title": "M1", "completed": True},
            {"id": "2", "category": "Resume", "title": "M2", "completed": False},
            {"id": "3", "category": "DSA", "title": "M3", "completed": True},
            {"id": "4", "category": "DSA", "title": "M4", "completed": True},
        ]
        prog = calculate_milestone_progress(milestones)
        assert prog["total"] == 4
        assert prog["completed"] == 3
        assert prog["pct"] == 75
        assert prog["by_category"]["Resume"]["pct"] == 50
        assert prog["by_category"]["DSA"]["pct"] == 100


class TestPipelineAnalytics:
    """Test application pipeline analytics, funnel metrics, and imports/exports."""

    def test_empty_pipeline_analytics(self):
        analytics = calculate_pipeline_analytics([])
        assert analytics["total"] == 0
        assert analytics["interviews"] == 0
        assert analytics["interview_rate"] == 0.0

    def test_sample_pipeline_analytics(self):
        sample = get_sample_pipeline()
        analytics = calculate_pipeline_analytics(sample)
        assert analytics["total"] == 6
        assert analytics["interviews"] >= 3
        assert analytics["offers"] == 1
        assert analytics["rejected"] == 1
        assert analytics["interview_rate"] > 0

    def test_export_and_import_pipeline_json(self):
        sample = get_sample_pipeline()
        json_str = export_pipeline_json(sample)
        assert isinstance(json_str, str)

        imported = import_pipeline_json(json_str)
        assert len(imported) == len(sample)
        assert imported[0]["company"] == sample[0]["company"]

    def test_import_pipeline_json_validation(self):
        with pytest.raises(ValueError):
            import_pipeline_json("{\"not\": \"a list\"}")

        with pytest.raises(ValueError):
            import_pipeline_json("[{\"no_company\": 123}]")

    def test_export_pipeline_csv(self):
        sample = get_sample_pipeline()
        csv_str = export_pipeline_csv(sample)
        assert "company,role,tier" in csv_str
        assert "Google" in csv_str


class TestPlacementDossierPDF:
    """Test PDF generation for Placement Dossier."""

    def test_generates_valid_pdf_bytes(self):
        readiness = calculate_placement_readiness(85, 80, 82, 88)
        milestones = calculate_milestone_progress([dict(m) for m in DEFAULT_MILESTONES])
        sample_apps = get_sample_pipeline()
        analytics = calculate_pipeline_analytics(sample_apps)

        pdf_bytes = generate_placement_dossier_pdf(
            candidate_name="Alex Mercer",
            readiness=readiness,
            milestones_progress=milestones,
            pipeline_analytics=analytics,
            applications=sample_apps,
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")
