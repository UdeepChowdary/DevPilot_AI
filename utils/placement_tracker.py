"""
Placement Tracker & Unified Engineering Readiness Engine -- DevPilot AI
Calculates a holistic Engineering Readiness Score (0-100) combining Resume ATS,
GitHub Portfolio, AI Mock Interview, and LeetCode Algorithmic metrics.
Includes milestone sprint planning, company tier benchmarking, and application pipeline management.
"""

import os
import json
import csv
import io
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional

from utils.gemini_client import ask_json
from utils.hf_models import hf_generate_placement_strategy

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & Benchmarks
# ---------------------------------------------------------------------------

DEFAULT_PILLAR_WEIGHTS = {
    "resume": 0.25,
    "github": 0.25,
    "interview": 0.25,
    "leetcode": 0.25,
}

COMPANY_TIERS = {
    "Tier-1 (FAANG / Quant / HFT / Top Unicorn)": {
        "min_score": 82,
        "resume_min": 80,
        "github_min": 75,
        "interview_min": 80,
        "leetcode_min": 85,
        "desc": "Elite tech bar requiring pristine DSA mastery, clean portfolio, and strong STAR technical delivery.",
    },
    "Tier-2 (High-Growth Unicorn / Mid-Tech Product)": {
        "min_score": 70,
        "resume_min": 72,
        "github_min": 65,
        "interview_min": 70,
        "leetcode_min": 68,
        "desc": "Product-focused companies prioritizing practical engineering, system trade-offs, and solid DSA.",
    },
    "Tier-3 (Enterprise IT / Tech Services / Scaleups)": {
        "min_score": 52,
        "resume_min": 60,
        "github_min": 50,
        "interview_min": 55,
        "leetcode_min": 50,
        "desc": "General engineering roles focusing on core fundamentals, resume completeness, and team communication.",
    },
}

PIPELINE_STAGES = [
    "Wishlist",
    "Applied",
    "OA / Screen",
    "Technical Round",
    "Final Round",
    "Offer Received",
    "Archived / Rejected",
]

STAGE_COLORS = {
    "Wishlist": "#94a3b8",
    "Applied": "#38bdf8",
    "OA / Screen": "#a855f7",
    "Technical Round": "#f59e0b",
    "Final Round": "#ec4899",
    "Offer Received": "#22c55e",
    "Archived / Rejected": "#ef4444",
}


# ---------------------------------------------------------------------------
# Unified Readiness Scoring Engine
# ---------------------------------------------------------------------------

