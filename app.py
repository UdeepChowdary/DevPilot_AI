import streamlit as st

st.set_page_config(
    page_title="DevPilot AI — Engineering Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

/* ── Hero ──────────────────────────────────────────────────────── */
.hero-main {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    border-radius: 20px;
    padding: 3.2rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(99, 102, 241, 0.25);
}
.hero-main::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-main::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-main h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: white;
    margin: 0 0 0.75rem 0;
    line-height: 1.15;
    position: relative;
    z-index: 1;
}
.hero-accent {
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    border-radius: 2px;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
}
.hero-main .tagline {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.8);
    margin: 0 0 1.5rem 0;
    max-width: 650px;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}
.hero-stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 1;
}
.hero-stat {
    text-align: center;
}
.hero-stat .stat-num {
    font-size: 1.6rem;
    font-weight: 800;
    color: #a78bfa;
    display: block;
    line-height: 1;
}
.hero-stat .stat-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: block;
    margin-top: 0.2rem;
}
.hero-divider {
    width: 1px;
    background: rgba(255,255,255,0.15);
    align-self: stretch;
}
.badge-row { position: relative; z-index: 1; }
.badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    border: 1px solid rgba(99,102,241,0.4);
    color: #818cf8;
    border-radius: 20px;
    padding: 0.35rem 0.95rem;
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
    transition: background 0.2s ease, border-color 0.2s ease;
}
.badge:hover {
    background: rgba(99,102,241,0.35);
    border-color: rgba(99,102,241,0.7);
}

