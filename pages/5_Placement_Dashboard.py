"""
📊 Placement Readiness Dashboard & Application Pipeline Manager -- DevPilot AI
Unified engineering readiness index, 4-pillar diagnostics, milestone sprint planner,
and end-to-end application tracking for software engineering placement seasons.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import json
import html
from datetime import datetime, date

# Ensure utils is importable from pages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.placement_tracker import (
    calculate_placement_readiness,
    calculate_milestone_progress,
    calculate_pipeline_analytics,
    get_sample_pipeline,
    DEFAULT_MILESTONES,
    COMPANY_TIERS,
    PIPELINE_STAGES,
    STAGE_COLORS,
    export_pipeline_json,
    import_pipeline_json,
    export_pipeline_csv,
    generate_placement_strategy,
)
from utils.pdf_generator import generate_placement_dossier_pdf
from utils.sidebar import render_sidebar
from utils.gemini_client import get_active_gemini_key, render_byok_section

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Placement Dashboard -- DevPilot AI",
    page_icon="📊",
    layout="wide",
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
render_sidebar()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero-placement {
    background: linear-gradient(135deg, #090d16 0%, #151b2e 50%, #1e1b4b 100%);
    border-radius: 18px;
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.7);
}
.hero-placement::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.22) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-placement h1 {
    font-family: 'Sora', sans-serif !important;
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
    position: relative;
    z-index: 1;
}
.hero-accent {
    width: 55px;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #ec4899);
    border-radius: 2px;
    margin-bottom: 0.9rem;
    position: relative;
    z-index: 1;
}
.hero-placement p {
    font-size: 1rem;
    color: #cbd5e1;
    margin: 0;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.kpi-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    position: relative;
}
.kpi-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2.2rem;
    font-weight: 800;
    color: #f0f6fc;
    margin: 0.2rem 0;
    font-variant-numeric: tabular-nums;
}
.kpi-sub { font-size: 0.8rem; color: #94a3b8; }

.pillar-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.pillar-card:hover {
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    transform: translateY(-2px);
}

.stage-badge {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 700;
}

.countdown-box {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ─── Initialize Session State Defaults ────────────────────────────────────────
if "placement_milestones" not in st.session_state:
    st.session_state["placement_milestones"] = [dict(m) for m in DEFAULT_MILESTONES]

if "placement_pipeline" not in st.session_state:
    st.session_state["placement_pipeline"] = get_sample_pipeline()

if "candidate_name" not in st.session_state:
    st.session_state["candidate_name"] = "Candidate"

if "target_placement_date" not in st.session_state:
    st.session_state["target_placement_date"] = date(date.today().year, 12, 1)

# Extract scores from other modules in session state
resume_res = st.session_state.get("resume_results") or {}
live_resume_score = (resume_res.get("ats") or {}).get("total")
live_github_score = (st.session_state.get("github_audit") or {}).get("total_score")
live_interview_score = (st.session_state.get("interview_session") or {}).get("total_score")
live_leetcode_score = (st.session_state.get("leetcode_audit") or {}).get("total_score")

# ─── Hero Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-placement">
    <h1>Placement Readiness Dashboard</h1>
    <div class="hero-accent"></div>
    <p>Unified Engineering Readiness Score (ERS), 4-pillar hiring bar diagnostics, milestone sprint planner, and real-time application pipeline tracker for tech placement season.</p>
</div>
""", unsafe_allow_html=True)

# ─── Global Configuration Bar ─────────────────────────────────────────────────
with st.container():
    c_col1, c_col2, c_col3 = st.columns([1.5, 1.5, 2], gap="medium")
    
    with c_col1:
        candidate_name = st.text_input("Candidate Name", value=st.session_state["candidate_name"])
        st.session_state["candidate_name"] = candidate_name

    with c_col2:
        target_date = st.date_input("Target Placement Season Date", value=st.session_state["target_placement_date"])
        st.session_state["target_placement_date"] = target_date

    with c_col3:
        target_tier = st.selectbox(
            "Target Company Tier",
            options=list(COMPANY_TIERS.keys()),
            index=0,
            help="Benchmarked against calibrated screening standards for these company types.",
        )

