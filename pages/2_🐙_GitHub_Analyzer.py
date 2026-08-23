"""
🐙 GitHub Profile Analyzer — DevPilot AI
Evaluates developer portfolio readiness, repository hygiene, coding activity,
and language diversity from a tech recruiter's perspective with AI critique & resume translation.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
from datetime import datetime

# Ensure utils is importable from the pages/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.github_fetcher import fetch_complete_github_data
from utils.github_scorer import audit_github_profile, generate_markdown_report
from utils.github_ai_reviewer import generate_ai_critique

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Profile Analyzer — DevPilot AI",
    page_icon="🐙",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

.hero-github {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #21262d 100%);
    border-radius: 16px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(99, 102, 241, 0.25);
    color: white;
}
.hero-github h1 { font-size: 2.2rem; font-weight: 800; margin: 0 0 0.5rem 0; }
.hero-github p  { font-size: 0.95rem; color: #8b949e; margin: 0; line-height: 1.6; }

.input-box-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.profile-card {
    background: linear-gradient(135deg, #161b22, #0d1117);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 1.8rem;
    color: #c9d1d9;
    margin-bottom: 1.5rem;
}
.profile-name { font-size: 1.6rem; font-weight: 700; color: #f0f6fc; margin: 0; }
.profile-login { font-size: 1rem; color: #8b949e; margin-bottom: 0.8rem; }
.profile-bio { font-size: 0.92rem; color: #e6edf3; line-height: 1.5; margin-bottom: 1rem; }

.stat-pill {
    display: inline-block;
    background: rgba(110, 118, 129, 0.15);
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.82rem;
    color: #e6edf3;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
}

.badge-pass {
    display: inline-block;
    background: rgba(35, 134, 54, 0.2);
    border: 1px solid #238636;
    color: #3fb950;
    border-radius: 6px;
    padding: 0.15rem 0.55rem;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-fail {
    display: inline-block;
    background: rgba(218, 54, 51, 0.15);
    border: 1px solid #da3633;
    color: #f85149;
    border-radius: 6px;
    padding: 0.15rem 0.55rem;
    font-size: 0.72rem;
    font-weight: 600;
}

.repo-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease-in-out;
}
.repo-card:hover {
    border-color: #58a6ff;
    box-shadow: 0 4px 16px rgba(88, 166, 255, 0.1);
}
.repo-title { font-size: 1.1rem; font-weight: 700; color: #58a6ff; text-decoration: none; }
.repo-desc { font-size: 0.88rem; color: #8b949e; margin: 0.5rem 0 0.8rem 0; line-height: 1.5; }

.checklist-card {
    background: #161b22;
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    color: #e6edf3;
}
.checklist-card-high {
    background: #161b22;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    color: #e6edf3;
}

.bullet-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #a855f7;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1.2rem;
}

div[data-testid="stTabs"] button { font-weight: 600; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ─── Main Hero ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-github">
    <h1>🐙 GitHub Profile Analyzer & Recruiter Auditor</h1>
    <p>Comprehensive engineering portfolio audit. Evaluates repository hygiene, code recency, technology stack depth, and translates your top projects into hiring-manager-ready resume bullet points.</p>
</div>
""", unsafe_allow_html=True)

# ─── Main Content Input Area ──────────────────────────────────────────────────
col_input, col_adv = st.columns([1.2, 1], gap="large")