/* ── Module Cards ──────────────────────────────────────────────── */
.module-card {
    background: linear-gradient(135deg, #1e1e2e, #1a1a2e);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 1.6rem;
    margin-bottom: 0.8rem;
    transition: all 0.25s ease-in-out;
    cursor: default;
    height: 260px;
    display: flex;
    flex-direction: column;
}
.module-card:hover {
    border-color: rgba(99,102,241,0.55);
    box-shadow: 0 8px 28px rgba(99,102,241,0.15);
    transform: translateY(-3px);
}
.module-card.soon {
    opacity: 0.75;
}
.module-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
.module-title { font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 0.4rem; }
.module-desc  { font-size: 0.86rem; color: #94a3b8; line-height: 1.55; flex-grow: 1; }
.module-status-live {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: 0.75rem;
}
.module-status-soon {
    display: inline-block;
    background: rgba(100,116,139,0.15);
    color: #64748b;
    border: 1px solid rgba(100,116,139,0.2);
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: 0.75rem;
}

/* ── Stack chips ───────────────────────────────────────────────── */
.stack-chip {
    display: inline-block;
    background: rgba(15,12,41,0.6);
    border: 1px solid rgba(99,102,241,0.2);
    color: #94a3b8;
    border-radius: 8px;
    padding: 0.35rem 0.85rem;
    font-size: 0.8rem;
    margin: 0.25rem;
    transition: border-color 0.2s ease, color 0.2s ease;
}
.stack-chip:hover {
    border-color: rgba(99,102,241,0.5);
    color: #c4b5fd;
}

/* ── Gradient divider ──────────────────────────────────────────── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
    margin: 1.5rem 0;
}

/* ── Sidebar enhancements ──────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
    <div style="font-size:1.5rem; font-weight:800; color:white; margin-top:0.3rem;">DevPilot AI</div>
    <div style="font-size:0.75rem; color:#6366f1; font-weight:600; letter-spacing:0.05em;">ENGINEERING DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("**Navigation**")
    st.page_link("app.py", label="Home", use_container_width=True)
    st.page_link("pages/1_Resume_Analyzer.py", label="Resume Analyzer", use_container_width=True)
    st.page_link("pages/2_GitHub_Analyzer.py", label="GitHub Profile Analyzer", use_container_width=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # Show session scores if analysis has been done
    resume_score = st.session_state.get("resume_results", {}).get("ats", {}).get("total")
    github_score = st.session_state.get("github_audit", {}).get("total_score")

    if resume_score is not None or github_score is not None:
        st.markdown("**Your Scores**")
        if resume_score is not None:
            color = "#22c55e" if resume_score >= 75 else "#eab308" if resume_score >= 50 else "#ef4444"
            st.markdown(f"""
<div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
     border-radius:10px; padding:0.75rem 1rem; margin-bottom:0.5rem;">
    <div style="font-size:0.75rem; color:#94a3b8;">Resume ATS Score</div>
    <div style="font-size:1.6rem; font-weight:800; color:{color};">{resume_score}<span style="font-size:0.9rem; color:#64748b;">/100</span></div>
</div>
""", unsafe_allow_html=True)
        if github_score is not None:
            color = "#22c55e" if github_score >= 70 else "#eab308" if github_score >= 50 else "#ef4444"
            st.markdown(f"""
<div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
     border-radius:10px; padding:0.75rem 1rem; margin-bottom:0.5rem;">
    <div style="font-size:0.75rem; color:#94a3b8;">GitHub Portfolio Score</div>
    <div style="font-size:1.6rem; font-weight:800; color:{color};">{github_score}<span style="font-size:0.9rem; color:#64748b;">/100</span></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
<div style="font-size:0.75rem; color:#475569; text-align:center; line-height:1.6;">
    Built for software engineering students<br>
    <a href="https://github.com/UdeepChowdary/DevPilot_AI" target="_blank"
       style="color:#6366f1; text-decoration:none;">Star on GitHub</a>
</div>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-main">
    <h1>DevPilot AI</h1>
    <div class="hero-accent"></div>
    <p class="tagline">Your Personal Software Engineering Placement & Interview Dashboard. Powered by ML text analytics and AI intelligence to accelerate your career readiness.</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="stat-num">200+</span>
            <span class="stat-label">Skills Tracked</span>
        </div>
        <div class="hero-divider"></div>
        <div class="hero-stat">
            <span class="stat-num">5</span>
            <span class="stat-label">Score Dimensions</span>
        </div>
        <div class="hero-divider"></div>
        <div class="hero-stat">
            <span class="stat-num">3</span>
            <span class="stat-label">AI Engines</span>
        </div>
        <div class="hero-divider"></div>
        <div class="hero-stat">
            <span class="stat-num">100%</span>
            <span class="stat-label">Offline Capable</span>
        </div>
    </div>
    <div class="badge-row">
        <span class="badge">ML & NLP Powered</span>
        <span class="badge">Instant Heuristic Engine</span>
        <span class="badge">Optional Gemini AI</span>
        <span class="badge">Free & Open Source</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Module Cards ──────────────────────────────────────────────────────────────
st.markdown("### Modules")

modules = [
    {
        "icon": "📄",
        "title": "Resume Analyzer",
        "desc": "ATS scoring with TF-IDF, keyword matching via RAKE + spaCy, section validator, and Google XYZ bullet rewriter.",
        "status": "live",
        "page": "pages/1_Resume_Analyzer.py",
    },
    {
        "icon": "🐙",
        "title": "GitHub Profile Analyzer",
        "desc": "Portfolio readiness scoring (0–100), repository hygiene audit, language breakdown, and AI resume bullets.",
        "status": "live",
        "page": "pages/2_GitHub_Analyzer.py",
    },
    {
        "icon": "💻",
        "title": "AI Code Reviewer",
        "desc": "Detect bugs, code smells, calculate time/space complexity, and generate refactoring suggestions.",
        "status": "soon",
    },
    {
        "icon": "🎤",
        "title": "AI Mock Interview",
        "desc": "Resume-based technical & behavioral interview simulations with real-time feedback.",
        "status": "soon",
    },
    {
        "icon": "🎯",
        "title": "LeetCode Coach",
        "desc": "Track coding progress, identify weak algorithmic topics, and generate targeted practice plans.",
        "status": "soon",
    },
    {
        "icon": "📊",
        "title": "Placement Readiness Dashboard",
        "desc": "Track overall preparation, calculate readiness score, and manage interview milestones.",
        "status": "soon",
    },
]

cols = st.columns(3, gap="medium")
for i, mod in enumerate(modules):
    with cols[i % 3]:
        status_html = (
            '<span class="module-status-live">Live</span>'
            if mod["status"] == "live"
            else '<span class="module-status-soon">🔜 Coming Soon</span>'
        )
        card_class = "module-card" if mod["status"] == "live" else "module-card soon"
        st.markdown(f"""
<div class="{card_class}">
    <div class="module-icon">{mod["icon"]}</div>
    <div class="module-title">{mod["title"]}</div>
    <div class="module-desc">{mod["desc"]}</div>
    {status_html}
</div>
""", unsafe_allow_html=True)
        if mod.get("page"):
            st.page_link(mod["page"], label=f"Launch {mod['title']} →", use_container_width=True)

st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.markdown("### Tech Stack & Architecture")
stack = [
    "Streamlit", "Python 3.10+", "PyMuPDF", "python-docx", "scikit-learn",
    "spaCy", "NLTK", "RAKE-NLTK", "Google Gemini AI", "HuggingFace Transformers",
    "Plotly Express",
]
chips = "".join(f"<span class='stack-chip'>{s}</span>" for s in stack)
st.markdown(chips, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#64748b; font-size:0.85rem; text-align:center;'>DevPilot AI • Built for software engineering students</p>",
    unsafe_allow_html=True,
)
