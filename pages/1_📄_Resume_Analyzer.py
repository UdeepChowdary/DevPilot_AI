"""
📄 Resume Analyzer — DevPilot AI
Analyzes resumes using ML (TF-IDF, RAKE, spaCy) and AI Bullet Enhancement (Rule-Based, Gemini, T5).
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Ensure utils is importable from the pages/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.resume_parser import extract_text, detect_sections, extract_bullet_points
from utils.ats_scorer import score_resume
from utils.keyword_extractor import extract_keywords, compare_keywords
from utils.bullet_enhancer import enhance_bullets

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer — DevPilot AI",
    page_icon="📄",
    layout="wide",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 2.2rem;
    margin-bottom: 1.5rem;
    color: white;
}
.hero h1 { font-size: 2.2rem; font-weight: 700; margin: 0 0 0.5rem 0; }
.hero p  { font-size: 1rem; opacity: 0.85; margin: 0; }

.score-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    color: white;
}
.score-number {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.kw-chip-match {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    border: 1px solid rgba(34,197,94,0.4);
    color: #22c55e;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.8rem;
    font-weight: 500;
}
.kw-chip-miss {
    display: inline-block;
    background: rgba(239,68,68,0.15);
    border: 1px solid rgba(239,68,68,0.4);
    color: #ef4444;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.8rem;
    font-weight: 500;
}
.kw-chip-neutral {
    display: inline-block;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    color: #818cf8;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.8rem;
    font-weight: 500;
}

.bullet-card {
    background: #1e1e2e;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    border-left: 4px solid #6366f1;
}
.bullet-original { color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.5rem; }
.bullet-enhanced { color: #f8fafc; font-size: 0.95rem; font-weight: 500; }
.bullet-tag {
    display: inline-block;
    font-size: 0.72rem;
    background: rgba(99,102,241,0.2);
    color: #818cf8;
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-top: 0.4rem;
}
.metric-tag {
    display: inline-block;
    font-size: 0.72rem;
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-left: 0.4rem;
}
.no-metric-tag {
    display: inline-block;
    font-size: 0.72rem;
    background: rgba(234,179,8,0.15);
    color: #eab308;
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-left: 0.4rem;
}
.ai-tag {
    display: inline-block;
    font-size: 0.72rem;
    background: rgba(168,85,247,0.2);
    color: #c084fc;
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-left: 0.4rem;
}

.strength-item { color: #22c55e; padding: 0.25rem 0; font-size: 0.9rem; }
.weakness-item { color: #f87171; padding: 0.25rem 0; font-size: 0.9rem; }

div[data-testid="stTabs"] button { font-weight: 600; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📄 Resume Analyzer</h1>
    <p>ATS scoring, keyword alignment, section validation, and AI-powered bullet enhancement for software engineering roles.</p>
</div>
""", unsafe_allow_html=True)

# ─── Upload Section ───────────────────────────────────────────────────────────
col_upload, col_jd = st.columns([1, 1], gap="large")

with col_upload:
    st.subheader("1. Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Supports PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        help="Upload your resume in PDF, Word (.docx), or plain text format.",
    )

with col_jd:
    st.subheader("2. Paste Job Description (Optional)")
    jd_text = st.text_area(
        "Job Description",
        placeholder="Paste the target job description to unlock targeted keyword matching, missing skill analysis, and role alignment...",
        height=160,
        label_visibility="collapsed",
    )