def calculate_placement_readiness(
    resume_score: Optional[float] = None,
    github_score: Optional[float] = None,
    interview_score: Optional[float] = None,
    leetcode_score: Optional[float] = None,
    custom_weights: Optional[Dict[str, float]] = None,
    target_tier: str = "Tier-1 (FAANG / Quant / HFT / Top Unicorn)",
) -> Dict[str, Any]:
    """
    Synthesize scores from all 4 DevPilot AI modules into a single, unified
    Engineering Placement Readiness Score (0-100).
    Gracefully handles uncompleted modules by assigning estimated baselines.
    """
    weights = custom_weights or DEFAULT_PILLAR_WEIGHTS.copy()
    
    # Normalize weights so sum is 1.0
    total_w = sum(weights.values())
    if total_w > 0:
        norm_weights = {k: v / total_w for k, v in weights.items()}
    else:
        norm_weights = DEFAULT_PILLAR_WEIGHTS.copy()

    # Tier benchmark config
    tier_info = COMPANY_TIERS.get(target_tier, COMPANY_TIERS["Tier-1 (FAANG / Quant / HFT / Top Unicorn)"])

    # Pillar definitions
    pillars_def = [
        {
            "id": "resume",
            "name": "Resume ATS & Keywords",
            "score": resume_score,
            "weight": norm_weights.get("resume", 0.25),
            "benchmark": tier_info["resume_min"],
            "icon": "📄",
            "page": "pages/1_Resume_Analyzer.py",
        },
        {
            "id": "github",
            "name": "GitHub Portfolio Readiness",
            "score": github_score,
            "weight": norm_weights.get("github", 0.25),
            "benchmark": tier_info["github_min"],
            "icon": "🐙",
            "page": "pages/2_GitHub_Analyzer.py",
        },
        {
            "id": "interview",
            "name": "Mock Interview Delivery",
            "score": interview_score,
            "weight": norm_weights.get("interview", 0.25),
            "benchmark": tier_info["interview_min"],
            "icon": "🎤",
            "page": "pages/3_Mock_Interview.py",
        },
        {
            "id": "leetcode",
            "name": "LeetCode Algorithmic Mastery",
            "score": leetcode_score,
            "weight": norm_weights.get("leetcode", 0.25),
            "benchmark": tier_info["leetcode_min"],
            "icon": "🎯",
            "page": "pages/4_LeetCode_Coach.py",
        },
    ]

    pillars_output = {}
    weighted_sum = 0.0
    tested_count = 0

    for p in pillars_def:
        raw = p["score"]
        is_tested = raw is not None
        score_val = round(float(raw)) if is_tested else 50  # 50 neutral baseline
        if is_tested:
            tested_count += 1

        gap = p["benchmark"] - score_val
        contribution = round(score_val * p["weight"], 1)
        weighted_sum += score_val * p["weight"]

        # Color token
        if score_val >= p["benchmark"]:
            color = "#22c55e"  # Green
            status = "Placement Ready"
        elif score_val >= p["benchmark"] - 12:
            color = "#f59e0b"  # Amber
            status = "Within Reach"
        else:
            color = "#ef4444"  # Red
            status = "Needs Improvement"

        # Actionable feedback
        if not is_tested:
            advice = f"Run {p['name']} module to replace the 50pt baseline with your real assessment."
        elif score_val >= p["benchmark"]:
            advice = f"Exceeds {target_tier.split()[0]} screening benchmark ({score_val}/{p['benchmark']}). Keep skills sharp."
        elif gap > 0:
            advice = f"Currently {gap} pts below target bar ({score_val}/{p['benchmark']}). Focus sprint here."
        else:
            advice = "Solid performance aligned with candidate cohort expectations."

        pillars_output[p["id"]] = {
            "name": p["name"],
            "score": score_val,
            "weight": p["weight"],
            "weight_pct": int(p["weight"] * 100),
            "contribution": contribution,
            "benchmark": p["benchmark"],
            "gap": gap,
            "tested": is_tested,
            "status": status,
            "color": color,
            "icon": p["icon"],
            "page": p["page"],
            "advice": advice,
        }

    composite_score = min(round(weighted_sum), 100)

    # Grading Scale
    if composite_score >= 90:
        grade = "A+"
        grade_label = "Elite Tier-1 Candidate"
        outlook = "Outstanding readiness across all pillars. High probability of clearing multiple screening and onsite rounds."
    elif composite_score >= 80:
        grade = "A"
        grade_label = "Strong Placement Contender"
        outlook = "Highly competitive profile. Well positioned for Tier-1/Tier-2 offers with minor fine-tuning on bottlenecks."
    elif composite_score >= 68:
        grade = "B"
        grade_label = "Placement Ready"
        outlook = "Demonstrates solid engineering foundations. Capable of clearing technical rounds at high-growth product companies."
    elif composite_score >= 52:
        grade = "C"
        grade_label = "Developing Readiness"
        outlook = "Good baseline with clear vulnerabilities in one or more core pillars that may risk screening elimination."
    else:
        grade = "D"
        grade_label = "High-Risk Foundation"
        outlook = "Candidate requires structured 30-day sprint across multiple dimensions before aggressive application submission."

    # Tier Match Assessment
    min_bar = tier_info["min_score"]
    if composite_score >= min_bar:
        tier_verdict = f"Target Match: READY for {target_tier.split()[0]}"
        tier_badge_color = "#22c55e"
    elif composite_score >= min_bar - 8:
        tier_verdict = f"Target Match: NEAR READY for {target_tier.split()[0]} (-{min_bar - composite_score} pts)"
        tier_badge_color = "#f59e0b"
    else:
        tier_verdict = f"Target Match: GAP for {target_tier.split()[0]} (-{min_bar - composite_score} pts)"
        tier_badge_color = "#ef4444"

    # Identify Strengths & Bottlenecks
    strengths = [
        f"**{p['name']}** ({p['score']}/100) -- {p['status']}"
        for p in pillars_output.values()
        if p["tested"] and p["score"] >= p["benchmark"]
    ]
    bottlenecks = [
        f"**{p['name']}** ({p['score']}/100) -- {p['gap']} pts below target bar ({p['benchmark']})"
        for p in sorted(pillars_output.values(), key=lambda item: item["gap"], reverse=True)
        if p["gap"] > 0
    ]

    # Prioritized Action Items
    action_items = []
    untested = [p for p in pillars_output.values() if not p["tested"]]
    if untested:
        action_items.append(
            f"Run diagnostics for untested modules: {', '.join(p['name'] for p in untested)} to get authentic metrics."
        )

    for p in sorted(pillars_output.values(), key=lambda x: x["gap"], reverse=True):
        if p["gap"] > 0 and p["tested"]:
            action_items.append(f"Close gap in {p['name']}: {p['advice']}")

    if len(action_items) < 3:
        action_items.append("Keep practicing daily active LeetCode streaks and weekly system design reviews.")
        action_items.append("Apply to 5 Tier-2 companies as calibration screens before entering Tier-1 dream loops.")

    return {
        "composite_score": composite_score,
        "grade": grade,
        "grade_label": grade_label,
        "outlook": outlook,
        "target_tier": target_tier,
        "tier_info": tier_info,
        "tier_verdict": tier_verdict,
        "tier_badge_color": tier_badge_color,
        "pillars": pillars_output,
        "tested_count": tested_count,
        "total_pillars": 4,
        "strengths": strengths,
        "bottlenecks": bottlenecks,
        "action_items": action_items[:4],
    }


