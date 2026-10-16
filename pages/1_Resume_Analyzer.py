"""
Resume Analyzer — DevPilot AI
Analyzes resumes using ML (TF-IDF, RAKE, spaCy) and AI Bullet Enhancement (Rule-Based, Gemini, T5).
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import html

# Ensure utils is importable from the pages/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.resume_parser import extract_text, detect_sections, extract_bullet_points
from utils.ats_scorer import score_resume
from utils.keyword_extractor import extract_keywords, compare_keywords
from utils.bullet_enhancer import enhance_bullets
from utils.pdf_generator import generate_resume_pdf
from utils.sidebar import render_sidebar
from utils.gemini_client import get_active_gemini_key, render_byok_section

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer — DevPilot AI",
    page_icon="📄",
    layout="wide",
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
render_sidebar()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #090d16 0%, #151b2e 50%, #1e1b4b 100%);
    border-radius: 18px;
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.8rem;
    color: #ffffff;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(99, 102, 241, 0.28);
    box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.7);
}
.hero::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -5%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero h1 {
    font-family: 'Sora', sans-serif !important;
    font-size: 2.3rem;
    font-weight: 800;
    color: #ffffff;
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
.hero p {
    font-size: 1rem;
    color: #cbd5e1;
    margin: 0;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

/* ── Upload drop zone ── */
div[data-testid="stFileUploadDropzone"] {
    background: rgba(99,102,241,0.06) !important;
    border: 1px dashed rgba(99,102,241,0.4) !important;
    border-radius: 14px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stFileUploadDropzone"]:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.7) !important;
}

/* ── Score card ── */
.score-card {
    background: linear-gradient(145deg, #131726 0%, #0e111d 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 14px;
    padding: 1.6rem;
    text-align: center;
    color: white;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}
.score-number {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-variant-numeric: tabular-nums;
}

/* ── Keyword chips ── */
.kw-chip-match {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.35);
    color: #4ade80;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.78rem;
    font-weight: 600;
}
.kw-chip-miss {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.35);
    color: #f87171;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.78rem;
    font-weight: 600;
}
.kw-chip-neutral {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    margin: 0.2rem;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── Bullet side-by-side card ── */
.bullet-card {
    background: linear-gradient(145deg, #131726 0%, #0e111d 100%);
    border: 1px solid rgba(99, 102, 241, 0.22);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.1rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.bullet-card:hover {
    border-color: rgba(99, 102, 241, 0.45);
    box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.5);
}
.bullet-col-label {
    font-family: 'Sora', sans-serif;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.45rem;
}
.bullet-original-label { color: #94a3b8; }
.bullet-enhanced-label { color: #a5b4fc; }
.bullet-text-original { color: #94a3b8; font-size: 0.88rem; line-height: 1.6; }
.bullet-text-enhanced { color: #f8fafc; font-size: 0.92rem; font-weight: 500; line-height: 1.6; }
.bullet-tags { grid-column: 1 / -1; display:flex; flex-wrap:wrap; gap:0.35rem; margin-top:0.4rem; }
.bullet-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: rgba(99,102,241,0.18);
    color: #a5b4fc;
    border-radius: 5px;
    padding: 0.18rem 0.55rem;
}
.metric-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: rgba(34,197,94,0.15);
    color: #4ade80;
    border-radius: 5px;
    padding: 0.18rem 0.55rem;
}
.no-metric-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: rgba(234,179,8,0.15);
    color: #facc15;
    border-radius: 5px;
    padding: 0.18rem 0.55rem;
}
.ai-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: rgba(168,85,247,0.18);
    color: #d8b4fe;
    border-radius: 5px;
    padding: 0.18rem 0.55rem;
}

.strength-item { color: #4ade80; padding: 0.25rem 0; font-size: 0.9rem; }
.weakness-item { color: #f87171; padding: 0.25rem 0; font-size: 0.9rem; }

.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
    margin: 1.6rem 0;
}

/* ── Score verdict badge ── */
.score-verdict {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    border-radius: 30px;
    padding: 0.5rem 1.4rem;
    font-size: 0.92rem;
    font-weight: 700;
    margin-top: 0.6rem;
    border: 1px solid;
}

div[data-testid="stTabs"] button { font-weight: 600; font-size: 0.95rem; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #64748b;
}
.empty-state .es-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-state .es-title { font-family: 'Sora', sans-serif; font-size: 1.15rem; font-weight: 700; color: #cbd5e1; margin-bottom: 0.5rem; }
.empty-state .es-sub { font-size: 0.9rem; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Resume Analyzer</h1>
    <div class="hero-accent"></div>
    <p>ATS scoring, keyword alignment, section validation, and AI-powered bullet enhancement for software engineering roles.</p>
</div>
""", unsafe_allow_html=True)

