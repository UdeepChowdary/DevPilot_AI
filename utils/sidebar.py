"""
Shared sidebar renderer for DevPilot AI.
Call render_sidebar() at the top of every page to ensure consistent navigation,
branding, and session-state score display across all Streamlit pages.
"""

import streamlit as st


SIDEBAR_CSS = """
<style>
/* Hide Streamlit's auto-generated page navigation — we use our own */
[data-testid="stSidebarNav"] {
    display: none !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%) !important;
}
.sidebar-logo-name {
    font-size: 1.5rem;
    font-weight: 800;
    color: white;
    margin-top: 0.3rem;
}
.sidebar-logo-sub {
    font-size: 0.75rem;
    color: #6366f1;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.sidebar-score-card {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.sidebar-score-label {
    font-size: 0.75rem;
    color: #94a3b8;
}
.sidebar-gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
    margin: 1rem 0;
}
</style>
"""


def render_sidebar() -> None:
    """
    Render the shared DevPilot AI sidebar with navigation, scores, and footer.
    Call this at the top of every page file after st.set_page_config().
    """
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # ── Logo / Branding ────────────────────────────────────────────────
        st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
    <div class="sidebar-logo-name">DevPilot AI</div>
    <div class="sidebar-logo-sub">ENGINEERING DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────────────
        st.markdown("**Navigation**")
        st.page_link("app.py", label="🏠  Home", use_container_width=True)
        st.page_link("pages/1_Resume_Analyzer.py", label="📄  Resume Analyzer", use_container_width=True)
        st.page_link("pages/2_GitHub_Analyzer.py", label="🐙  GitHub Profile Analyzer", use_container_width=True)

        # Code Reviewer — link shown only once the page file exists
        import os as _os
        _cr_path = _os.path.join(_os.path.dirname(__file__), "..", "pages", "3_Code_Reviewer.py")
        if _os.path.exists(_cr_path):
            st.page_link("pages/3_Code_Reviewer.py", label="💻  AI Code Reviewer", use_container_width=True)
        else:
            st.markdown(
                "<div style='padding:0.4rem 0.75rem; color:#475569; font-size:0.85rem;'>💻 AI Code Reviewer <span style='font-size:0.72rem; color:#6366f1;'>coming soon</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='sidebar-gradient-divider'></div>", unsafe_allow_html=True)

        # ── Session Scores ────────────────────────────────────────────────
        resume_score = st.session_state.get("resume_results", {}).get("ats", {}).get("total")
        github_score = st.session_state.get("github_audit", {}).get("total_score")

        if resume_score is not None or github_score is not None:
            st.markdown("**Your Scores**")

            if resume_score is not None:
                color = "#22c55e" if resume_score >= 75 else "#eab308" if resume_score >= 50 else "#ef4444"
                st.markdown(f"""
<div class="sidebar-score-card">
    <div class="sidebar-score-label">Resume ATS Score</div>
    <div style="font-size:1.6rem; font-weight:800; color:{color};">
        {resume_score}<span style="font-size:0.9rem; color:#64748b;">/100</span>
    </div>
</div>
""", unsafe_allow_html=True)

            if github_score is not None:
                color = "#22c55e" if github_score >= 70 else "#eab308" if github_score >= 50 else "#ef4444"
                st.markdown(f"""
<div class="sidebar-score-card">
    <div class="sidebar-score-label">GitHub Portfolio Score</div>
    <div style="font-size:1.6rem; font-weight:800; color:{color};">
        {github_score}<span style="font-size:0.9rem; color:#64748b;">/100</span>
    </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("<div class='sidebar-gradient-divider'></div>", unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────────────
        st.markdown("""
<div style="font-size:0.75rem; color:#475569; text-align:center; line-height:1.6;">
    Built for software engineering students<br>
    <a href="https://github.com/UdeepChowdary/DevPilot_AI" target="_blank"
       style="color:#6366f1; text-decoration:none;">⭐ Star on GitHub</a>
</div>
""", unsafe_allow_html=True)