# ---------------------------------------------------------------------------
# Milestone Sprint Planning
# ---------------------------------------------------------------------------

DEFAULT_MILESTONES: List[Dict[str, Any]] = [
    {
        "id": "m1",
        "category": "Resume & Branding",
        "title": "ATS Score >= 80 on target job description",
        "desc": "Optimize keywords, high-impact action verbs, and section completeness.",
        "priority": "High",
        "completed": False,
    },
    {
        "id": "m2",
        "category": "Resume & Branding",
        "title": "Quantified Google XYZ bullets for top 3 projects",
        "desc": "Include clear latency, throughput, scale, and user metrics in bullet points.",
        "priority": "High",
        "completed": False,
    },
    {
        "id": "m3",
        "category": "GitHub & Portfolio",
        "title": "3+ Repos with README, Architecture Diagram & Live Demo",
        "desc": "Provide verified live URLs (Vercel/Render) and clean architectural documentation.",
        "priority": "Medium",
        "completed": False,
    },
    {
        "id": "m4",
        "category": "GitHub & Portfolio",
        "title": "Add OSI Licenses & Topic tags across public repositories",
        "desc": "Clean up repository metadata to score 80+ on GitHub portfolio hygiene.",
        "priority": "Low",
        "completed": False,
    },
    {
        "id": "m5",
        "category": "DSA & LeetCode",
        "title": "Solve 150+ problems (>= 75 Mediums)",
        "desc": "Establish a balanced problem volume across easy and medium interview questions.",
        "priority": "High",
        "completed": False,
    },
    {
        "id": "m6",
        "category": "DSA & LeetCode",
        "title": "Master Blind 75 / FAANG 75 core patterns",
        "desc": "Two Pointers, Sliding Window, Trees, and Dynamic Programming foundations.",
        "priority": "High",
        "completed": False,
    },
    {
        "id": "m7",
        "category": "DSA & LeetCode",
        "title": "Achieve >= 70 mastery in Graph Theory & Dynamic Programming",
        "desc": "Eliminate the two most lethal blind spots in Tier-1 coding loops.",
        "priority": "Medium",
        "completed": False,
    },
    {
        "id": "m8",
        "category": "Mock Interviews",
        "title": "Complete 3+ Mock Interviews with Score >= 75",
        "desc": "Practice verbal delivery and build confidence in timed environments.",
        "priority": "High",
        "completed": False,
    },
    {
        "id": "m9",
        "category": "Mock Interviews",
        "title": "Eliminate verbal fillers & master STAR structure",
        "desc": "Structure responses into Situation, Task, Action, and Measurable Result.",
        "priority": "Medium",
        "completed": False,
    },
    {
        "id": "m10",
        "category": "Applications & Referrals",
        "title": "Curate list of 30 target companies across Tiers 1, 2, and 3",
        "desc": "Map out career portals, hiring managers, and active opening dates.",
        "priority": "High",
        "completed": False,
    },
    {
        "id": "m11",
        "category": "Applications & Referrals",
        "title": "Reach out to 15 alumni or engineers for warm referrals",
        "desc": "A warm internal referral boosts interview callback rates by up to 4x.",
        "priority": "Medium",
        "completed": False,
    },
    {
        "id": "m12",
        "category": "Applications & Referrals",
        "title": "Submit 25+ targeted applications with tailored ATS resumes",
        "desc": "Maintain consistent application cadence while tracking stages in pipeline.",
        "priority": "High",
        "completed": False,
    },
]