# ─── Upload Section ───────────────────────────────────────────────────────────
col_upload, col_jd = st.columns([1, 1], gap="large")

with col_upload:
    st.subheader("1. Upload Your Resume")
    st.caption("Drag & drop or browse — PDF, DOCX, or TXT supported")
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
            "Bullet Rewriting & AI Engine:",
            options=["t5", "gemini", "rule_based"],
            format_func=lambda x: {
                "t5": "🤗 Hugging Face Local Neural Engine (T5, 100% Offline, No Key)",
                "gemini": "✨ Google Gemini 2.0 Flash (Online Cloud LLM, API Key)",
                "rule_based": "⚡ Fast Rule-Based Heuristic (Instant, Zero Dependencies)",
            }[x],
            index=0,
            help="Choose how weak bullet points are analyzed and enhanced into high-impact accomplishments.",
        )
    with opt_col2:
        if enhancement_mode == "t5":
            st.info(
                "🤗 **Hugging Face Local Neural Engine**: Runs directly on your machine via PyTorch & Transformers. "
                "100% private and offline Google XYZ bullet transformation without external API keys."
            )
        elif enhancement_mode == "gemini":
            render_byok_section(widget_key="resume_byok", compact=False)
        elif enhancement_mode == "rule_based":
            st.caption("Fast deterministic heuristic engine with action verb swaps and metric verification.")

# ─── Analyze Button ───────────────────────────────────────────────────────────
analyze_clicked = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True,
    disabled=(uploaded_file is None),
)