# ─── Advanced Options ─────────────────────────────────────────────────────────
with st.expander("⚙️ Enhancement Engine & AI Options"):
    opt_col1, opt_col2 = st.columns(2)
    with opt_col1:
        enhancement_mode = st.radio(
            "Bullet Rewriting Mode:",
            options=["rule_based", "gemini", "t5"],
            format_func=lambda x: {
                "rule_based": "⚡ Fast Rule-Based (Instant, 100% Offline)",
                "gemini": "🧠 Gemini AI Mode (Google XYZ Formula)",
                "t5": "🤖 Local T5 Model (Offline Neural)",
            }[x],
            index=0,
            help="Choose how weak bullet points are enhanced into high-impact accomplishments.",
        )
    with opt_col2:
        if enhancement_mode == "gemini":
            has_env_key = bool(os.getenv("GEMINI_API_KEY"))
            if not has_env_key:
                user_key = st.text_input(
                    "Enter Gemini API Key (optional if in .env):",
                    type="password",
                    help="Used only for generating smart Google XYZ bullet rewrites.",
                )
                if user_key:
                    os.environ["GEMINI_API_KEY"] = user_key
            else:
                st.success("✅ GEMINI_API_KEY detected from environment.")
        elif enhancement_mode == "t5":
            st.info("ℹ️ T5-small runs locally and downloads ~240MB weights on first execution.")

# ─── Analyze Button ───────────────────────────────────────────────────────────
analyze_clicked = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True,
    disabled=(uploaded_file is None),
)

if uploaded_file is None:
    st.info("👆 Upload your resume (PDF, DOCX, TXT) to begin.")
    st.stop()

