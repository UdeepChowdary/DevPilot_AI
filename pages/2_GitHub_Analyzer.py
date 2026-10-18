"""
GitHub Profile Analyzer — DevPilot AI
Evaluates developer portfolio readiness, repository hygiene, coding activity,
and language diversity from a tech recruiter's perspective with AI critique & resume translation.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import html
from datetime import datetime

# Ensure utils is importable from the pages/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.github_fetcher import fetch_complete_github_data
from utils.github_scorer import audit_github_profile, generate_markdown_report
from utils.github_ai_reviewer import generate_ai_critique
from utils.pdf_generator import generate_github_pdf
from utils.sidebar import render_sidebar
from utils.gemini_client import get_active_gemini_key, render_byok_section

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub Profile Analyzer — DevPilot AI",
    page_icon="🐙",
    layout="wide",
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
render_sidebar()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero-github {
    background: linear-gradient(135deg, #0d0b1d 0%, #1a103c 50%, #2e1065 100%);
    border-radius: 18px;
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(168, 85, 247, 0.35);
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.7);
}
.hero-github::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -5%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(168,85,247,0.2) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-github h1 {
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
    background: linear-gradient(90deg, #6366f1, #a855f7);
    border-radius: 2px;
    margin-bottom: 0.9rem;
    position: relative;
    z-index: 1;
}
.hero-github p {
    font-size: 1rem;
    color: #e9d5ff;
    margin: 0;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.input-box-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1.5rem;
}

.profile-card {
    background: linear-gradient(135deg, #131726, #0d111a);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.8rem;
    color: #c9d1d9;
    margin-bottom: 1.5rem;
}
.profile-name {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.6rem;
    font-weight: 700;
    color: #f0f6fc;
    margin: 0;
}
.profile-login {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    color: #94a3b8;
    margin-bottom: 0.8rem;
}
.profile-bio { font-size: 0.92rem; color: #e6edf3; line-height: 1.55; margin-bottom: 1rem; }

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

.badge-pass {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(35, 134, 54, 0.18);
    border: 1px solid #238636;
    color: #4ade80;
    border-radius: 6px;
    padding: 0.15rem 0.55rem;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-fail {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(218, 54, 51, 0.18);
    border: 1px solid #da3633;
    color: #f87171;
    border-radius: 6px;
    padding: 0.15rem 0.55rem;
    font-size: 0.72rem;
    font-weight: 600;
}

.repo-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.3rem;
    margin-bottom: 1rem;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.repo-card:hover {
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    transform: translateY(-2px);
}
.repo-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.1rem;
    font-weight: 700;
    color: #818cf8;
    text-decoration: none;
}
.repo-desc { font-size: 0.88rem; color: #94a3b8; margin: 0.5rem 0 0.8rem 0; line-height: 1.55; }

.checklist-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.85rem;
    color: #e6edf3;
}
.checklist-card-high {
    background: linear-gradient(145deg, rgba(239, 68, 68, 0.08), #131726);
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.85rem;
    color: #e6edf3;
}

.bullet-box {
    background: linear-gradient(145deg, rgba(168, 85, 247, 0.06), #131726);
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.2rem;
}

div[data-testid="stTabs"] button { font-weight: 600; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ─── Main Hero ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-github">
    <h1>GitHub Profile Analyzer &amp; Recruiter Auditor</h1>
    <div class="hero-accent"></div>
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
    with st.expander("GitHub Token & Gemini AI Options", expanded=False):
        github_pat = st.text_input(
            "GitHub Personal Access Token (PAT)",
            type="password",
            placeholder="ghp_xxxxxxxxxxxx",
            help="Optional. Unauthenticated requests are limited to 60/hr. A token unlocks 5,000/hr.",
        )
        st.markdown("<div style='margin-top:0.6rem; font-size:0.82rem; font-weight:600;'>Gemini AI Key (BYOK)</div>", unsafe_allow_html=True)
        render_byok_section(widget_key="gh_top_byok", compact=True)

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("Analyze GitHub Profile", type="primary", use_container_width=True)

# ─── Execution Logic ──────────────────────────────────────────────────────────
active_user = username_val.strip() if username_val else st.session_state.get("gh_target_user", "").strip()

if analyze_btn:
    if not active_user:
        st.warning("Please enter a valid GitHub username to analyze.")
    else:
        progress_bar = st.progress(0, text=f"Starting analysis for @{active_user}...")
        try:
            progress_bar.progress(15, text="👤 Fetching GitHub profile...")
            progress_bar.progress(35, text="Loading repositories (paginating if needed)...")
            gh_data = fetch_complete_github_data(
                username=active_user,
                token=github_pat.strip() if github_pat else None,
            )
            progress_bar.progress(70, text="Running portfolio scoring engine...")
            audit_result = audit_github_profile(gh_data)
            progress_bar.progress(95, text="Finalizing audit report...")

            # Save into session_state for persistence across rerenders
            st.session_state["gh_data"] = gh_data
            st.session_state["gh_audit"] = audit_result
            st.session_state["gh_user"] = active_user
            st.session_state["gh_ai_critique"] = None  # Reset critique on new user

            # Also persist GitHub score in top-level session_state for sidebar KPI
            st.session_state["github_audit"] = audit_result

            # Auto-sync to Firebase if user is authenticated
            try:
                from utils.firebase_db import sync_module_to_cloud_async
                sync_module_to_cloud_async("github")
            except Exception:
                pass

            progress_bar.progress(100, text="Analysis complete!")

        except ValueError as ve:
            progress_bar.empty()
            st.error(f"⚠️ {str(ve)}")
        except PermissionError as pe:
            progress_bar.empty()
            st.error(f"{str(pe)}")
        except Exception as e:
            progress_bar.empty()
            st.error(f"Error fetching GitHub data: {str(e)}")
        finally:
            progress_bar.empty()

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
    raw_avatar = str(profile.get("avatar_url", "") or "")
    avatar = html.escape(raw_avatar) if raw_avatar.startswith(("http://", "https://")) else ""
    p_name = html.escape(str(profile.get("name") or profile.get("login") or "Developer"))
    p_login = html.escape(str(profile.get("login") or ""))
    p_bio = html.escape(str(profile.get("bio") or "(No bio provided on profile)"))
    p_location = html.escape(str(profile.get("location") or "Worldwide"))
    p_company = html.escape(str(profile.get("company") or "Independent"))
    raw_html_url = str(profile.get("html_url") or "#")
    p_html_url = html.escape(raw_html_url) if raw_html_url.startswith(("http://", "https://", "#")) else "#"

    col_prof, col_gauge = st.columns([2.3, 1.2], gap="medium")

    with col_prof:
        st.markdown(f"""