if uploaded_file is None and "resume_results" not in st.session_state:
    st.markdown("""
<div class="empty-state">
    <div class="es-icon">📄</div>
    <div class="es-title">No resume uploaded yet</div>
    <div class="es-sub">Upload your resume above (PDF, DOCX, or TXT) to get your ATS score, keyword analysis, and bullet improvements.</div>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ─── Run Analysis ─────────────────────────────────────────────────────────────
if analyze_clicked or "resume_results" in st.session_state:

    if analyze_clicked:
        # File size defense (5 MB ceiling)
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("File size exceeds 5 MB limit. Please upload a smaller document.")
            st.stop()

        # Staged progress messages for better UX
        progress_bar = st.progress(0, text="🔬 Starting analysis...")
        try:
            progress_bar.progress(10, text="📑 Extracting text from document...")
            resume_text = extract_text(uploaded_file)
            if not resume_text or not resume_text.strip():
                st.error("Could not extract readable text from the file. Please ensure the document contains selectable text.")
                st.stop()

            progress_bar.progress(30, text="Detecting resume sections...")
            sections = detect_sections(resume_text)

            progress_bar.progress(50, text="Calculating ATS score...")
            ats_result = score_resume(resume_text, jd_text or None, sections)

            progress_bar.progress(65, text="Extracting & matching keywords...")
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

            progress_bar.progress(80, text="Enhancing bullet points...")
            bullets = extract_bullet_points(resume_text)
            gemini_key = get_active_gemini_key()
            if enhancement_mode == "gemini" and not gemini_key:
                st.warning("⚠️ No Gemini API key detected. Using offline heuristic engine instead. Paste your key in the BYOK slot to enable Gemini.")

            if enhancement_mode == "t5":
                # T5 may trigger a ~240MB model download on first run.
                # Wrap in st.status so the user sees progress instead of a frozen screen.
                with st.status(
                    "⏳ Loading T5 neural model (first run downloads ~240MB)…",
                    expanded=True,
                ) as _t5_status:
                    st.write("Downloading `t5-small` from HuggingFace Hub…")
                    st.write("This is a one-time download. Subsequent runs are instant.")
                    bullet_results = enhance_bullets(bullets[:15], mode="t5", api_key=gemini_key)
                    _t5_status.update(
                        label="✅ T5 model loaded and bullets enhanced!",
                        state="complete",
                        expanded=False,
                    )
            else:
                bullet_results = enhance_bullets(bullets[:15], mode=enhancement_mode, api_key=gemini_key)

            progress_bar.progress(100, text="Analysis complete!")

            # Cache in session state
            st.session_state["resume_results"] = {
                "ats":         ats_result,
                "kw":          kw_result,
                "bullets":     bullet_results,
                "sections":    sections,
                "resume_text": resume_text,
                "filename":    uploaded_file.name,
            }

            # Auto-sync to Firebase if user is authenticated
            try:
                from utils.firebase_db import sync_module_to_cloud_async
                sync_module_to_cloud_async("resume")
            except Exception:
                pass


        except Exception as e:
            progress_bar.empty()
            st.error(f"Analysis encountered an error: {e}")
            st.stop()
        finally:
            progress_bar.empty()

    results = st.session_state.get("resume_results")
    if not results:
        st.stop()

    ats         = results["ats"]
    kw          = results["kw"]
    bullets     = results["bullets"]
    sections    = results["sections"]
    resume_text = results["resume_text"]
    score       = ats["total"]

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ─── Top Stats Bar ────────────────────────────────────────────────────────
    top_c1, top_c2, top_c3 = st.columns([1, 1, 1])
    with top_c1:
        st.metric("Total ATS Score", f"{score} / 100")
    with top_c2:
        wc = len(resume_text.split())
        st.metric("Resume Length", f"{wc} words", delta="Optimal" if 350 <= wc <= 850 else "Check length")
    with top_c3:
        sec_count = len([k for k in sections.keys() if k != "other"])
        st.metric("Key Sections", f"{sec_count} detected")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── 4 Result Tabs ────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["ATS Score", "Keywords", "Enhanced Bullets", "Parsed Content"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — ATS Score
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        col_g, col_sw = st.columns([1, 1], gap="large")
        with col_g:
            # Score verdict badge (shown above gauge for immediate clarity)
            if score >= 80:
                verdict_label = "Excellent — Interview Ready"
                verdict_color = "#22c55e"
                verdict_bg    = "rgba(34,197,94,0.12)"
                verdict_border= "rgba(34,197,94,0.4)"
            elif score >= 65:
                verdict_label = "🟡 Competitive — Minor Tweaks Needed"
                verdict_color = "#eab308"
                verdict_bg    = "rgba(234,179,8,0.12)"
                verdict_border= "rgba(234,179,8,0.4)"
            elif score >= 45:
                verdict_label = "🟠 Needs Refinement"
                verdict_color = "#f97316"
                verdict_bg    = "rgba(249,115,22,0.12)"
                verdict_border= "rgba(249,115,22,0.4)"
            else:
                verdict_label = "Weak ATS Profile"
                verdict_color = "#ef4444"
                verdict_bg    = "rgba(239,68,68,0.12)"
                verdict_border= "rgba(239,68,68,0.4)"

            st.markdown(
                f"<div style='text-align:center; margin-bottom:0.5rem;'>"
                f"<span class='score-verdict' style='color:{verdict_color}; background:{verdict_bg}; border-color:{verdict_border};'>{verdict_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Gauge chart — thresholds now match the verdict labels above
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
                        {"range": [45, 65],  "color": "#1e2030"},
                        {"range": [65, 80],  "color": "#1a2040"},
                        {"range": [80, 100], "color": "#1a2535"},
                    ],
                    "threshold": {
                        "line": {"color": "#a855f7", "width": 4},
                        "thickness": 0.8,
                        "value": 80,
                    },
                },
                title={"text": "ATS Readiness Score", "font": {"color": "#94a3b8", "size": 15}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=280,
                margin=dict(t=40, b=0, l=30, r=30),
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_sw:
            col_s, col_w = st.columns(2)
            with col_s:
                st.markdown("#### Strengths")
                for s in ats["strengths"]:
                    st.markdown(f"<div class='strength-item'>✓ {s}</div>", unsafe_allow_html=True)
            with col_w:
                st.markdown("#### ⚠️ Areas to Improve")
                for w in ats["weaknesses"]:
                    st.markdown(f"<div class='weakness-item'>✗ {w}</div>", unsafe_allow_html=True)

        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
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
                st.markdown(f"### Matched Keywords ({len(kw['matched'])})")
                if kw["matched"]:
                    chips = "".join(f"<span class='kw-chip-match'>{html.escape(k)}</span>" for k in kw["matched"])
                    st.markdown(f"<div style='line-height:2.2;'>{chips}</div>", unsafe_allow_html=True)
                else:
                    st.warning("No direct keyword matches found. Ensure skills match JD terminology.")

            with col_mi:
                st.markdown(f"### Missing Keywords from JD ({len(kw['missing'])})")
                if kw["missing"]:
                    chips = "".join(f"<span class='kw-chip-miss'>{html.escape(k)}</span>" for k in kw["missing"])
                    st.markdown(f"<div style='line-height:2.2;'>{chips}</div>", unsafe_allow_html=True)
                    st.caption("Tip: Integrate relevant missing keywords naturally into your experience & project bullets.")
                else:
                    st.success("Perfect match! Your resume covers all key job requirements.")

            if kw["matched"] or kw["missing"]:
                fig_pie = px.pie(
                    names=["Matched Skills", "Missing Skills"],
                    values=[len(kw["matched"]), len(kw["missing"])],
                    color=["Matched Skills", "Missing Skills"],
                    color_discrete_map={"Matched Skills": "#22c55e", "Missing Skills": "#ef4444"},
                    hole=0.55,
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
            st.markdown("### Extracted Resume Keywords")
            st.caption("No Job Description was provided. Displaying key skills and technologies identified in your resume:")
            chips = "".join(f"<span class='kw-chip-neutral'>{html.escape(k)}</span>" for k in kw["resume_keywords"])
            st.markdown(f"<div style='line-height:2.2;'>{chips}</div>", unsafe_allow_html=True)
            st.info("Paste a target job description in the upload area to see matched vs. missing skills.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — Enhanced Bullets (side-by-side layout)
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        if not bullets:
            st.markdown("""
<div class="empty-state">
    <div class="es-icon">📝</div>
    <div class="es-title">No bullet points detected</div>
    <div class="es-sub">Ensure your experience and project sections use bullet points (•, -, *) or start lines with action verbs.</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"**Analyzed {len(bullets)} bullet points** — showing original vs. enhanced side-by-side:")
            st.markdown("<br>", unsafe_allow_html=True)

            for i, item in enumerate(bullets):
                metric_tag = (
                    "<span class='metric-tag'>Quantified</span>"
                    if item["has_metric"]
                    else "<span class='no-metric-tag'>Add metric (%, ms, $)</span>"
                )
                ai_tag_html = "<span class='ai-tag'>Gemini AI</span>" if item.get("ai_suggestion") else ""
                explanation_tag = f"<span class='bullet-tag'>{html.escape(str(item['explanation']))}</span>"
                orig_esc = html.escape(str(item['original']))
                enh_esc = html.escape(str(item['enhanced']))

                st.markdown(f"""
<div class="bullet-card">
    <div>
        <div class="bullet-col-label bullet-original-label">Original</div>
        <div class="bullet-text-original">{orig_esc}</div>
    </div>
    <div>
        <div class="bullet-col-label bullet-enhanced-label">Enhanced</div>
        <div class="bullet-text-enhanced">{enh_esc}</div>
    </div>
    <div class="bullet-tags">
        {explanation_tag} {metric_tag} {ai_tag_html}
    </div>
</div>
""", unsafe_allow_html=True)
                # Quick copy block
                st.code(item['enhanced'], language="text")

            st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
            st.markdown("#### Google's XYZ Resume Formula Guide")
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
        st.markdown("### Raw Text & Section Mapping")
        st.caption("Verify that your resume's text was cleanly parsed without layout corruption.")

        st.markdown("#### Detected Sections:")
        for s_name, s_content in sections.items():
            with st.expander(f"📁 {s_name.upper()} ({len(s_content.split())} words)"):
                st.text(s_content)

    # ─── Download Report (primary CTA at bottom) ───────────────────────────
    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    with st.spinner("Generating PDF report..."):
        try:
            pdf_bytes = generate_resume_pdf(results)
            st.download_button(
                label="Download ATS Audit Report (.pdf)",
                data=pdf_bytes,
                file_name="resume_ats_audit_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
        except Exception as pdf_err:
            st.error(f"PDF generation failed: {pdf_err}")
