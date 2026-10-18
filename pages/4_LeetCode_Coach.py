"""
🎯 LeetCode Coach & Algorithmic Diagnostic — DevPilot AI
Analyzes candidate LeetCode problem-solving profiles, tracks mastery across 8 algorithmic pillars,
identifies weak patterns, delivers company-specific roadmaps, and provides code complexity optimization.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import html

# Ensure utils is importable from pages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.leetcode_coach import (
    fetch_leetcode_stats,
    audit_algorithmic_readiness,
    generate_practice_roadmap,
    analyze_code_complexity,
    ALGORITHMIC_PILLARS,
)
from utils.pdf_generator import generate_leetcode_pdf
from utils.sidebar import render_sidebar
from utils.gemini_client import get_active_gemini_key, render_byok_section

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LeetCode Coach — DevPilot AI",
    page_icon="🎯",
    layout="wide",
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
render_sidebar()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero-leetcode {
    background: linear-gradient(135deg, #0d1117 0%, #171d2b 50%, #1e283d 100%);
    border-radius: 18px;
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.7);
}
.hero-leetcode::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -5%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-leetcode h1 {
    font-family: 'Sora', sans-serif !important;
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
    position: relative;
    z-index: 1;
}
.hero-accent {
    width: 50px;
    height: 3px;
    background: linear-gradient(90deg, #f59e0b, #ef4444);
    border-radius: 2px;
    margin-bottom: 0.9rem;
    position: relative;
    z-index: 1;
}
.hero-leetcode p {
    font-size: 1rem;
    color: #cbd5e1;
    margin: 0;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.stat-pill {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(110, 118, 129, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.78rem;
    color: #e6edf3;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
}
.pill-easy   { font-family: 'JetBrains Mono', monospace; background: rgba(34,197,94,0.15); border-color:#22c55e; color:#4ade80; font-weight:700; }
.pill-medium { font-family: 'JetBrains Mono', monospace; background: rgba(245,158,11,0.15); border-color:#f59e0b; color:#fbbf24; font-weight:700; }
.pill-hard   { font-family: 'JetBrains Mono', monospace; background: rgba(239,68,68,0.15); border-color:#ef4444; color:#f87171; font-weight:700; }

.problem-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.85rem;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.problem-card:hover {
    border-color: rgba(245, 158, 11, 0.5);
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    transform: translateY(-2px);
}
.problem-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.05rem;
    font-weight: 700;
    color: #f8fafc;
    text-decoration: none;
}
.problem-title:hover { color: #f59e0b; }

.complexity-card {
    background: linear-gradient(145deg, rgba(245, 158, 11, 0.06), #131726);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 1rem;
    color: #f8fafc;
}

.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.35), transparent);
    margin: 1.6rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-leetcode">
    <h1>LeetCode Coach &amp; Algorithmic Diagnostic</h1>
    <div class="hero-accent"></div>
    <p>Track algorithmic mastery across 8 core pillars, diagnose data structure blind spots, generate curated placement roadmaps, and optimize Time &amp; Space complexity for technical coding rounds.</p>
</div>
""", unsafe_allow_html=True)

# ─── Session State Initialization ─────────────────────────────────────────────
if "lc_stats" not in st.session_state:
    st.session_state["lc_stats"] = None
if "leetcode_audit" not in st.session_state:
    st.session_state["leetcode_audit"] = None
if "lc_target_user" not in st.session_state:
    st.session_state["lc_target_user"] = ""

# ─── Input & Ingestion Section ────────────────────────────────────────────────
col_in, col_opt = st.columns([1.2, 1], gap="large")