# ─── Run Analysis ─────────────────────────────────────────────────────────────
if analyze_clicked or "resume_results" in st.session_state:

    if analyze_clicked:
        with st.spinner("🔬 Extracting text, analyzing ATS factors, and extracting keywords..."):
            try:
                # 1. Extract text
                resume_text = extract_text(uploaded_file)
                if not resume_text or not resume_text.strip():
                    st.error("Could not extract readable text from the file. Please ensure the document contains selectable text.")
                    st.stop()

                # 2. Detect sections
                sections = detect_sections(resume_text)

                # 3. ATS Score
                ats_result = score_resume(resume_text, jd_text or None, sections)

                # 4. Keywords
                if jd_text and len(jd_text.strip()) > 20:
                    kw_result = compare_keywords(resume_text, jd_text)
                else:
                    kw_result = {
                        "matched": [],
                        "missing": [],
                        "resume_only": [],
                        "resume_keywords": extract_keywords(resume_text, 35),
                        "jd_keywords": [],
                        "match_rate": 0.0,
                    }

                # 5. Bullet enhancement
                bullets = extract_bullet_points(resume_text)
                bullet_results = enhance_bullets(bullets[:15], mode=enhancement_mode)

                # Cache in session state
                st.session_state["resume_results"] = {
                    "ats":         ats_result,
                    "kw":          kw_result,
                    "bullets":     bullet_results,
                    "sections":    sections,
                    "resume_text": resume_text,
                    "filename":    uploaded_file.name,
                }

            except Exception as e:
                st.error(f"Analysis encountered an error: {e}")
                st.stop()

    results = st.session_state.get("resume_results")
    if not results:
        st.stop()

    ats         = results["ats"]
    kw          = results["kw"]
    bullets     = results["bullets"]
    sections    = results["sections"]
    resume_text = results["resume_text"]
    score       = ats["total"]

    st.divider()

    # ─── Top Stats Bar & Report Exporter ──────────────────────────────────────────
    top_c1, top_c2, top_c3, top_c4 = st.columns([1, 1, 1, 1])
    with top_c1:
        st.metric("Total ATS Score", f"{score} / 100")
    with top_c2:
        wc = len(resume_text.split())
        st.metric("Resume Length", f"{wc} words", delta="Optimal" if 350 <= wc <= 850 else "Check length")
    with top_c3:
        sec_count = len([k for k in sections.keys() if k != "other"])
        st.metric("Key Sections", f"{sec_count} detected")
    with top_c4:
        # Generate Markdown Report for Download
        report_md = f"""# DevPilot AI — Resume ATS Audit Report
**File:** {results.get('filename', 'Resume')}
**Overall ATS Score:** {score}/100

---

## 📊 Score Breakdown
""" + "\n".join([f"- **{b['label']}:** {b['score']} / {b['max']}" for b in ats["breakdown"]]) + f"""

## ✅ Key Strengths
""" + "\n".join([f"- {s}" for s in ats["strengths"]]) + f"""

## ⚠️ Areas for Improvement
""" + "\n".join([f"- {w}" for w in ats["weaknesses"]]) + f"""

## 🔑 Keyword Analysis
- **Matched Keywords ({len(kw['matched'])}):** {', '.join(kw['matched']) if kw['matched'] else 'N/A'}
- **Missing JD Keywords ({len(kw['missing'])}):** {', '.join(kw['missing']) if kw['missing'] else 'N/A'}

## ✨ Enhanced Bullet Suggestions
""" + "\n".join([f"### Original:\n> {b['original']}\n**Enhanced:**\n> {b['enhanced']}\n*Note:* {b['explanation']}\n" for b in bullets])

        st.download_button(
            label="📥 Download Audit Report",
            data=report_md,
            file_name="resume_ats_audit_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── 4 Result Tabs ────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 ATS Score", "🔑 Keywords", "✨ Enhanced Bullets", "📄 Parsed Content"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — ATS Score
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        col_g, col_sw = st.columns([1, 1], gap="large")
        with col_g:
            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"suffix": "/100", "font": {"size": 38, "color": "white"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                    "bar":  {"color": "#6366f1", "thickness": 0.3},
                    "bgcolor": "#1e1e2e",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  45],  "color": "#1e293b"},
                        {"range": [45, 75],  "color": "#1e1e2e"},
                        {"range": [75, 100], "color": "#1a1a2e"},
                    ],
                    "threshold": {
                        "line": {"color": "#a855f7", "width": 4},
                        "thickness": 0.8,
                        "value": 75,
                    },
                },
                title={"text": "ATS Readiness Gauge", "font": {"color": "#94a3b8", "size": 16}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=290,
                margin=dict(t=40, b=0, l=30, r=30),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            if score >= 80:
                label, color = "🟢 Excellent (Interview Ready)", "#22c55e"
            elif score >= 65:
                label, color = "🟡 Competitive (Minor Improvements Needed)", "#eab308"
            elif score >= 45:
                label, color = "🟠 Needs Refinement", "#f97316"
            else:
                label, color = "🔴 Weak ATS Profile", "#ef4444"
            st.markdown(f"<p style='text-align:center; color:{color}; font-size:1.15rem; font-weight:600'>{label}</p>", unsafe_allow_html=True)

        with col_sw:
            col_s, col_w = st.columns(2)
            with col_s:
                st.markdown("#### ✅ Strengths")
                for s in ats["strengths"]:
                    st.markdown(f"<div class='strength-item'>✓ {s}</div>", unsafe_allow_html=True)
            with col_w:
                st.markdown("#### ⚠️ Areas to Improve")
                for w in ats["weaknesses"]:
                    st.markdown(f"<div class='weakness-item'>✗ {w}</div>", unsafe_allow_html=True)

        st.markdown("#### Score Component Breakdown")
        labels  = [b["label"]  for b in ats["breakdown"]]
        scores  = [b["score"]  for b in ats["breakdown"]]
        maxvals = [b["max"]    for b in ats["breakdown"]]
        pct     = [round((s / m) * 100) if m > 0 else 0 for s, m in zip(scores, maxvals)]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=pct, y=labels, orientation="h",
            marker_color=["#6366f1" if p >= 75 else "#f97316" if p >= 50 else "#ef4444" for p in pct],
            text=[f"{s} / {m} pts ({p}%)" for s, m, p in zip(scores, maxvals, pct)],
            textposition="inside",
            textfont_color="white",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 100], ticksuffix="%", color="#64748b", gridcolor="#1e293b"),
            yaxis=dict(color="#94a3b8", autorange="reversed"),
            font_color="white",
            height=280,
            margin=dict(t=10, b=10, l=10, r=20),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — Keywords
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        if kw["jd_keywords"]:
            col_m, col_mi = st.columns(2, gap="large")
            with col_m:
                st.markdown(f"### ✅ Matched Keywords ({len(kw['matched'])})")
                if kw["matched"]:
                    chips = "".join(f"<span class='kw-chip-match'>{k}</span>" for k in kw["matched"])
                    st.markdown(chips, unsafe_allow_html=True)
                else:
                    st.warning("No direct keyword matches found. Ensure skills match JD terminology.")

            with col_mi:
                st.markdown(f"### ❌ Missing Keywords from JD ({len(kw['missing'])})")
                if kw["missing"]:
                    chips = "".join(f"<span class='kw-chip-miss'>{k}</span>" for k in kw["missing"])
                    st.markdown(chips, unsafe_allow_html=True)
                    st.caption("💡 Tip: Integrate relevant missing keywords naturally into your experience & project bullets.")
                else:
                    st.success("🎯 Perfect match! Your resume covers all key job requirements.")

            if kw["matched"] or kw["missing"]:
                fig_pie = px.pie(
                    names=["Matched Skills", "Missing Skills"],
                    values=[len(kw["matched"]), len(kw["missing"])],
                    color=["Matched Skills", "Missing Skills"],
                    color_discrete_map={"Matched Skills": "#22c55e", "Missing Skills": "#ef4444"},
                    hole=0.5,
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    legend=dict(font_color="white"),
                    height=260,
                    margin=dict(t=20, b=10),
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown("### 🔑 Extracted Resume Keywords")
            st.caption("No Job Description was provided. Displaying key skills and technologies identified in your resume:")
            chips = "".join(f"<span class='kw-chip-neutral'>{k}</span>" for k in kw["resume_keywords"])
            st.markdown(chips, unsafe_allow_html=True)
            st.info("💡 Paste a target job description in the upload area to see matched vs. missing skills.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — Enhanced Bullets
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        if not bullets:
            st.warning("No bullet points detected. Ensure your experience and project sections use bullet points (•, -, *) or action statements.")
        else:
            st.markdown(f"**Analyzed {len(bullets)} bullet points.** Showing optimized accomplishment statements:")

            for i, item in enumerate(bullets):
                metric_html = (
                    "<span class='metric-tag'>📊 Quantified</span>"
                    if item["has_metric"]
                    else "<span class='no-metric-tag'>💡 Tip: Add metric (%, ms, $)</span>"
                )
                ai_html = "<span class='ai-tag'>🧠 Gemini AI</span>" if item.get("ai_suggestion") else ""
                tag_html = f"<span class='bullet-tag'>{item['explanation']}</span>{metric_html}{ai_html}"

                st.markdown(f"""
<div class="bullet-card">
    <div class="bullet-original"><strong>Original:</strong> {item['original']}</div>
    <div class="bullet-enhanced"><strong>Enhanced:</strong> {item['enhanced']}</div>
    {tag_html}
</div>
""", unsafe_allow_html=True)
                # Quick 1-click copy block
                st.code(item['enhanced'], language="text")

            st.divider()
            st.markdown("#### 💡 Google's XYZ Resume Formula Guide")
            tip_c1, tip_c2 = st.columns(2)
            with tip_c1:
                st.markdown("""
- **Formula:** *"Accomplished **[X]** as measured by **[Y]**, by doing **[Z]**"*
- **Action Verbs:** Start every bullet with a high-impact verb (*Engineered, Spearheaded, Architected*).
""")
            with tip_c2:
                st.markdown("""
- **Quantify Everything:** Include %, latency drops, user count, requests/sec, or team size.
- **Conciseness:** Keep bullets to 1–2 lines max to ensure readability by hiring managers.
""")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — Parsed Content & Layout
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 📄 Raw Text & Section Mapping")
        st.caption("Verify that your resume's text was cleanly parsed without layout corruption.")

        st.markdown("#### Detected Sections:")
        for s_name, s_content in sections.items():
            with st.expander(f"📁 {s_name.upper()} ({len(s_content.split())} words)"):
                st.text(s_content)