def calculate_milestone_progress(milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall and categorized milestone completion statistics."""
    if not milestones:
        return {"total": 0, "completed": 0, "pct": 0, "by_category": {}}

    total = len(milestones)
    completed = sum(1 for m in milestones if m.get("completed", False))
    pct = round((completed / total) * 100) if total > 0 else 0

    by_category: Dict[str, Dict[str, int]] = {}
    for m in milestones:
        cat = m.get("category", "General")
        if cat not in by_category:
            by_category[cat] = {"total": 0, "completed": 0}
        by_category[cat]["total"] += 1
        if m.get("completed", False):
            by_category[cat]["completed"] += 1

    for cat_data in by_category.values():
        c_tot = cat_data["total"]
        c_done = cat_data["completed"]
        cat_data["pct"] = round((c_done / c_tot) * 100) if c_tot > 0 else 0

    return {
        "total": total,
        "completed": completed,
        "pct": pct,
        "by_category": by_category,
    }


# ---------------------------------------------------------------------------
# Application Pipeline Management & Analytics
# ---------------------------------------------------------------------------

def get_sample_pipeline() -> List[Dict[str, Any]]:
    """Return pre-populated realistic applications for immediate interactive demoing."""
    return [
        {
            "id": "app_1",
            "company": "Google",
            "role": "Software Engineer (L3 / Early Career)",
            "tier": "Tier-1 (FAANG / Quant / HFT / Top Unicorn)",
            "stage": "Technical Round",
            "applied_date": "2026-09-20",
            "compensation": "$185,000 / yr",
            "referral": "Yes (Alumni Senior SWE)",
            "location": "Mountain View, CA / Hybrid",
            "notes": "Cleared OA (2 DSA questions). Round 1 Technical scheduled: Trees & Graphs.",
        },
        {
            "id": "app_2",
            "company": "Stripe",
            "role": "Backend Infrastructure Engineer",
            "tier": "Tier-1 (FAANG / Quant / HFT / Top Unicorn)",
            "stage": "OA / Screen",
            "applied_date": "2026-09-28",
            "compensation": "$190,000 / yr",
            "referral": "No (Direct Portal)",
            "location": "San Francisco, CA / Remote",
            "notes": "CodeSignal assessment received: 4 questions, 70 min limit. Reviewing sliding window.",
        },
        {
            "id": "app_3",
            "company": "Datadog",
            "role": "Software Engineer - Distributed Systems",
            "tier": "Tier-2 (High-Growth Unicorn / Mid-Tech Product)",
            "stage": "Offer Received",
            "applied_date": "2026-09-05",
            "compensation": "$160,000 / yr",
            "referral": "Yes (LinkedIn connection)",
            "location": "New York, NY",
            "notes": "🎉 Offer letter received! Base + equity package. Decision deadline: end of month.",
        },
        {
            "id": "app_4",
            "company": "Uber",
            "role": "Full Stack Engineer (New Grad)",
            "tier": "Tier-2 (High-Growth Unicorn / Mid-Tech Product)",
            "stage": "Applied",
            "applied_date": "2026-10-02",
            "compensation": "$155,000 / yr",
            "referral": "Pending response",
            "location": "Seattle, WA",
            "notes": "Tailored resume with Python, React, and Redis keywords.",
        },
        {
            "id": "app_5",
            "company": "Atlassian",
            "role": "Associate Product Engineer",
            "tier": "Tier-2 (High-Growth Unicorn / Mid-Tech Product)",
            "stage": "Wishlist",
            "applied_date": "2026-10-10",
            "compensation": "$145,000 / yr",
            "referral": "Reaching out this week",
            "location": "Remote",
            "notes": "Targeting team working on Jira Core API platform.",
        },
        {
            "id": "app_6",
            "company": "Adobe",
            "role": "Computer Scientist 1",
            "tier": "Tier-2 (High-Growth Unicorn / Mid-Tech Product)",
            "stage": "Archived / Rejected",
            "applied_date": "2026-08-15",
            "compensation": "$140,000 / yr",
            "referral": "No",
            "location": "San Jose, CA",
            "notes": "Rejected post-resume screen. Action: improved ATS keyword alignment from 64 to 82.",
        },
    ]


def calculate_pipeline_analytics(applications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate key funnel conversion and distribution metrics across applications."""
    if not applications:
        return {
            "total": 0,
            "active": 0,
            "interviews": 0,
            "offers": 0,
            "rejected": 0,
            "interview_rate": 0.0,
            "offer_rate": 0.0,
            "by_stage": {s: 0 for s in PIPELINE_STAGES},
            "by_tier": {},
        }

    total = len(applications)
    by_stage = {s: 0 for s in PIPELINE_STAGES}
    by_tier: Dict[str, int] = {}

    for app in applications:
        stage = app.get("stage", "Wishlist")
        if stage in by_stage:
            by_stage[stage] += 1
        else:
            by_stage["Wishlist"] += 1

        tier = app.get("tier", "Other")
        by_tier[tier] = by_tier.get(tier, 0) + 1

    active = total - by_stage.get("Archived / Rejected", 0) - by_stage.get("Wishlist", 0)
    interviews = (
        by_stage.get("OA / Screen", 0)
        + by_stage.get("Technical Round", 0)
        + by_stage.get("Final Round", 0)
        + by_stage.get("Offer Received", 0)
    )
    offers = by_stage.get("Offer Received", 0)
    rejected = by_stage.get("Archived / Rejected", 0)

    applied_and_beyond = total - by_stage.get("Wishlist", 0)
    interview_rate = (
        round((interviews / applied_and_beyond) * 100, 1)
        if applied_and_beyond > 0
        else 0.0
    )
    offer_rate = (
        round((offers / applied_and_beyond) * 100, 1)
        if applied_and_beyond > 0
        else 0.0
    )

    return {
        "total": total,
        "active": active,
        "interviews": interviews,
        "offers": offers,
        "rejected": rejected,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
        "by_stage": by_stage,
        "by_tier": by_tier,
    }


def export_pipeline_json(applications: List[Dict[str, Any]]) -> str:
    """Export application pipeline list to formatted JSON string."""
    return json.dumps(applications, indent=2)


def import_pipeline_json(json_str: str) -> List[Dict[str, Any]]:
    """Parse JSON string into application pipeline list with validation."""
    data = json.loads(json_str)
    if not isinstance(data, list):
        raise ValueError("Pipeline JSON must be an array of application objects.")
    for idx, item in enumerate(data):
        if not isinstance(item, dict) or "company" not in item:
            raise ValueError(f"Application at index {idx} must be an object with at least a 'company' key.")
        if "id" not in item:
            item["id"] = f"app_{idx+1}_{int(datetime.now().timestamp())}"
        if "stage" not in item or item["stage"] not in PIPELINE_STAGES:
            item["stage"] = "Wishlist"
    return data


def export_pipeline_csv(applications: List[Dict[str, Any]]) -> str:
    """Export applications to CSV string format."""
    output = io.StringIO()
    fieldnames = [
        "company",
        "role",
        "tier",
        "stage",
        "applied_date",
        "compensation",
        "referral",
        "location",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for app in applications:
        writer.writerow(app)
    return output.getvalue()


# ---------------------------------------------------------------------------
# AI Placement Strategy & Career Accelerator
# ---------------------------------------------------------------------------

def generate_placement_strategy(
    placement_data: Dict[str, Any],
    engine: str = "hf",
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an Executive Placement Strategy and Actionable 4-Week Roadmap.
    Supports:
      - 'hf': Hugging Face Local Neural Engine (100% offline, CPU/GPU)
      - 'gemini': Google Gemini 2.0 Flash (Online Cloud LLM)
    """
    if engine == "hf":
        try:
            return hf_generate_placement_strategy(placement_data)
        except Exception as e:
            logger.warning("HF placement strategy fallback: %s", e)

    key = (api_key or "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if key and engine != "offline":
        composite = placement_data.get("composite_score", 65)
        pillars = placement_data.get("pillars", {})
        tier = placement_data.get("target_tier", "Tier-1 (FAANG / Quant / HFT / Top Unicorn)")

        prompt = f"""
You are an Executive Tech Career Coach and Director of University Engineering Placements.
Analyze this candidate's multi-pillar engineering readiness profile and craft a high-impact placement acceleration strategy.

<candidate_profile>
Composite Score: {composite}/100
Target Tier: {tier}
Pillars: {json.dumps(pillars, indent=2)}
</candidate_profile>

Return a valid JSON object matching this schema:
{{
  "executive_verdict": "2-3 sentences assessing current candidacy and tier feasibility.",
  "strongest_pillar": "Pillar name and why it is a competitive advantage.",
  "priority_gap": "Weakest pillar name and concrete steps to eliminate screening risk.",
  "sprint_plan": [
    {{
      "week": "Week 1: Immediate Screening Optimization",
      "focus": "Core focus",
      "action": "Concrete tactical steps to execute this week."
    }},
    {{
      "week": "Week 2: Deep Technical & Project Fortification",
      "focus": "Core focus",
      "action": "Concrete tactical steps to execute this week."
    }},
    {{
      "week": "Week 3: High-Stress Mock Interview Simulation",
      "focus": "Core focus",
      "action": "Concrete tactical steps to execute this week."
    }},
    {{
      "week": "Week 4: Referral & Pipeline Conversion",
      "focus": "Core focus",
      "action": "Concrete tactical steps to execute this week."
    }}
  ],
  "recruiter_advice": "Advice on LinkedIn positioning, referral outreach, and phone screens."
}}
Return ONLY valid JSON without markdown fences.
"""
        try:
            res = ask_json(prompt, api_key=key)
            if isinstance(res, dict) and "executive_verdict" in res:
                res["ai_engine"] = "Google Gemini 2.0 Flash"
                res["is_ai_generated"] = True
                return res
        except Exception as e:
            logger.warning("Gemini placement strategy generation failed: %s", e)

    # Fallback to Hugging Face local neural strategy
    return hf_generate_placement_strategy(placement_data)
