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
}
.hero-main h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: white;
    margin: 0 0 0.75rem 0;
    line-height: 1.15;
}
.hero-main .tagline {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.8);
    margin: 0 0 1.75rem 0;
    max-width: 650px;
    line-height: 1.6;
}
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
}

.module-card {
    background: linear-gradient(135deg, #1e1e2e, #1a1a2e);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 1.6rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease-in-out;
}
.module-card:hover {
    border-color: rgba(99,102,241,0.55);
    box-shadow: 0 8px 24px rgba(99,102,241,0.12);
}
.module-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
.module-title { font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 0.4rem; }
.module-desc  { font-size: 0.86rem; color: #94a3b8; line-height: 1.55; min-height: 52px; }
.module-status-live {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    color: #22c55e;
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
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: 0.75rem;
}

.stack-chip {
    display: inline-block;
    background: rgba(15,12,41,0.6);
    border: 1px solid rgba(99,102,241,0.2);
    color: #94a3b8;
    border-radius: 8px;
    padding: 0.35rem 0.85rem;
    font-size: 0.8rem;
    margin: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-main">
    <h1>🚀 DevPilot AI</h1>
    <p class="tagline">Your Personal Software Engineering Placement & Interview Dashboard. Powered by ML text analytics and AI intelligence to accelerate your career readiness.</p>
    <span class="badge">🧠 ML & NLP Powered</span>
    <span class="badge">⚡ Instant Heuristic Engine</span>
    <span class="badge">🤖 Optional Gemini AI</span>
    <span class="badge">🆓 Free & Open Source</span>
</div>
""", unsafe_allow_html=True)

# ── Module Cards ──────────────────────────────────────────────────────────────
st.markdown("### 🌟 Modules")

modules = [
    {
        "icon": "📄",
        "title": "Resume Analyzer",
        "desc": "ATS scoring with TF-IDF, keyword matching via RAKE + spaCy, section validator, and Google XYZ bullet rewriter.",
        "status": "live",
        "page": "pages/1_📄_Resume_Analyzer.py",
    },
    {
        "icon": "🐙",
        "title": "GitHub Profile Analyzer",
        "desc": "Repo quality scoring, commit consistency, language breakdown, and project quality assessment.",
        "status": "soon",
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
        "icon": "🧠",
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
            '<span class="module-status-live">✅ Live</span>'
            if mod["status"] == "live"
            else '<span class="module-status-soon">🔜 Coming Soon</span>'
        )
        st.markdown(f"""
<div class="module-card">
    <div class="module-icon">{mod["icon"]}</div>
    <div class="module-title">{mod["title"]}</div>
    <div class="module-desc">{mod["desc"]}</div>
    {status_html}
</div>
""", unsafe_allow_html=True)
        if mod.get("page"):
            st.page_link(mod["page"], label=f"Launch {mod['title']} →", icon="🚀", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.markdown("### 🛠️ Tech Stack & Architecture")
stack = [
    "Streamlit", "Python 3.10+", "PyMuPDF", "python-docx", "scikit-learn",
    "spaCy", "NLTK", "RAKE-NLTK", "Google Gemini AI", "HuggingFace Transformers",
    "Plotly Express", "SQLite",
]
chips = "".join(f"<span class='stack-chip'>{s}</span>" for s in stack)
st.markdown(chips, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#64748b; font-size:0.85rem; text-align:center;'>DevPilot AI • Built with ❤️ for software engineering students</p>",
    unsafe_allow_html=True,
)
