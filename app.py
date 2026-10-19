import streamlit as st
import sys, os, base64
sys.path.insert(0, os.path.dirname(__file__))
from utils.sidebar import render_sidebar

# ── Logo helper ───────────────────────────────────────────────────────────────
def _logo_b64() -> str:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

_LOGO_URI = f"data:image/png;base64,{_logo_b64()}"

st.set_page_config(
    page_title="DevPilot AI — Engineering Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Hero ──────────────────────────────────────────────────────── */
.hero-main {
    background: linear-gradient(135deg, #090d16 0%, #151b2e 50%, #1e1b4b 100%);
    border-radius: 20px;
    padding: 3rem 2.8rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(99, 102, 241, 0.28);
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
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
    font-family: 'Sora', sans-serif !important;
    font-size: 2.8rem;
    font-weight: 800;
    color: white;
    margin: 0 0 0.6rem 0;
    letter-spacing: -0.03em;
    line-height: 1.15;
    position: relative;
    z-index: 1;
}
.hero-accent {
    width: 55px;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    border-radius: 2px;
    margin-bottom: 1.1rem;
    position: relative;
    z-index: 1;
}
.hero-main .tagline {
    font-size: 1.08rem;
    color: #cbd5e1;
    margin: 0 0 1.6rem 0;
    max-width: 680px;
    line-height: 1.65;
    position: relative;
    z-index: 1;
}
.hero-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
    margin-bottom: 1.6rem;
    position: relative;
    z-index: 1;
}
.hero-stat {
    text-align: left;
}
.hero-stat .stat-num {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.75rem;
    font-weight: 800;
    color: #c4b5fd;
    display: block;
    line-height: 1;
    letter-spacing: -0.02em;
}
.hero-stat .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: block;
    margin-top: 0.35rem;
}
.hero-divider {
    width: 1px;
    background: rgba(255,255,255,0.12);
    align-self: stretch;
}
.badge-row { position: relative; z-index: 1; }
.badge {
    display: inline-block;
    background: rgba(99,102,241,0.14);
    border: 1px solid rgba(99,102,241,0.32);
    color: #a5b4fc;
    border-radius: 20px;
    padding: 0.32rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
    transition: all 0.2s ease;
}
.badge:hover {
    background: rgba(99,102,241,0.25);
    border-color: rgba(99,102,241,0.6);
    color: #ffffff;
}

/* ── Module Cards ──────────────────────────────────────────────── */
.module-card {
    background: linear-gradient(145deg, #131726 0%, #0e111d 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 1.6rem;
    margin-bottom: 0.8rem;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    cursor: default;
    min-height: 250px;
    display: flex;
    flex-direction: column;
}
.module-card:hover {
    border-color: rgba(99,102,241,0.48);
    box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(99, 102, 241, 0.35);
    transform: translateY(-4px);
}
.module-card.soon {
    opacity: 0.75;
}
.module-icon-wrap {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 0.9rem;
}
.module-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.12rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.45rem;
    letter-spacing: -0.01em;
}
.module-desc  {
    font-size: 0.86rem;
    color: #94a3b8;
    line-height: 1.6;
    flex-grow: 1;
}
.module-status-live {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(34,197,94,0.12);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 0.85rem;
    width: fit-content;
}
.module-status-soon {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(100,116,139,0.15);
    color: #94a3b8;
    border: 1px solid rgba(100,116,139,0.25);
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 0.85rem;
    width: fit-content;
}

/* ── Stack chips ───────────────────────────────────────────────── */
.stack-chip {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(15,18,30,0.7);
    border: 1px solid rgba(99,102,241,0.2);
    color: #94a3b8;
    border-radius: 6px;
    padding: 0.35rem 0.8rem;
    font-size: 0.78rem;
    margin: 0.25rem;
    transition: all 0.2s ease;
}
.stack-chip:hover {
    border-color: rgba(99,102,241,0.55);
    color: #c4b5fd;
    background: rgba(99,102,241,0.1);
}

/* ── Gradient divider ──────────────────────────────────────────── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
    margin: 1.6rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-main">
    <img src="{_LOGO_URI}" alt="DevPilot AI" style="height:72px; margin-bottom:1rem; display:block; filter: drop-shadow(0 0 18px rgba(168,85,247,0.45));" />
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
        <span class="badge">Gemini AI (BYOK Support)</span>
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
        "icon": "🎤",
        "title": "AI Mock Interview",
        "desc": "Resume-tailored technical & behavioral interview simulations with real-time feedback and speech pacing analysis.",
        "status": "live",
        "page": "pages/3_Mock_Interview.py",
    },
    {
        "icon": "🎯",
        "title": "LeetCode Coach",
        "desc": "Algorithmic topic radar, weak-pattern diagnostics, curated company roadmaps, and AI code complexity optimization.",
        "status": "live",
        "page": "pages/4_LeetCode_Coach.py",
    },
    {
        "icon": "📊",
        "title": "Placement Readiness Dashboard",
        "desc": "Track overall preparation, calculate readiness score, and manage interview milestones.",
        "status": "live",
        "page": "pages/5_Placement_Dashboard.py",
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
    <div class="module-icon-wrap">{mod["icon"]}</div>
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
    "Streamlit", "Python 3.10+", "Firebase (Auth & Firestore)", "PyMuPDF", "python-docx", "scikit-learn",
    "spaCy", "NLTK", "RAKE-NLTK", "Google Gemini AI", "HuggingFace Transformers",
    "Plotly Express",
]
chips = "".join(f"<span class='stack-chip'>{s}</span>" for s in stack)
st.markdown(chips, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#64748b; font-size:0.85rem; text-align:center;'>DevPilot AI <span style='color:#818cf8; font-weight:600;'>v3.2.2</span> • Built for software engineering students</p>",
    unsafe_allow_html=True,
)