<div class="profile-card">
    <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
        <img src="{avatar}" width="96" height="96" style="border-radius: 50%; border: 3px solid #6366f1;" />
        <div style="flex: 1; min-width: 240px;">
            <div class="profile-name">{p_name} <a href="{p_html_url}" target="_blank" rel="noopener noreferrer" style="color: #58a6ff; font-size: 1rem; text-decoration: none;">↗</a></div>
            <div class="profile-login">@{p_login}</div>
            <div class="profile-bio">{p_bio}</div>
            <div>
                <span class="stat-pill">{p_location}</span>
                <span class="stat-pill">{p_company}</span>
                <span class="stat-pill">{profile.get('followers', 0)} followers</span>
                <span class="stat-pill">{stats['original_repo_count']} original repos</span>
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
    st.markdown("#### Score Breakdown by Dimension")
    dim_cols = st.columns(5)
    dims = audit["dimensions"]

    dim_keys = [
        ("profile_completeness", "Profile Info", "👤"),
        ("repo_quality", "Repo Hygiene", ""),
        ("activity_consistency", "Commit Activity", ""),
        ("language_diversity", "Tech Depth", ""),
        ("community_impact", "Impact & Stars", ""),
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
        "Portfolio Diagnostics & Plan",
        "Repository Health Audit",
        "Tech Stack & Languages",
        "AI Recruiter Coach & Resume Bullets",
        "Export Audit Report",
    ])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1: Diagnostics & Action Plan
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[0]:
        c1, c2 = st.columns([1.2, 1], gap="large")

        with c1:
            st.markdown("### Recruiter Audit Verdict")
            st.info(audit["verdict"])

            # Green Flags vs Red Flags
            if audit["green_flags"]:
                st.markdown("##### Green Flags (Recruiter Favorites)")
                for gf in audit["green_flags"]:
                    st.markdown(f"- **{gf}**")

            if audit["red_flags"]:
                st.markdown("##### Red Flags (Immediate Fixes Recommended)")
                for rf in audit["red_flags"]:
                    st.markdown(f"- ⚠️ **{rf}**")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Prioritized Action Plan")
            st.caption("Ranked checklist to rapidly increase your developer portfolio score.")
            for i, act in enumerate(audit["action_checklist"], 1):
                card_class = "checklist-card-high" if act["impact"] == "High" else "checklist-card"
                task_esc = html.escape(str(act.get('task', '')))
                impact_esc = html.escape(str(act.get('impact', '')))
                effort_esc = html.escape(str(act.get('effort', '')))
                st.markdown(f"""
<div class="{card_class}">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 700; color: #f0f6fc;">{i}. {task_esc}</span>
        <span>
            <span class="stat-pill" style="color:#f59e0b; border-color:#f59e0b;">{impact_esc} Impact</span>
            <span class="stat-pill">⏱️ {effort_esc}</span>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

        with c2:
            st.markdown("### Portfolio Radar Matrix")
            r_categories = [d["label"] for d in dims.values()]
            r_values = [(d["score"] / d["max"]) * 100 for d in dims.values()]

            # Color-code fill by overall average score zone
            avg_score = sum(r_values) / max(len(r_values), 1)
            if avg_score >= 70:
                fill_color = "rgba(34, 197, 94, 0.2)"   # green
                line_color = "#22c55e"
            elif avg_score >= 50:
                fill_color = "rgba(234, 179, 8, 0.2)"   # yellow
                line_color = "#eab308"
            else:
                fill_color = "rgba(239, 68, 68, 0.2)"   # red
                line_color = "#ef4444"

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=r_values + [r_values[0]],
                theta=r_categories + [r_categories[0]],
                fill='toself',
                fillcolor=fill_color,
                line=dict(color=line_color, width=2.5),
                name='Portfolio Score',
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

            with st.expander("View Dimension-Level Strengths & Gaps"):
                for key, d in dims.items():
                    st.markdown(f"**{d['label']} ({d['score']}/{d['max']})**")
                    for s in d.get("strengths", []):
                        st.markdown(f"<span style='color:#22c55e;'>✔ {html.escape(str(s))}</span>", unsafe_allow_html=True)
                    for imp in d.get("improvements", []):
                        st.markdown(f"<span style='color:#f87171;'>• {html.escape(str(imp))}</span>", unsafe_allow_html=True)
                    st.markdown("---")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2: Repository Health Audit
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("### Repository-by-Repository Health Audit")
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

                r_name = html.escape(str(r.get("name") or ""))
                raw_url = str(r.get("html_url") or "#")
                r_url = html.escape(raw_url) if raw_url.startswith(("http://", "https://", "#")) else "#"
                r_desc = html.escape(str(r.get("description") or "No description provided."))
                r_lang = html.escape(str(r.get("language") or "Other"))
                r_stars = r.get("stars", 0)
                r_health = r.get("health_score", 0)

                raw_hp = str(r.get("homepage") or "").strip()
                is_valid_hp = raw_hp.startswith(("http://", "https://"))
                demo_link_html = (
                    f' <a href="{html.escape(raw_hp)}" target="_blank" rel="noopener noreferrer" style="color: #22c55e; margin-left: 0.8rem; font-size: 0.85rem;">🔗 Open Live Demo</a>'
                    if (r.get("has_homepage") and is_valid_hp)
                    else ""
                )

                repo_card_html = (
                    f'<div class="repo-card">'
                    f'<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">'
                    f'<div>'
                    f'<a class="repo-title" href="{r_url}" target="_blank" rel="noopener noreferrer">{r_name}</a>{demo_link_html}'
                    f'</div>'
                    f'<div>'
                    f'<span class="stat-pill">⭐ {r_stars} stars</span>'
                    f'<span class="stat-pill">{r_lang}</span>'
                    f'<span class="stat-pill" style="border-color:#6366f1; color:#818cf8; font-weight:700;">Health: {r_health}/100</span>'
                    f'</div>'
                    f'</div>'
                    f'<div class="repo-desc">{r_desc}</div>'
                    f'<div style="margin-top: 0.6rem;">{desc_badge} &nbsp; {demo_badge} &nbsp; {lic_badge} &nbsp; {topic_badge}</div>'
                    f'</div>'
                )
                st.markdown(repo_card_html, unsafe_allow_html=True)
                if r.get("suggestions"):
                    with st.expander(f"Recommended fixes for {r['name']}"):
                        for s in r["suggestions"]:
                            st.markdown(f"- {s}")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 3: Tech Stack & Languages
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("### Language Distribution & Tech Stack Mapping")
        
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
                st.markdown("##### Primary Stack Specialization")
                sorted_l = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)
                for lang_name, b_count in sorted_l[:6]:
                    pct = (b_count / total_bytes) * 100
                    st.write(f"**{lang_name}** — `{pct:.1f}%` ({b_count / 1024:.1f} KB)")
                    st.progress(min(pct / 100.0, 1.0))

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("##### Repositories per Language")
                for l_name, r_cnt in gh_data.get("language_repo_counts", {}).items():
                    st.markdown(f"- **{l_name}**: {r_cnt} project{'s' if r_cnt > 1 else ''}")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 4: AI Recruiter Coach & Resume Bullets
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("### AI Recruiter Assessment & Resume Bullet Generator")
        st.caption("Converts GitHub projects directly into quantified Google XYZ resume bullet points.")

        gh_engine_choice = st.radio(
            "Select AI Reviewer Engine:",
            options=["hf", "gemini", "rule_based"],
            format_func=lambda x: {
                "hf": "🤗 Hugging Face Local Neural Engine (100% Offline, No Key Needed)",
                "gemini": "✨ Google Gemini 2.0 Flash (Online Cloud LLM, API Key)",
                "rule_based": "⚡ Fast Heuristic Rule Engine (Instant)",
            }[x],
            horizontal=True,
            index=0,
            key="gh_engine_selector",
        )

        if gh_engine_choice == "gemini":
            render_byok_section(widget_key="gh_tab4_byok", compact=False)

        ai_key_to_use = get_active_gemini_key()

        c_btn_col1, c_btn_col2 = st.columns([2, 1])
        with c_btn_col1:
            trigger_critique = st.button("Generate AI Recruiter Critique & Resume Bullets", type="primary", use_container_width=True)
        with c_btn_col2:
            if st.session_state.get("gh_ai_critique"):
                if st.button("🔄 Regenerate Critique", use_container_width=True):
                    st.session_state["gh_ai_critique"] = None
                    st.rerun()

        if trigger_critique:
            if gh_engine_choice == "gemini" and not ai_key_to_use:
                st.warning("⚠️ No Gemini API key detected. Please paste your key in the Bring Your Own Key slot above, or select Hugging Face / Rule Engine.")
            with st.spinner(f"Analyzing portfolio repositories with {gh_engine_choice.upper()} Engine..."):
                critique = generate_ai_critique(gh_data, audit, api_key=ai_key_to_use, engine=gh_engine_choice)
                st.session_state["gh_ai_critique"] = critique
                st.rerun()

        critique = st.session_state.get("gh_ai_critique")
        if critique:
            engine_name = critique.get("ai_engine", "Google Gemini AI" if critique.get("is_ai_generated") else "Built-in Rule Engine (Offline)")
            st.caption(f"*🤖 Engine: {engine_name}*")

            st.markdown("#### Executive Recruiter Summary")
            st.info(critique.get("executive_summary", ""))

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 30-Second Interview Elevator Pitch")
            st.caption("Use this script when interviewers ask: *'Walk me through your background and projects'*")
            pitch_text = critique.get("elevator_pitch", "")
            st.code(pitch_text, language="text")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Ready-to-Use XYZ Resume Bullet Points")
            st.caption("Quantified bullet points based on your GitHub projects formatted for engineering resumes.")
            
            for b in critique.get("resume_bullets", []):
                b_repo = html.escape(str(b.get('repo_name') or ''))
                b_lang = html.escape(str(b.get('language') or ''))
                b_xyz = html.escape(str(b.get('bullet_xyz') or ''))
                b_tip = html.escape(str(b.get('recruiter_tip') or ''))
                st.markdown(f"""
<div class="bullet-box">
    <div style="font-weight: 700; color: #a855f7; margin-bottom: 0.4rem;">
        {b_repo} &nbsp;<span style="color:#8b949e; font-size:0.85rem;">({b_lang})</span>
    </div>
    <div style="color: #f0f6fc; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.6rem;">
        • {b_xyz}
    </div>
    <div style="color: #94a3b8; font-size: 0.85rem;">
        <em>Interview Tip:</em> {b_tip}
    </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Recommended Capstone Project to Build Next")
            st.success(f"**Strategic Recommendation:** {critique.get('capstone_recommendation', '')}", icon="💡")

            if critique.get("interview_talking_points"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### ❓ Likely Technical Interview Questions from Your Repos")
                for q in critique["interview_talking_points"]:
                    st.markdown(f"- 💬 *\"{q}\"*")

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 5: Export Markdown Audit Report
    # ──────────────────────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("### Download Portfolio Audit Report")
        st.caption("Export your complete GitHub audit results as a professionally styled PDF.")

        with st.spinner("Generating PDF report..."):
            try:
                pdf_bytes = generate_github_pdf(gh_data, audit)
                st.download_button(
                    label="Download Audit Report (.pdf)",
                    data=pdf_bytes,
                    file_name=f"DevPilot_GitHub_Audit_{profile.get('login', 'report')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
            except Exception as pdf_err:
                st.warning(f"PDF generation failed ({pdf_err}). Falling back to Markdown.")
                report_md = generate_markdown_report(gh_data, audit)
                st.download_button(
                    label="⬇️ Download Audit Report (.md)",
                    data=report_md,
                    file_name=f"DevPilot_GitHub_Audit_{profile.get('login', 'report')}.md",
                    mime="text/markdown",
                    type="primary",
                    use_container_width=True,
                )

        with st.expander("Preview Report Content", expanded=False):
            report_md_preview = generate_markdown_report(gh_data, audit)
            st.markdown(report_md_preview)

else:
    # Empty State Guide
    st.markdown("""
<div style="background: #161b22; border: 1px dashed #30363d; border-radius: 12px; padding: 2.5rem; text-align: center; color: #8b949e; margin-top: 1rem;">
    <div style="font-size: 3rem; margin-bottom: 0.8rem;"></div>
    <h3 style="color: #f0f6fc; margin-bottom: 0.5rem;">Ready to Audit Your GitHub Presence</h3>
    <p style="max-width: 550px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
        Enter any public GitHub username above to calculate your Developer Portfolio Readiness Score (0–100), audit repository documentation, and generate recruiter-ready resume bullet points.
    </p>
</div>
""", unsafe_allow_html=True)