# Target Date Countdown Calculation
days_left = (st.session_state["target_placement_date"] - date.today()).days
countdown_msg = (
    f"⏳ <b>{days_left} Days Remaining</b> until your target placement date ({html.escape(st.session_state['target_placement_date'].strftime('%B %d, %Y'))})"
    if days_left > 0
    else f"🎯 <b>Placement Season Active!</b> ({abs(days_left)} days past target date)"
)
st.markdown(f"""
<div class="countdown-box">
    <div>{countdown_msg}</div>
    <div style="font-size:0.8rem; color:#94a3b8;">Focus: High-leverage sprint actions</div>
</div>
""", unsafe_allow_html=True)

# ─── Quick Presets & Manual Overrides ──────────────────────────────────────────
with st.expander("⚙️ Score Ingestion & Calibration Presets", expanded=False):
    st.markdown("Use real session scores from the other DevPilot AI modules or simulate standard candidate profiles:")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    with p_col1:
        if st.button("🚀 Load FAANG Ready Profile", use_container_width=True):
            st.session_state["sim_resume"] = 88
            st.session_state["sim_github"] = 82
            st.session_state["sim_interview"] = 85
            st.session_state["sim_leetcode"] = 92
            st.rerun()

    with p_col2:
        if st.button("📈 Load Unicorn Contender", use_container_width=True):
            st.session_state["sim_resume"] = 78
            st.session_state["sim_github"] = 72
            st.session_state["sim_interview"] = 72
            st.session_state["sim_leetcode"] = 74
            st.rerun()

    with p_col3:
        if st.button("🌱 Load Early Stage Prep", use_container_width=True):
            st.session_state["sim_resume"] = 62
            st.session_state["sim_github"] = 50
            st.session_state["sim_interview"] = 52
            st.session_state["sim_leetcode"] = 46
            st.rerun()

    with p_col4:
        if st.button("🔄 Sync Live Session Scores", use_container_width=True):
            for k in ["sim_resume", "sim_github", "sim_interview", "sim_leetcode"]:
                st.session_state.pop(k, None)
            st.rerun()

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        val_resume = st.session_state.get("sim_resume", live_resume_score)
        eff_resume = st.slider("Resume ATS Score", 0, 100, int(val_resume) if val_resume is not None else 50)
    with s_col2:
        val_gh = st.session_state.get("sim_github", live_github_score)
        eff_github = st.slider("GitHub Portfolio Score", 0, 100, int(val_gh) if val_gh is not None else 50)
    with s_col3:
        val_int = st.session_state.get("sim_interview", live_interview_score)
        eff_interview = st.slider("Mock Interview Score", 0, 100, int(val_int) if val_int is not None else 50)
    with s_col4:
        val_lc = st.session_state.get("sim_leetcode", live_leetcode_score)
        eff_leetcode = st.slider("LeetCode DSA Score", 0, 100, int(val_lc) if val_lc is not None else 50)

# Calculate Readiness
readiness = calculate_placement_readiness(
    resume_score=eff_resume if (live_resume_score is not None or "sim_resume" in st.session_state) else None,
    github_score=eff_github if (live_github_score is not None or "sim_github" in st.session_state) else None,
    interview_score=eff_interview if (live_interview_score is not None or "sim_interview" in st.session_state) else None,
    leetcode_score=eff_leetcode if (live_leetcode_score is not None or "sim_leetcode" in st.session_state) else None,
    target_tier=target_tier,
)
st.session_state["placement_readiness"] = readiness

# Auto-sync to Firebase if user is authenticated
try:
    from utils.firebase_db import sync_module_to_cloud_async
    sync_module_to_cloud_async("placement")
except Exception:
    pass