with col_input:
    st.markdown("### 1. Enter Target GitHub Profile")
    
    # Initialize session state for input value if not set
    if "gh_target_user" not in st.session_state:
        st.session_state["gh_target_user"] = ""

    username_val = st.text_input(
        "GitHub Username",
        value=st.session_state["gh_target_user"],
        placeholder="e.g. torvalds, tiangolo, your-handle",
        help="Enter any public GitHub username.",
        key="username_field",
    )

    st.markdown("<p style='color:#8b949e; font-size:0.82rem; margin-top:-0.5rem;'>Quick sample profiles:</p>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    if p_col1.button("tiangolo", use_container_width=True):
        st.session_state["gh_target_user"] = "tiangolo"
        st.rerun()
    if p_col2.button("karpathy", use_container_width=True):
        st.session_state["gh_target_user"] = "karpathy"
        st.rerun()
    if p_col3.button("charliermarsh", use_container_width=True):
        st.session_state["gh_target_user"] = "charliermarsh"
        st.rerun()
    if p_col4.button("torvalds", use_container_width=True):
        st.session_state["gh_target_user"] = "torvalds"
        st.rerun()

with col_adv:
    st.markdown("### 2. Optional Credentials")
    with st.expander("🔑 GitHub Token & Gemini AI Options", expanded=False):
        github_pat = st.text_input(
            "GitHub Personal Access Token (PAT)",
            type="password",
            placeholder="ghp_xxxxxxxxxxxx",
            help="Optional. Unauthenticated requests are limited to 60/hr. A token unlocks 5,000/hr.",
        )
        gemini_key_input = st.text_input(
            "Gemini API Key (Optional)",
            type="password",
            placeholder="AIzaSy...",
            help="Optional. Generates custom AI recruiter critiques and XYZ resume bullets.",
        )
        if not gemini_key_input and os.getenv("GEMINI_API_KEY"):
            gemini_key_input = os.getenv("GEMINI_API_KEY")

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("🚀 Analyze GitHub Profile", type="primary", use_container_width=True)

# ─── Execution Logic ──────────────────────────────────────────────────────────
active_user = username_val.strip() if username_val else st.session_state.get("gh_target_user", "").strip()

if analyze_btn:
    if not active_user:
        st.warning("Please enter a valid GitHub username to analyze.")
    else:
        with st.spinner(f"Fetching public profile and repositories for @{active_user}..."):
            try:
                gh_data = fetch_complete_github_data(
                    username=active_user,
                    token=github_pat.strip() if github_pat else None,
                )
                audit_result = audit_github_profile(gh_data)
                
                # Save into session_state for persistence across rerenders
                st.session_state["gh_data"] = gh_data
                st.session_state["gh_audit"] = audit_result
                st.session_state["gh_user"] = active_user
                st.session_state["gh_ai_critique"] = None  # Reset critique on new user
                
            except ValueError as ve:
                st.error(f"⚠️ {str(ve)}")
            except PermissionError as pe:
                st.error(f"🔒 {str(pe)}")
            except Exception as e:
                st.error(f"❌ Error fetching GitHub data: {str(e)}")

# ─── Results Rendering ────────────────────────────────────────────────────────
if "gh_data" in st.session_state and "gh_audit" in st.session_state:
    st.markdown("---")
    gh_data = st.session_state["gh_data"]
    audit = st.session_state["gh_audit"]
    profile = gh_data["profile"]
    stats = gh_data["stats"]
    score = audit["total_score"]
    grade = audit["grade"]
    grade_color = audit["grade_color"]

    # ── Top Profile Overview Card ──
    avatar = profile.get("avatar_url", "")
    p_name = profile.get("name") or profile.get("login")
    p_bio = profile.get("bio") or "*(No bio provided on profile)*"
    p_location = profile.get("location") or "Worldwide"
    p_company = profile.get("company") or "Independent"

    col_prof, col_gauge = st.columns([2.3, 1.2], gap="medium")

    with col_prof:
        st.markdown(f"""
<div class="profile-card">
    <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
        <img src="{avatar}" width="96" height="96" style="border-radius: 50%; border: 3px solid #6366f1;" />
        <div style="flex: 1; min-width: 240px;">
            <div class="profile-name">{p_name} <a href="{profile.get('html_url')}" target="_blank" style="color: #58a6ff; font-size: 1rem; text-decoration: none;">↗</a></div>
            <div class="profile-login">@{profile.get('login')}</div>
            <div class="profile-bio">{p_bio}</div>
            <div>
                <span class="stat-pill">📍 {p_location}</span>
                <span class="stat-pill">🏢 {p_company}</span>
                <span class="stat-pill">👥 {profile.get('followers', 0)} followers</span>
                <span class="stat-pill">📦 {stats['original_repo_count']} original repos</span>
                <span class="stat-pill">⭐ {stats['total_stars']} stars earned</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    with col_gauge:
        # Gauge Chart for Readiness Score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Portfolio Readiness<br><span style='font-size:14px; color:{grade_color}'>{grade}</span>", 'font': {'size': 18, 'color': '#ffffff'}},
            number={'suffix': "/100", 'font': {'size': 32, 'color': grade_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#8b949e"},
                'bar': {'color': grade_color, 'thickness': 0.28},
                'bgcolor': "#161b22",
                'borderwidth': 1,
                'bordercolor': "#30363d",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [50, 70], 'color': 'rgba(234, 179, 8, 0.15)'},
                    {'range': [70, 85], 'color': 'rgba(99, 102, 241, 0.15)'},
                    {'range': [85, 100], 'color': 'rgba(34, 197, 94, 0.15)'},
                ],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Dimension Metric Quick Cards ──
    st.markdown("#### 🧭 Score Breakdown by Dimension")
    dim_cols = st.columns(5)
    dims = audit["dimensions"]

    dim_keys = [
        ("profile_completeness", "Profile Info", "👤"),
        ("repo_quality", "Repo Hygiene", "🛠️"),
        ("activity_consistency", "Commit Activity", "⚡"),
        ("language_diversity", "Tech Depth", "💻"),
        ("community_impact", "Impact & Stars", "🌟"),
    ]

    for idx, (dkey, dlabel, dicon) in enumerate(dim_keys):
        dinfo = dims[dkey]
        with dim_cols[idx]:
            st.metric(
                label=f"{dicon} {dlabel}",
                value=f"{dinfo['score']} / {dinfo['max']}",
                delta=f"{(dinfo['score']/dinfo['max'])*100:.0f}%",
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Navigation Tabs ──
    tabs = st.tabs([
        "📊 Portfolio Diagnostics & Plan",
        "🛠️ Repository Health Audit",
        "💻 Tech Stack & Languages",
        "🧠 AI Recruiter Coach & Resume Bullets",
        "📥 Export Audit Report",
    ])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1: Diagnostics & Action Plan
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[0]:
        c1, c2 = st.columns([1.2, 1], gap="large")

        with c1:
            st.markdown("### 📋 Recruiter Audit Verdict")
            st.info(audit["verdict"], icon="💡")

            # Green Flags vs Red Flags
            if audit["green_flags"]:
                st.markdown("##### 🟢 Green Flags (Recruiter Favorites)")
                for gf in audit["green_flags"]:
                    st.markdown(f"- ✅ **{gf}**")

            if audit["red_flags"]:
                st.markdown("##### 🔴 Red Flags (Immediate Fixes Recommended)")
                for rf in audit["red_flags"]:
                    st.markdown(f"- ⚠️ **{rf}**")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🚀 Prioritized Action Plan")
            st.caption("Ranked checklist to rapidly increase your developer portfolio score.")
            for i, act in enumerate(audit["action_checklist"], 1):
                card_class = "checklist-card-high" if act["impact"] == "High" else "checklist-card"
                st.markdown(f"""
<div class="{card_class}">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 700; color: #f0f6fc;">{i}. {act['task']}</span>
        <span>
            <span class="stat-pill" style="color:#f59e0b; border-color:#f59e0b;">⚡ {act['impact']} Impact</span>
            <span class="stat-pill">⏱️ {act['effort']}</span>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

        with c2:
            st.markdown("### 🕸️ Portfolio Radar Matrix")
            r_categories = [d["label"] for d in dims.values()]
            r_values = [(d["score"] / d["max"]) * 100 for d in dims.values()]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=r_values + [r_values[0]],
                theta=r_categories + [r_categories[0]],
                fill='toself',
                fillcolor='rgba(99, 102, 241, 0.25)',
                line=dict(color='#818cf8', width=2),
                name='Portfolio Score'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#8b949e")),
                    bgcolor="#161b22",
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=30, r=30, t=20, b=20),
                height=350,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            with st.expander("🔍 View Dimension-Level Strengths & Gaps"):
                for key, d in dims.items():
                    st.markdown(f"**{d['label']} ({d['score']}/{d['max']})**")
                    for s in d.get("strengths", []):
                        st.markdown(f"<span style='color:#22c55e;'>✔ {s}</span>", unsafe_allow_html=True)
                    for imp in d.get("improvements", []):
                        st.markdown(f"<span style='color:#f87171;'>• {imp}</span>", unsafe_allow_html=True)
                    st.markdown("---")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2: Repository Health Audit
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### 🛠️ Repository-by-Repository Health Audit")
        st.caption("Review individual repository hygiene: descriptions, licenses, live demo links, and star ratings.")

        repo_audits = audit.get("repo_audits", [])
        if not repo_audits:
            st.warning("No original repositories found to audit.")
        else:
            # Filter & Sorting
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                search_query = st.text_input("Filter repositories by name or keyword", placeholder="Type project name...")
            with f_col2:
                sort_mode = st.selectbox("Sort By", ["Highest Health Score", "Most Stars", "Recently Updated"])

            filtered_repos = repo_audits
            if search_query.strip():
                q = search_query.lower().strip()
                filtered_repos = [r for r in filtered_repos if q in r["name"].lower() or q in r["description"].lower() or q in r["language"].lower()]

            if sort_mode == "Highest Health Score":
                filtered_repos = sorted(filtered_repos, key=lambda x: x["health_score"], reverse=True)
            elif sort_mode == "Most Stars":
                filtered_repos = sorted(filtered_repos, key=lambda x: x["stars"], reverse=True)
            elif sort_mode == "Recently Updated":
                filtered_repos = sorted(filtered_repos, key=lambda x: x.get("updated_at", ""), reverse=True)

            for r in filtered_repos:
                desc_badge = '<span class="badge-pass">✔ Description</span>' if r["has_description"] else '<span class="badge-fail">✘ Missing Description</span>'
                demo_badge = '<span class="badge-pass">✔ Live Demo</span>' if r["has_homepage"] else '<span class="badge-fail">✘ No Live Demo</span>'
                lic_badge = '<span class="badge-pass">✔ License</span>' if r["has_license"] else '<span class="badge-fail">✘ No License</span>'
                topic_badge = '<span class="badge-pass">✔ Topics</span>' if r["has_topics"] else '<span class="badge-fail">✘ No Topics</span>'

                demo_link_html = f'<a href="{r["homepage"]}" target="_blank" style="color: #22c55e; margin-left: 0.8rem; font-size: 0.85rem;">🔗 Open Live Demo</a>' if r["has_homepage"] else ""

                st.markdown(f"""
<div class="repo-card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <a class="repo-title" href="{r['html_url']}" target="_blank">📦 {r['name']}</a>
            {demo_link_html}
        </div>
        <div>
            <span class="stat-pill">⭐ {r['stars']} stars</span>
            <span class="stat-pill">💻 {r['language']}</span>
            <span class="stat-pill" style="border-color:#6366f1; color:#818cf8; font-weight:700;">Health: {r['health_score']}/100</span>
        </div>
    </div>
    <div class="repo-desc">{r['description']}</div>
    <div style="margin-top: 0.6rem;">
        {desc_badge} &nbsp; {demo_badge} &nbsp; {lic_badge} &nbsp; {topic_badge}
    </div>
</div>
""", unsafe_allow_html=True)
                if r.get("suggestions"):
                    with st.expander(f"💡 Recommended fixes for {r['name']}"):
                        for s in r["suggestions"]:
                            st.markdown(f"- 🔧 {s}")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3: Tech Stack & Languages
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### 💻 Language Distribution & Tech Stack Mapping")
        
        lang_bytes = gh_data.get("language_bytes", {})
        if not lang_bytes:
            st.info("No language statistics detected across public repositories.")
        else:
            col_chart, col_stats = st.columns([1.2, 1], gap="large")

            with col_chart:
                total_bytes = sum(lang_bytes.values())
                labels = list(lang_bytes.keys())
                values = list(lang_bytes.values())

                fig_pie = px.pie(
                    names=labels,
                    values=values,
                    hole=0.45,
                    title="Codebase Composition (by bytes of code)",
                    color_discrete_sequence=px.colors.qualitative.Prism,
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#c9d1d9"),
                    height=380,
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_stats:
                st.markdown("##### 📊 Primary Stack Specialization")
                sorted_l = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)
                for lang_name, b_count in sorted_l[:6]:
                    pct = (b_count / total_bytes) * 100
                    st.write(f"**{lang_name}** — `{pct:.1f}%` ({b_count / 1024:.1f} KB)")
                    st.progress(min(pct / 100.0, 1.0))

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### 🗂️ Repositories per Language")
                for l_name, r_cnt in gh_data.get("language_repo_counts", {}).items():
                    st.markdown(f"- **{l_name}**: {r_cnt} project{'s' if r_cnt > 1 else ''}")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 4: AI Recruiter Coach & Resume Bullets
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### 🧠 AI Recruiter Assessment & Resume Bullet Generator")
        st.caption("Converts GitHub projects directly into quantified Google XYZ resume bullet points.")

        ai_key_to_use = gemini_key_input.strip() if gemini_key_input else None

        # Button to generate / refresh critique
        if st.session_state.get("gh_ai_critique") is None:
            if st.button("✨ Generate AI Recruiter Critique & Resume Bullets", type="primary"):
                with st.spinner("Analyzing portfolio repositories with AI Recruiter Engine..."):
                    critique = generate_ai_critique(gh_data, audit, api_key=ai_key_to_use)
                    st.session_state["gh_ai_critique"] = critique
                    st.rerun()

        critique = st.session_state.get("gh_ai_critique")
        if critique:
            gen_tag = "🤖 Generated via Google Gemini AI" if critique.get("is_ai_generated") else "⚡ Generated via Built-in Rule Engine (Offline)"
            st.caption(f"*{gen_tag}*")

            st.markdown("#### 🎯 Executive Recruiter Summary")
            st.info(critique.get("executive_summary", ""), icon="📌")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🎙️ 30-Second Interview Elevator Pitch")
            st.caption("Use this script when interviewers ask: *'Walk me through your background and projects'*")
            pitch_text = critique.get("elevator_pitch", "")
            st.code(pitch_text, language="text")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📄 Ready-to-Use XYZ Resume Bullet Points")
            st.caption("Quantified bullet points based on your GitHub projects formatted for engineering resumes.")
            
            for b in critique.get("resume_bullets", []):
                st.markdown(f"""
<div class="bullet-box">
    <div style="font-weight: 700; color: #a855f7; margin-bottom: 0.4rem;">
        📦 {b.get('repo_name')} &nbsp;<span style="color:#8b949e; font-size:0.85rem;">({b.get('language')})</span>
    </div>
    <div style="color: #f0f6fc; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.6rem;">
        • {b.get('bullet_xyz')}
    </div>
    <div style="color: #94a3b8; font-size: 0.85rem;">
        💡 <em>Interview Tip:</em> {b.get('recruiter_tip')}
    </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🚀 Recommended Capstone Project to Build Next")
            st.success(f"**Strategic Recommendation:** {critique.get('capstone_recommendation', '')}", icon="🏆")

            if critique.get("interview_talking_points"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### ❓ Likely Technical Interview Questions from Your Repos")
                for q in critique["interview_talking_points"]:
                    st.markdown(f"- 💬 *\"{q}\"*")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 5: Export Markdown Audit Report
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("### 📥 Download Portfolio Audit Report")
        st.caption("Export your complete GitHub audit results as a portable Markdown file.")

        report_md = generate_markdown_report(gh_data, audit)
        
        st.download_button(
            label="⬇️ Download Audit Report (.md)",
            data=report_md,
            file_name=f"DevPilot_GitHub_Audit_{profile.get('login', 'report')}.md",
            mime="text/markdown",
            type="primary",
        )

        with st.expander("📄 Preview Markdown Report", expanded=True):
            st.markdown(report_md)

else:
    # Empty State Guide
    st.markdown("""
<div style="background: #161b22; border: 1px dashed #30363d; border-radius: 12px; padding: 2.5rem; text-align: center; color: #8b949e; margin-top: 1rem;">
    <div style="font-size: 3rem; margin-bottom: 0.8rem;">🐙</div>
    <h3 style="color: #f0f6fc; margin-bottom: 0.5rem;">Ready to Audit Your GitHub Presence</h3>
    <p style="max-width: 550px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
        Enter any public GitHub username above to calculate your Developer Portfolio Readiness Score (0–100), audit repository documentation, and generate recruiter-ready resume bullet points.
    </p>
</div>
""", unsafe_allow_html=True)