with col_in:
    st.markdown("### 1. Ingest LeetCode Profile")
    lc_user_input = st.text_input(
        "LeetCode Username",
        value=st.session_state.get("lc_target_user", ""),
        placeholder="e.g. neal_wu, lee215, your-handle",
        help="Enter any public LeetCode username to automatically fetch problem counts across topics.",
    )

    st.markdown("<p style='color:#8b949e; font-size:0.82rem; margin-top:-0.5rem;'>Quick sample profiles:</p>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    if s1.button("neal_wu (Competitive)", use_container_width=True):
        st.session_state["lc_target_user"] = "neal_wu"
        st.rerun()
    if s2.button("lee215 (Legendary)", use_container_width=True):
        st.session_state["lc_target_user"] = "lee215"
        st.rerun()
    if s3.button("SDE-1 Placement Demo", use_container_width=True):
        # Demo data for testing
        demo_stats = {
            "username": "Placement_Demo",
            "ranking": 125000,
            "reputation": 45,
            "total_solved": 142,
            "easy_solved": 65,
            "medium_solved": 68,
            "hard_solved": 9,
            "pillar_counts": {
                "Arrays & Hashing": 38,
                "Two Pointers & Sliding Window": 24,
                "Binary Search & Divide/Conquer": 18,
                "Trees & Binary Search Trees": 26,
                "Graphs, BFS & DFS": 14,
                "Dynamic Programming & Recursion": 11,
                "Heaps & Priority Queues": 6,
                "Backtracking & Greedy": 5,
            },
        }
        st.session_state["lc_stats"] = demo_stats
        st.session_state["leetcode_audit"] = audit_algorithmic_readiness(demo_stats)
        try:
            from utils.firebase_db import sync_module_to_cloud_async
            sync_module_to_cloud_async("leetcode")
        except Exception:
            pass
        st.rerun()

with col_opt:
    st.markdown("### 2. Manual / Custom Stats Mode")
    with st.expander("Offline Manual Input (Optional)", expanded=False):
        st.caption("Don't have a public LeetCode handle? Input your estimated solved counts:")
        m_easy = st.number_input("Easy Solved", min_value=0, max_value=2000, value=40)
        m_med = st.number_input("Medium Solved", min_value=0, max_value=3000, value=50)
        m_hard = st.number_input("Hard Solved", min_value=0, max_value=1000, value=5)
        apply_manual = st.button("Apply Manual Solved Stats")

        if apply_manual:
            m_total = m_easy + m_med + m_hard
            manual_stats = {
                "username": "Candidate (Self-Reported)",
                "ranking": 250000 if m_total >= 50 else 0,
                "reputation": 0,
                "total_solved": m_total,
                "easy_solved": m_easy,
                "medium_solved": m_med,
                "hard_solved": m_hard,
                "pillar_counts": {
                    "Arrays & Hashing": round(m_total * 0.32),
                    "Two Pointers & Sliding Window": round(m_total * 0.18),
                    "Binary Search & Divide/Conquer": round(m_total * 0.12),
                    "Trees & Binary Search Trees": round(m_total * 0.14),
                    "Graphs, BFS & DFS": round(m_total * 0.10),
                    "Dynamic Programming & Recursion": round(m_total * 0.08),
                    "Heaps & Priority Queues": round(m_total * 0.03),
                    "Backtracking & Greedy": round(m_total * 0.03),
                },
            }
            st.session_state["lc_stats"] = manual_stats
            st.session_state["leetcode_audit"] = audit_algorithmic_readiness(manual_stats)
            try:
                from utils.firebase_db import sync_module_to_cloud_async
                sync_module_to_cloud_async("leetcode")
            except Exception:
                pass
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
fetch_btn = st.button("Analyze LeetCode Profile", type="primary", use_container_width=True)

# Handle live fetch
active_user = lc_user_input.strip() if lc_user_input else st.session_state.get("lc_target_user", "").strip()

if fetch_btn:
    if not active_user:
        st.warning("Please enter a valid LeetCode username.")
    else:
        with st.spinner(f"Querying LeetCode GraphQL API for @{active_user}..."):
            try:
                stats = fetch_leetcode_stats(active_user)
                audit = audit_algorithmic_readiness(stats)
                st.session_state["lc_stats"] = stats
                st.session_state["leetcode_audit"] = audit
                st.session_state["lc_target_user"] = active_user

                # Auto-sync to Firebase if user is authenticated
                try:
                    from utils.firebase_db import sync_module_to_cloud_async
                    sync_module_to_cloud_async("leetcode")
                except Exception:
                    pass

                st.success(f"Profile @{stats['username']} analyzed successfully!")
            except Exception as e:
                st.error(f"Error fetching profile: {e}")

# ─── Results Dashboard ────────────────────────────────────────────────────────
if st.session_state.get("lc_stats") and st.session_state.get("leetcode_audit"):
    stats = st.session_state["lc_stats"]
    audit = st.session_state["leetcode_audit"]
    score = audit["total_score"]
    grade = audit["grade"]
    grade_color = audit["grade_color"]

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Top KPI Bar ──
    col_prof, col_gauge = st.columns([2, 1.2], gap="large")

    with col_prof:
        u_esc = html.escape(str(stats.get('username', '')))
        u_url_esc = html.escape(f"https://leetcode.com/{stats.get('username', '')}")
        st.markdown(f"""
<div style="background:#161b22; border:1px solid #30363d; border-radius:14px; padding:1.5rem; margin-bottom:1rem;">
    <div style="font-size:1.5rem; font-weight:800; color:#f8fafc; margin-bottom:0.3rem;">
        @{u_esc}
        <a href="{u_url_esc}" target="_blank" style="color:#f59e0b; font-size:1rem; text-decoration:none;">↗</a>
    </div>
    <div style="margin-bottom:0.8rem;">
        <span class="stat-pill" style="border-color:#f59e0b; color:#f59e0b; font-weight:700;">Global Rank: #{stats.get('ranking', 0):,}</span>
        <span class="stat-pill">Total Solved: <b>{stats['total_solved']}</b></span>
    </div>
    <div>
        <span class="stat-pill pill-easy">🟢 Easy: {stats['easy_solved']}</span>
        <span class="stat-pill pill-medium">🟡 Medium: {stats['medium_solved']}</span>
        <span class="stat-pill pill-hard">🔴 Hard: {stats['hard_solved']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

    with col_gauge:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Algorithmic Readiness<br><span style='font-size:14px; color:{grade_color}'>{grade}</span>", 'font': {'size': 18, 'color': '#ffffff'}},
            number={'suffix': "/100", 'font': {'size': 32, 'color': grade_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#8b949e"},
                'bar': {'color': grade_color, 'thickness': 0.28},
                'bgcolor': "#161b22",
                'steps': [
                    {'range': [0, 45], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [45, 65], 'color': 'rgba(234, 179, 8, 0.15)'},
                    {'range': [65, 80], 'color': 'rgba(99, 102, 241, 0.15)'},
                    {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.15)'},
                ],
            }
        ))
        fig_g.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_g, use_container_width=True)

    # ── 4 Main Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "8-Axis Algorithmic Radar",
        "Weak Patterns & Blind Spots",
        "Targeted Placement Roadmaps",
        "AI Code Complexity Optimizer",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: 8-Axis Radar Chart & Dimensions
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        col_rad, col_diag = st.columns([1.2, 1], gap="large")

        with col_rad:
            st.markdown("### 8-Axis Algorithmic Radar Matrix")
            st.caption("Normalized against a 25-problem benchmark per pillar for Tier-1 interview readiness.")

            radar_data = audit.get("radar_data", [])
            categories = [r["pillar"] for r in radar_data]
            values = [r["pct"] for r in radar_data]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(245, 158, 11, 0.2)',
                line=dict(color='#f59e0b', width=2.5),
                name='Candidate Coverage',
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#8b949e")),
                    bgcolor="#161b22",
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=30, b=30),
                height=380,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_diag:
            st.markdown("### Diagnostic Assessment")
            st.info(audit["verdict"])

            st.markdown("#### Dimension Scorecard")
            for dim in audit.get("dimensions", {}).values():
                st.write(f"**{dim['label']}**: `{dim['score']} / {dim['max']} pts`")
                st.progress(dim["score"] / dim["max"])

            st.markdown("<br>", unsafe_allow_html=True)
            if audit.get("strengths"):
                st.markdown("##### Standout Pillars:")
                for s in audit["strengths"]:
                    st.markdown(f"- ✅ {s}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: Weak Patterns & Blind Spots
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### Algorithmic Blind Spots & Topic Gaps")
        st.caption("Identifies data structures where low problem counts create vulnerability in technical interviews.")

        col_b1, col_b2 = st.columns([1, 1], gap="large")
        with col_b1:
            st.markdown("#### Priority Gap Areas:")
            for b in audit.get("blind_spots", []):
                st.markdown(f"""
<div style="background:linear-gradient(145deg, rgba(239,68,68,0.08), #131726); border:1px solid rgba(239,68,68,0.32); border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.75rem;">
    <span style="color:#f87171; font-weight:700;">⚠️ {html.escape(str(b))}</span>
</div>
""", unsafe_allow_html=True)

        with col_b2:
            st.markdown("#### Solved Counts by Pillar:")
            for item in audit.get("radar_data", []):
                p_col = "#22c55e" if item["count"] >= 20 else "#f59e0b" if item["count"] >= 8 else "#ef4444"
                p_name_esc = html.escape(str(item.get('pillar', '')))
                p_cnt_esc = html.escape(str(item.get('count', 0)))
                st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding:0.4rem 0; border-bottom:1px solid #1e293b;">
    <span style="color:#e2e8f0; font-size:0.9rem;">{p_name_esc}</span>
    <span style="color:{p_col}; font-weight:700;">{p_cnt_esc} solved</span>
</div>
""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3: Targeted Placement Roadmaps
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### Targeted Company Practice Roadmaps")
        st.caption("Problems are automatically sorted to prioritize your weakest pillars first.")

        track_choice = st.selectbox(
            "Select Target Roadmap Track:",
            options=["FAANG / Big Tech 75", "FinTech & Low-Latency", "Placement Sprint (Foundations)"],
            index=0,
        )

        roadmap = generate_practice_roadmap(stats, track=track_choice)

        for prob in roadmap:
            diff_pill = "pill-easy" if prob["difficulty"] == "Easy" else "pill-medium" if prob["difficulty"] == "Medium" else "pill-hard"
            p_name = html.escape(str(prob.get("name") or ""))
            raw_url = str(prob.get("url") or "#")
            p_url = html.escape(raw_url) if raw_url.startswith(("http://", "https://", "#")) else "#"
            p_pillar = html.escape(str(prob.get("pillar") or ""))
            p_diff = html.escape(str(prob.get("difficulty") or ""))
            p_pattern = html.escape(str(prob.get("pattern") or ""))
            st.markdown(f"""
<div class="problem-card">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
        <div>
            <a class="problem-title" href="{p_url}" target="_blank" rel="noopener noreferrer">{p_name} ↗</a>
            <div style="color:#94a3b8; font-size:0.85rem; margin-top:0.3rem;">Pillar: <b>{p_pillar}</b></div>
        </div>
        <div>
            <span class="stat-pill {diff_pill}">{p_diff}</span>
        </div>
    </div>
    <div style="margin-top:0.6rem; color:#cbd5e1; font-size:0.88rem; background:rgba(15,23,42,0.6); padding:0.6rem 0.8rem; border-radius:6px;">
        💡 <b>Pattern Insight:</b> {p_pattern}
    </div>
</div>
""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4: AI Complexity & Pattern Optimizer
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### AI Code Complexity & Pattern Optimizer")
        st.caption("Paste an algorithm implementation or brute-force solution to analyze its computational complexity and optimize data structures.")

        lc_engine_opts = [
            "🤗 Hugging Face Neural Engine (Local ML - No API Key)",
            "✨ Google Gemini 2.0 Flash (Cloud AI)",
            "⚡ AST & Heuristic Static Analyzer (Instant)",
        ]
        lc_engine_choice = st.radio(
            "Select Code Optimizer Engine:",
            options=lc_engine_opts,
            index=0,
            horizontal=True,
            key="lc_code_engine_radio",
        )
        if "Hugging Face" in lc_engine_choice:
            selected_lc_engine = "hf"
        elif "Gemini" in lc_engine_choice:
            selected_lc_engine = "gemini"
            render_byok_section(widget_key="leetcode_byok", compact=False)
        else:
            selected_lc_engine = "offline"

        code_input = st.text_area(
            "Paste your solution (Python, Java, C++, or JavaScript):",
            height=200,
            placeholder="""def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []""",
        )

        opt_btn = st.button("Analyze Complexity & Optimize", type="primary")

        if opt_btn and code_input.strip():
            ai_key = get_active_gemini_key()
            if selected_lc_engine == "gemini" and not ai_key:
                st.warning("⚠️ No Gemini API key detected. Please paste your key in the Bring Your Own Key slot above, or select Hugging Face / Static AST analyzer.")
            with st.spinner("Analyzing runtime and space complexity..."):
                analysis = analyze_code_complexity(code_input, api_key=ai_key, engine=selected_lc_engine)

                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.metric("Time Complexity", analysis["time_complexity"])
                with c_col2:
                    st.metric("Space Complexity", analysis["space_complexity"])

                eng_badge = html.escape(str(analysis.get("ai_engine", "Local Neural Engine")))
                pattern_str = html.escape(str(analysis.get("detected_pattern", "")))
                opt_tip = html.escape(str(analysis.get("optimization_tip", "")))
                st.markdown(f"""
<div class="complexity-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; flex-wrap:wrap; gap:0.5rem;">
        <span style="font-size:1.1rem; font-weight:700; color:#f59e0b;">
            Pattern: {pattern_str}
        </span>
        <span style="font-size:0.75rem; background:rgba(99,102,241,0.18); border:1px solid rgba(99,102,241,0.4); color:#a5b4fc; padding:2px 8px; border-radius:12px; font-weight:600;">
            {eng_badge}
        </span>
    </div>
    <div style="color:#e2e8f0; font-size:0.92rem; line-height:1.6;">
        <b>Optimization Strategy:</b> {opt_tip}
    </div>
</div>
""", unsafe_allow_html=True)

    # ── PDF Download Section ──
    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
    with st.spinner("Generating PDF LeetCode Diagnostic Report..."):
        try:
            pdf_bytes = generate_leetcode_pdf(stats, audit, roadmap)
            st.download_button(
                label="Download LeetCode Algorithmic Audit (.pdf)",
                data=pdf_bytes,
                file_name=f"DevPilot_LeetCode_Audit_{stats['username']}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as pdf_err:
            st.error(f"PDF generation error: {pdf_err}")

else:
    # Empty state guide
    st.markdown("""
<div style="background:#161b22; border:1px dashed #30363d; border-radius:12px; padding:2.8rem; text-align:center; color:#8b949e; margin-top:1.5rem;">
    <div style="font-size:3rem; margin-bottom:0.8rem;">🎯</div>
    <h3 style="color:#f0f6fc; margin-bottom:0.5rem;">Ready to Audit Your Algorithmic Readiness</h3>
    <p style="max-width:550px; margin:0 auto; line-height:1.6;">
        Enter any public LeetCode username or choose a sample profile above to generate your 8-Axis Algorithmic Radar, uncover data structure blind spots, and curate your targeted interview roadmap.
    </p>
</div>
""", unsafe_allow_html=True)