# ─── Dashboard Tabs ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Unified Readiness & Radar",
    "🧠 AI Career Strategist",
    "🎯 Placement Sprint Milestones",
    "💼 Application Pipeline Manager",
    "📑 Executive Placement Dossier",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: Unified Readiness & Radar
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    m_col1, m_col2 = st.columns([1.2, 1.8], gap="large")

    with m_col1:
        score = readiness["composite_score"]
        grade = readiness["grade"]
        badge_color = readiness["tier_badge_color"]

        grade_label_esc = html.escape(str(readiness.get('grade_label', '')))
        outlook_esc = html.escape(str(readiness.get('outlook', '')))
        tier_verdict_esc = html.escape(str(readiness.get('tier_verdict', '')))
        st.markdown(f"""
<div class="kpi-card" style="border-top: 4px solid {badge_color};">
    <div class="kpi-title">Engineering Readiness Score (ERS)</div>
    <div style="display:flex; align-items:baseline; gap: 10px;">
        <span class="kpi-value" style="color: {badge_color};">{score}</span>
        <span style="font-size:1.1rem; color:#8b949e;">/100</span>
        <span style="background:{badge_color}22; color:{badge_color}; border:1px solid {badge_color}; padding:0.2rem 0.6rem; border-radius:12px; font-weight:800; font-size:1rem; margin-left:auto;">
            Grade {grade}
        </span>
    </div>
    <div style="font-weight:700; color:#f0f6fc; margin-top:0.4rem;">{grade_label_esc}</div>
    <div class="kpi-sub" style="margin-top:0.5rem; line-height:1.5;">{outlook_esc}</div>
    <div style="margin-top:1rem; padding:0.6rem 0.8rem; background:rgba(255,255,255,0.03); border-radius:8px; border:1px solid #30363d;">
        <span style="font-size:0.85rem; font-weight:700; color:{badge_color};">{tier_verdict_esc}</span>
    </div>
</div>
""", unsafe_allow_html=True)

        # 4 Pillar Progress Cards
        st.markdown("#### 4 Pillars Breakdown")
        for p_id, p in readiness["pillars"].items():
            p_score = p["score"]
            tested_tag = "Live Tested" if p["tested"] else "Baseline"
            p_name_esc = html.escape(str(p.get('name', '')))
            p_icon_esc = html.escape(str(p.get('icon', '')))
            p_status_esc = html.escape(str(p.get('status', '')))
            st.markdown(f"""
<div class="pillar-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:700; color:#f0f6fc; font-size:0.95rem;">{p_icon_esc} {p_name_esc}</span>
        <span style="font-weight:800; color:{p['color']}; font-size:1.1rem;">{p_score}/100</span>
    </div>
    <div style="margin: 0.5rem 0;">
        <div style="height:6px; background:#21262d; border-radius:3px; overflow:hidden;">
            <div style="height:100%; width:{p_score}%; background:{p['color']}; border-radius:3px;"></div>
        </div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#8b949e;">
        <span>Target: {p['benchmark']} | Status: <b style="color:{p['color']};">{p_status_esc}</b></span>
        <span>{tested_tag}</span>
    </div>
</div>
""", unsafe_allow_html=True)
            if not p["tested"]:
                st.page_link(p["page"], label=f"Launch {p['name']} to test →")

    with m_col2:
        st.markdown("#### 4-Pillar Polar Readiness Radar")
        
        # Radar Chart comparing Candidate vs Target Tier Benchmark
        categories = [p["name"] for p in readiness["pillars"].values()]
        candidate_vals = [p["score"] for p in readiness["pillars"].values()]
        benchmark_vals = [p["benchmark"] for p in readiness["pillars"].values()]

        # Close the loop for radar chart
        r_categories = categories + [categories[0]]
        r_candidate = candidate_vals + [candidate_vals[0]]
        r_benchmark = benchmark_vals + [benchmark_vals[0]]

        fig = go.Figure()

        # Target Benchmark Trace
        fig.add_trace(go.Scatterpolar(
            r=r_benchmark,
            theta=r_categories,
            fill='toself',
            name=f"{target_tier.split()[0]} Benchmark",
            line=dict(color='#818cf8', width=2, dash='dot'),
            fillcolor='rgba(129, 140, 248, 0.12)',
        ))

        # Candidate Score Trace
        fig.add_trace(go.Scatterpolar(
            r=r_candidate,
            theta=r_categories,
            fill='toself',
            name=f"{candidate_name}'s Score",
            line=dict(color='#22c55e' if score >= 75 else '#f59e0b', width=3),
            fillcolor='rgba(34, 197, 94, 0.25)' if score >= 75 else 'rgba(245, 158, 11, 0.25)',
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color="#8b949e", size=9),
                    gridcolor="#30363d",
                ),
                angularaxis=dict(
                    tickfont=dict(color="#f0f6fc", size=10, family="Inter"),
                    gridcolor="#30363d",
                ),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color="#f0f6fc", size=11),
            ),
            margin=dict(l=40, r=40, t=20, b=40),
            height=370,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Strategic Strengths & Bottlenecks
        st.markdown("#### Strategic Assessment")
        s_col, b_col = st.columns(2)
        with s_col:
            st.markdown("**🌟 Key Strengths**")
            if readiness["strengths"]:
                for s in readiness["strengths"]:
                    st.markdown(f"- {s}")
            else:
                st.caption("No pillars currently exceed target tier benchmark. Focus on rapid gains below.")

        with b_col:
            st.markdown("**⚠️ Critical Bottlenecks**")
            if readiness["bottlenecks"]:
                for b in readiness["bottlenecks"]:
                    st.markdown(f"- {b}")
            else:
                st.caption("All pillars meet or exceed target threshold! Maintain consistency.")

        st.markdown("**🎯 High-Leverage Action Items**")
        for idx, act in enumerate(readiness["action_items"], 1):
            st.markdown(f"{idx}. {act}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: AI Career Strategist & 4-Week Sprint Roadmap
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🧠 AI Career Strategist & 4-Week Placement Sprint")
    st.caption("Synthesizes all 4 engineering assessment pillars to formulate an executive hiring strategy, diagnose priority screening gaps, and build a customized 4-week sprint roadmap.")

    strat_engine_opts = [
        "🤗 Hugging Face Neural Engine (Local ML - No API Key)",
        "✨ Google Gemini 2.0 Flash (Cloud AI)",
    ]
    strat_choice = st.radio(
        "Select Placement Strategy Engine:",
        options=strat_engine_opts,
        index=0,
        horizontal=True,
        key="placement_strat_engine_radio",
    )
    selected_strat_engine = "hf" if "Hugging Face" in strat_choice else "gemini"

    if selected_strat_engine == "gemini":
        render_byok_section(widget_key="placement_byok", compact=False)

    col_btn, _ = st.columns([1.5, 2.5])
    with col_btn:
        generate_strat_btn = st.button("Generate AI Placement Strategy & Sprint", type="primary", use_container_width=True)

    if generate_strat_btn or "ai_placement_strategy" not in st.session_state:
        ai_key = get_active_gemini_key()
        if selected_strat_engine == "gemini" and not ai_key:
            st.warning("⚠️ No Gemini API key detected. Please paste your key in the Bring Your Own Key slot above, or select Hugging Face Neural Engine.")
        with st.spinner("AI Strategist is synthesizing multi-pillar metrics and building your 4-week sprint..."):
            strategy = generate_placement_strategy(
                placement_data=readiness,
                engine=selected_strat_engine,
                api_key=ai_key,
            )
            st.session_state["ai_placement_strategy"] = strategy

    if "ai_placement_strategy" in st.session_state:
        strat = st.session_state["ai_placement_strategy"]
        eng_label = strat.get("ai_engine", "Local Neural Engine")

        # Executive verdict card
        st.markdown(f"""
<div class="kpi-card" style="border-left: 4px solid #6366f1; margin-top: 1rem;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; flex-wrap:wrap; gap:0.5rem;">
        <span style="font-size:1.15rem; font-weight:700; color:#f8fafc;">Executive Candidate Verdict</span>
        <span style="font-size:0.75rem; background:rgba(99,102,241,0.18); border:1px solid rgba(99,102,241,0.4); color:#a5b4fc; padding:2px 8px; border-radius:12px; font-weight:600;">
            {eng_label}
        </span>
    </div>
    <div style="color:#e2e8f0; font-size:1rem; line-height:1.6;">
        {html.escape(strat.get("executive_verdict", ""))}
    </div>
</div>
""", unsafe_allow_html=True)

        col_st, col_gap = st.columns(2)
        with col_st:
            st.markdown(f"""
<div style="background:#0f172a; border:1px solid rgba(34, 197, 94, 0.3); border-radius:12px; padding:1.2rem; margin-top:1rem;">
    <div style="font-weight:700; color:#4ade80; margin-bottom:0.4rem; font-size:1rem;">🌟 Strongest Competitive Advantage</div>
    <div style="color:#cbd5e1; font-size:0.92rem; line-height:1.5;">{html.escape(strat.get("strongest_pillar", ""))}</div>
</div>
""", unsafe_allow_html=True)
        with col_gap:
            st.markdown(f"""
<div style="background:#0f172a; border:1px solid rgba(239, 68, 68, 0.3); border-radius:12px; padding:1.2rem; margin-top:1rem;">
    <div style="font-weight:700; color:#f87171; margin-bottom:0.4rem; font-size:1rem;">⚠️ Priority Screening Risk to Fix</div>
    <div style="color:#cbd5e1; font-size:0.92rem; line-height:1.5;">{html.escape(strat.get("priority_gap", ""))}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📅 4-Week Placement Acceleration Sprint")

        sprint_cols = st.columns(4)
        sprint_items = strat.get("sprint_plan", [])
        for i, item in enumerate(sprint_items):
            col_target = sprint_cols[i % len(sprint_cols)]
            with col_target:
                st.markdown(f"""
<div style="background:#131726; border:1px solid #30363d; border-radius:12px; padding:1.2rem; height:100%; display:flex; flex-direction:column; justify-content:space-between;">
    <div>
        <div style="font-size:0.85rem; font-weight:700; color:#818cf8; text-transform:uppercase; letter-spacing:0.04em;">{html.escape(item.get('week', f'Week {i+1}'))}</div>
        <div style="font-weight:700; color:#f0f6fc; margin:0.4rem 0 0.6rem 0; font-size:1rem;">{html.escape(item.get('focus', ''))}</div>
        <div style="font-size:0.88rem; color:#94a3b8; line-height:1.5;">{html.escape(item.get('action', ''))}</div>
    </div>
</div>
""", unsafe_allow_html=True)

        if strat.get("recruiter_advice"):
            st.markdown(f"""
<div style="background:#161b26; border:1px dashed #475569; border-radius:12px; padding:1.2rem; margin-top:1.5rem;">
    <div style="font-weight:700; color:#38bdf8; margin-bottom:0.3rem;">💼 Senior Recruiter Conversion Advice</div>
    <div style="color:#cbd5e1; font-size:0.92rem; line-height:1.5;">{html.escape(strat.get("recruiter_advice", ""))}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: Placement Sprint Milestones
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🎯 Placement Sprint Milestone Checklist")
    st.markdown("Track essential preparation milestones across 5 core placement categories:")

    milestones = st.session_state["placement_milestones"]
    prog = calculate_milestone_progress(milestones)

    # Top progress summary
    p_col1, p_col2 = st.columns([1, 3])
    with p_col1:
        st.metric(
            "Sprint Completion",
            f"{prog['pct']}%",
            f"{prog['completed']} / {prog['total']} Milestones",
        )
    with p_col2:
        st.markdown(f"**Overall Progress ({prog['pct']}%)**")
        st.progress(prog["pct"] / 100.0)

    # Categories tabs / expanders
    categories = sorted(list(set(m["category"] for m in milestones)))
    
    for cat in categories:
        cat_items = [m for m in milestones if m["category"] == cat]
        cat_done = sum(1 for m in cat_items if m.get("completed", False))
        cat_pct = round((cat_done / len(cat_items)) * 100) if cat_items else 0

        with st.expander(f"📁 {cat} ({cat_done}/{len(cat_items)} Done — {cat_pct}%)", expanded=(cat_pct < 100)):
            for m in cat_items:
                m_id = m["id"]
                checked = st.checkbox(
                    f"**{m['title']}** — _{m.get('desc', '')}_",
                    value=m.get("completed", False),
                    key=f"chk_{m_id}",
                )
                if checked != m.get("completed", False):
                    m["completed"] = checked
                    st.rerun()

    # Add custom milestone
    with st.expander("➕ Add Custom Milestone"):
        with st.form("custom_milestone_form"):
            c_title = st.text_input("Milestone Title (e.g. Implement LRU Cache in Go)")
            c_desc = st.text_input("Description / Notes")
            c_cat = st.selectbox("Category", options=categories + ["Custom Sprint"])
            c_pri = st.selectbox("Priority", options=["High", "Medium", "Low"])
            
            if st.form_submit_button("Add Milestone"):
                if c_title.strip():
                    new_m = {
                        "id": f"custom_{int(datetime.now().timestamp())}",
                        "category": c_cat,
                        "title": c_title.strip(),
                        "desc": c_desc.strip(),
                        "priority": c_pri,
                        "completed": False,
                    }
                    st.session_state["placement_milestones"].append(new_m)
                    st.success("Milestone added!")
                    st.rerun()

    if st.button("🔄 Reset to Default Milestones"):
        st.session_state["placement_milestones"] = [dict(m) for m in DEFAULT_MILESTONES]
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: Application Pipeline Manager
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 💼 Application & Interview Pipeline Manager")
    apps = st.session_state["placement_pipeline"]
    analytics = calculate_pipeline_analytics(apps)

    # Funnel Metric Cards
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
    f_col1.metric("Total Tracked", analytics["total"])
    f_col2.metric("Active Pipeline", analytics["active"])
    f_col3.metric("Interviews Secured", analytics["interviews"], f"{analytics['interview_rate']}% rate")
    f_col4.metric("Offers Received", analytics["offers"], f"{analytics['offer_rate']}% rate")
    f_col5.metric("Archived / Rejected", analytics["rejected"])

    # Stage Distribution Bar
    stage_counts = analytics["by_stage"]
    fig_stages = px.bar(
        x=list(stage_counts.keys()),
        y=list(stage_counts.values()),
        color=list(stage_counts.keys()),
        color_discrete_map=STAGE_COLORS,
        labels={"x": "Pipeline Stage", "y": "Number of Applications"},
        title="Application Stage Distribution Funnel",
    )
    fig_stages.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0f6fc"),
        showlegend=False,
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_stages, use_container_width=True)

    # Add Application Form
    with st.expander("➕ Add New Application", expanded=False):
        with st.form("new_application_form"):
            a1, a2 = st.columns(2)
            with a1:
                app_company = st.text_input("Company Name *")
                app_role = st.text_input("Role Title (e.g. SDE 1, SWE Intern)")
                app_tier = st.selectbox("Company Tier", options=list(COMPANY_TIERS.keys()))
                app_stage = st.selectbox("Current Stage", options=PIPELINE_STAGES, index=1)
            with a2:
                app_date = st.date_input("Date Applied", value=date.today())
                app_comp = st.text_input("Target Compensation / CTC (e.g. $165,000 / 24 LPA)")
                app_ref = st.text_input("Referral Contact / Status")
                app_loc = st.text_input("Location / Remote Model")
            
            app_notes = st.text_area("Interview Notes & Preparation Debrief")

            if st.form_submit_button("Save Application"):
                if app_company.strip():
                    new_app = {
                        "id": f"app_{int(datetime.now().timestamp())}",
                        "company": app_company.strip(),
                        "role": app_role.strip() or "Software Engineer",
                        "tier": app_tier,
                        "stage": app_stage,
                        "applied_date": str(app_date),
                        "compensation": app_comp.strip() or "N/A",
                        "referral": app_ref.strip() or "None",
                        "location": app_loc.strip() or "Hybrid",
                        "notes": app_notes.strip(),
                    }
                    st.session_state["placement_pipeline"].insert(0, new_app)
                    st.success(f"Added {app_company} to application tracker!")
                    st.rerun()
                else:
                    st.error("Company Name is required.")

    # Applications Table & Quick Stage Updaters
    st.markdown("#### Tracked Applications")
    if not apps:
        st.info("No applications currently tracked. Click '➕ Add New Application' or load sample demo data.")
    else:
        for idx, app in enumerate(apps):
            app_id = app.get("id", f"app_{idx}")
            stage = app.get("stage", "Wishlist")
            s_color = STAGE_COLORS.get(stage, "#94a3b8")

            with st.container():
                company_str = html.escape(str(app.get('company') or ''))
                role_str = html.escape(str(app.get('role') or ''))
                tier_str = html.escape(str(app.get('tier', '').split()[0]))
                loc_str = html.escape(str(app.get('location', 'N/A')))
                comp_str = html.escape(str(app.get('compensation', 'N/A')))
                ref_str = html.escape(str(app.get('referral', 'None')))
                date_str = html.escape(str(app.get('applied_date', 'N/A')))
                notes_html = f'<div style="font-size:0.82rem; color:#c9d1d9; margin-top:0.4rem; font-style:italic;">{html.escape(app["notes"])}</div>' if app.get('notes') else ''

                app_card_html = (
                    f'<div style="background:linear-gradient(145deg, {s_color}10, #131726); border:1px solid {s_color}44; border-radius:12px; padding:1.1rem 1.3rem; margin-bottom:0.85rem; box-shadow:0 4px 14px -2px rgba(0,0,0,0.3);">'
                    f'<div style="display:flex; justify-content:space-between; align-items:flex-start;">'
                    f'<div>'
                    f'<span style="font-family:\'Sora\', sans-serif; font-size:1.12rem; font-weight:700; color:#f0f6fc;">{company_str}</span>'
                    f'<span style="color:#94a3b8; font-size:0.9rem;"> — {role_str}</span>'
                    f'<span style="font-family:\'JetBrains Mono\', monospace; margin-left:0.6rem; font-size:0.72rem; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); padding:0.15rem 0.5rem; border-radius:12px; color:#cbd5e1;">{tier_str}</span>'
                    f'</div>'
                    f'<span style="font-family:\'JetBrains Mono\', monospace; background:{s_color}22; color:{s_color}; border:1px solid {s_color}55; padding:0.2rem 0.7rem; border-radius:12px; font-weight:700; font-size:0.78rem;">{html.escape(str(stage))}</span>'
                    f'</div>'
                    f'<div style="display:flex; gap:16px; font-size:0.8rem; color:#94a3b8; margin-top:0.5rem;">'
                    f'<span>📅 Applied: {date_str}</span>'
                    f'<span>📍 {loc_str}</span>'
                    f'<span>💰 {comp_str}</span>'
                    f'<span>🤝 Referral: {ref_str}</span>'
                    f'</div>'
                    f'{notes_html}'
                    f'</div>'
                )
                st.markdown(app_card_html, unsafe_allow_html=True)
                
                # Inline Stage Changer & Delete
                ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 3])
                with ctrl_col1:
                    new_stage = st.selectbox(
                        "Update Stage",
                        options=PIPELINE_STAGES,
                        index=PIPELINE_STAGES.index(stage) if stage in PIPELINE_STAGES else 0,
                        key=f"stage_select_{app_id}_{idx}",
                        label_visibility="collapsed",
                    )
                    if new_stage != stage:
                        app["stage"] = new_stage
                        st.rerun()

                with ctrl_col2:
                    if st.button("🗑️ Delete", key=f"del_{app_id}_{idx}"):
                        st.session_state["placement_pipeline"] = [
                            a for a in st.session_state["placement_pipeline"] if a.get("id") != app_id
                        ]
                        st.rerun()

    # Import / Export Pipeline Data
    st.markdown("---")
    st.markdown("#### 🔄 Pipeline Data Export & Import")
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    
    with exp_col1:
        csv_data = export_pipeline_csv(apps)
        st.download_button(
            "📥 Export to CSV",
            data=csv_data,
            file_name="placement_applications.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp_col2:
        json_data = export_pipeline_json(apps)
        st.download_button(
            "📥 Export to JSON",
            data=json_data,
            file_name="placement_applications.json",
            mime="application/json",
            use_container_width=True,
        )

    with exp_col3:
        if st.button("🚀 Load Sample Pipeline", use_container_width=True):
            st.session_state["placement_pipeline"] = get_sample_pipeline()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: Executive Placement Dossier (PDF Export)
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📑 Executive Placement Dossier")
    st.markdown("Generate and export a unified, recruiter-ready placement report synthesizing your 4-pillar readiness, sprint milestones, and active pipeline.")

    # Generate PDF bytes
    pdf_bytes = generate_placement_dossier_pdf(
        candidate_name=candidate_name,
        readiness=readiness,
        milestones_progress=calculate_milestone_progress(st.session_state["placement_milestones"]),
        pipeline_analytics=calculate_pipeline_analytics(st.session_state["placement_pipeline"]),
        applications=st.session_state["placement_pipeline"],
    )

    d_col1, d_col2 = st.columns([2, 1])
    with d_col1:
        st.markdown(f"""
<div class="kpi-card">
    <div style="font-weight:700; font-size:1.1rem; color:#f0f6fc;">Ready for Export: {candidate_name}'s Dossier</div>
    <div style="font-size:0.85rem; color:#8b949e; margin-top:0.3rem;">
        Includes overall ERS grade ({readiness['grade']}), 4-pillar benchmark breakdown, key strengths,
        vulnerabilities, milestone sprint completion ({prog['pct']}%), and active application table.
    </div>
</div>
""", unsafe_allow_html=True)

    with d_col2:
        st.download_button(
            label="⬇️ Download Executive PDF Dossier",
            data=pdf_bytes,
            file_name=f"{candidate_name.replace(' ', '_')}_Placement_Dossier.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # Markdown Summary Preview
    st.markdown("#### Dossier Preview Summary")
    st.markdown(f"""
- **Candidate**: {candidate_name}
- **Engineering Readiness Score**: **{readiness['composite_score']}/100** (Grade **{readiness['grade']}** — {readiness['grade_label']})
- **Target Company Tier**: {target_tier}
- **Status Verdict**: {readiness['tier_verdict']}
- **Milestones Completed**: {prog['completed']} / {prog['total']} ({prog['pct']}%)
- **Active Job Applications**: {analytics['total']} tracked ({analytics['interviews']} interviews in progress)
""")
