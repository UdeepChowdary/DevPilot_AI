"""
🎤 AI Mock Interview & Recruiter Simulator — DevPilot AI
Simulates technical and behavioral software engineering interview loops.
Generates resume-tailored questions, analyzes candidate spoken/text delivery,
evaluates responses across 4 core dimensions, and produces an exportable interview audit.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
import html
import io

# Ensure utils is importable from pages/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.interview_coach import (
    generate_interview_questions,
    evaluate_candidate_answer,
    summarize_interview_session,
    analyze_communication_delivery,
)
from utils.pdf_generator import generate_interview_pdf
from utils.sidebar import render_sidebar
from utils.gemini_client import get_active_gemini_key, render_byok_section

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Mock Interview — DevPilot AI",
    page_icon="🎤",
    layout="wide",
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
render_sidebar()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero-interview {
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
.hero-interview::before {
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
.hero-interview h1 {
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
.hero-interview p {
    font-size: 1rem;
    color: #cbd5e1;
    margin: 0;
    line-height: 1.6;
    position: relative;
    z-index: 1;
}

.question-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(99, 102, 241, 0.28);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    color: #f8fafc;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}
.question-category {
    font-family: 'JetBrains Mono', monospace;
    display: inline-block;
    background: rgba(99,102,241,0.18);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.76rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.question-text {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.5;
    color: #ffffff;
    margin-bottom: 0.8rem;
    letter-spacing: -0.01em;
}
.question-context {
    font-size: 0.88rem;
    color: #94a3b8;
    line-height: 1.55;
}

.feedback-card {
    background: linear-gradient(145deg, #131726, #0e111d);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 1.6rem;
    margin-top: 1.2rem;
    margin-bottom: 1.5rem;
}

.ideal-answer-box {
    background: linear-gradient(145deg, rgba(168, 85, 247, 0.08), rgba(99, 102, 241, 0.05));
    border: 1px solid rgba(168, 85, 247, 0.3);
    border-radius: 12px;
    padding: 1.3rem 1.4rem;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.65;
    margin-top: 1rem;
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

.strength-item { color: #4ade80; padding: 0.25rem 0; font-size: 0.9rem; }
.weakness-item { color: #f87171; padding: 0.25rem 0; font-size: 0.9rem; }

.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-interview">
    <h1>AI Mock Interview &amp; Recruiter Simulator</h1>
    <div class="hero-accent"></div>
    <p>Practice realistic technical and behavioral interviews tailored to your parsed resume. Receive instant recruiter-grade rubrics, speech delivery critique, filler word counts, and exemplary model answers.</p>
</div>
""", unsafe_allow_html=True)

# ─── Session State Initialization ─────────────────────────────────────────────
if "interview_questions" not in st.session_state:
    st.session_state["interview_questions"] = []
if "current_q_index" not in st.session_state:
    st.session_state["current_q_index"] = 0
if "interview_evaluations" not in st.session_state:
    st.session_state["interview_evaluations"] = []
if "interview_session" not in st.session_state:
    st.session_state["interview_session"] = None
if "interview_active" not in st.session_state:
    st.session_state["interview_active"] = False
if "candidate_answers" not in st.session_state:
    st.session_state["candidate_answers"] = {}

# ─── SETUP VIEW (When no interview is active) ─────────────────────────────────
if not st.session_state["interview_active"]:
    col_cfg, col_ctx = st.columns([1.1, 1], gap="large")

    with col_cfg:
        st.markdown("### 1. Interview Setup & Target Role")
        target_role = st.selectbox(
            "Target Engineering Role:",
            options=[
                "Backend Engineer / Systems",
                "Frontend Engineer / UI",
                "Full-Stack Software Engineer",
                "Machine Learning / AI Engineer",
                "DevOps / Cloud Platform Engineer",
                "General SDE-1 / Graduate Placement",
            ],
            index=0,
            help="Calibrates technical depth and domain expectations.",
        )

        company_style = st.selectbox(
            "Target Interview Style:",
            options=[
                "FAANG / Tier-1 Big Tech (High Bar, Deep Tradeoffs)",
                "High-Growth Tech Unicorn (Fast-Paced, Pragmatic)",
                "FinTech / Quantitative (Concurrency, Low-Latency)",
                "Early-Stage Startup (Broad Ownership, Agility)",
            ],
            index=0,
            help="Influences interviewer persona, question difficulty, and evaluation rigor.",
        )

        category_focus = st.radio(
            "Question Mix & Focus:",
            options=[
                "Mixed Technical & Behavioral (Standard Loop)",
                "Deep Technical Architecture & System Design",
                "Behavioral & STAR Leadership Experience",
            ],
            index=0,
        )

        num_q = st.slider("Number of Questions:", min_value=2, max_value=5, value=3)

    with col_ctx:
        st.markdown("### 2. Candidate Context & Resume")
        
        # Check if resume was already parsed in Module 1
        cached_resume = st.session_state.get("resume_results") or {}
        cached_text = cached_resume.get("resume_text", "")
        cached_fname = cached_resume.get("filename", "Uploaded Resume")
        has_cached_resume = bool(cached_text)

        if has_cached_resume and cached_text:
            st.success(f"Loaded active resume: **{cached_fname}** ({len(cached_text.split())} words)")
            use_cached = st.checkbox("Tailor questions to loaded resume profile", value=True)
            resume_input = cached_text if use_cached else ""
        else:
            resume_input = ""
            st.info("Tip: Upload your resume in the **Resume Analyzer** first to automatically customize interview questions to your projects!")

        custom_context = st.text_area(
            "Or paste key skills, technologies, or past projects:",
            value=resume_input[:1500] if resume_input else "",
            placeholder="e.g. 3 years experience with Python, FastAPI, React, PostgreSQL, Docker. Led migration of microservices handling 50k users...",
            height=130,
        )

        st.markdown("#### 3. AI Evaluation & Generation Engine")
        engine_options = [
            "🤗 Hugging Face Neural Engine (Local ML - No API Key Required)",
            "✨ Google Gemini 2.0 Flash (Online Cloud LLM)",
            "⚡ Rule-Based Heuristic Rubric (100% Offline, Instant)",
        ]
        curr_eng = st.session_state.get("interview_engine", "hf")
        def_idx = 0 if curr_eng == "hf" else (1 if curr_eng == "gemini" else 2)

        chosen_eng_label = st.radio(
            "Select Intelligence Engine:",
            options=engine_options,
            index=def_idx,
            help="Choose between offline Hugging Face local transformer inference, Gemini cloud AI, or instant deterministic heuristics.",
            key="interview_engine_choice_radio",
        )
        if "Hugging Face" in chosen_eng_label:
            selected_interview_engine = "hf"
            st.caption("🚀 **Local Neural Engine Active:** Generates dynamic questions and analyzes answer depth on-device without external API calls.")
        elif "Gemini" in chosen_eng_label:
            selected_interview_engine = "gemini"
            render_byok_section(widget_key="interview_byok", compact=False)
        else:
            selected_interview_engine = "offline"
            st.caption("⚡ **Heuristic Engine Active:** Uses curated 30+ question taxonomies and deterministic STAR framework rubrics.")

        st.session_state["interview_engine"] = selected_interview_engine

    st.markdown("<br>", unsafe_allow_html=True)
    start_btn = st.button("Start Mock Interview Session", type="primary", use_container_width=True)

    if start_btn:
        ai_key = get_active_gemini_key()
        chosen_engine = st.session_state.get("interview_engine", "hf")
        if chosen_engine == "gemini" and not ai_key:
            st.warning("⚠️ No Gemini API key detected. Please paste your key in the Bring Your Own Key slot above, or select Hugging Face / Heuristic engine.")
        with st.spinner("Generating tailored interview loop questions..."):
            questions = generate_interview_questions(
                role=target_role,
                company_style=company_style,
                category_focus=category_focus,
                resume_context=custom_context,
                num_questions=num_q,
                api_key=ai_key,
                engine=chosen_engine,
            )

            st.session_state["interview_questions"] = questions
            st.session_state["current_q_index"] = 0
            st.session_state["interview_evaluations"] = []
            st.session_state["interview_session"] = None
            st.session_state["interview_active"] = True
            st.session_state["candidate_answers"] = {}
            st.session_state["session_role"] = target_role
            st.session_state["session_style"] = company_style
            st.session_state["session_engine"] = chosen_engine
            st.rerun()

# ─── ACTIVE INTERVIEW ROOM ───────────────────────────────────────────────────
else:
    questions = st.session_state["interview_questions"]
    curr_idx = st.session_state["current_q_index"]
    total_q = len(questions)

    # Check if session is already completed
    if curr_idx >= total_q or (len(st.session_state["interview_evaluations"]) >= total_q and total_q > 0):
        # ── Summary Scorecard View ──
        if st.session_state["interview_session"] is None:
            st.session_state["interview_session"] = summarize_interview_session(
                evaluations=st.session_state["interview_evaluations"],
                role=st.session_state.get("session_role", "Software Engineer"),
                company_style=st.session_state.get("session_style", "General Tech"),
            )

        summary = st.session_state["interview_session"]
        score = summary["total_score"]
        grade = summary["grade"]
        grade_color = summary["grade_color"]

        st.markdown("### Interview Session Complete!")
        
        col_res1, col_res2 = st.columns([2, 1.2], gap="large")
        with col_res1:
            st.info(f"**Interviewer Verdict:** {summary['verdict']}")
            
            st.markdown("#### Dimension Scorecard")
            dim_cols = st.columns(4)
            for i, (k, d) in enumerate(summary["dimensions"].items()):
                with dim_cols[i]:
                    st.metric(
                        label=d["label"],
                        value=f"{d['score']} / {d['max']}",
                        delta=f"{(d['score']/d['max'])*100:.0f}%",
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            col_st, col_im = st.columns(2)
            with col_st:
                st.markdown("##### Candidate Strengths")
                for s in summary.get("all_strengths", []):
                    st.markdown(f"<div class='strength-item'>✓ {html.escape(str(s))}</div>", unsafe_allow_html=True)
            with col_im:
                st.markdown("##### Key Areas to Practice")
                for imp in summary.get("all_improvements", []):
                    st.markdown(f"<div class='weakness-item'>• {html.escape(str(imp))}</div>", unsafe_allow_html=True)

        with col_res2:
            # Score Gauge
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Interview Readiness<br><span style='font-size:14px; color:{grade_color}'>{grade}</span>", 'font': {'size': 18, 'color': '#ffffff'}},
                number={'suffix': "/100", 'font': {'size': 32, 'color': grade_color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': "#8b949e"},
                    'bar': {'color': grade_color, 'thickness': 0.28},
                    'bgcolor': "#161b22",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                        {'range': [50, 70], 'color': 'rgba(234, 179, 8, 0.15)'},
                        {'range': [70, 82], 'color': 'rgba(99, 102, 241, 0.15)'},
                        {'range': [82, 100], 'color': 'rgba(34, 197, 94, 0.15)'},
                    ],
                }
            ))
            fig_g.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=220,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig_g, use_container_width=True)

        # Question by question review
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        st.markdown("### Question-by-Question Deep Dive")
        for ev in summary.get("evaluations", []):
            with st.expander(f"Question #{ev['question_id']}: {ev['question']} — Score: {ev['overall_score']}/100 ({ev['verdict']})"):
                st.markdown(f"**Candidate Answer:** *\"{ev.get('candidate_answer')}\"*")
                st.markdown("---")
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("**What went well:**")
                    for s in ev.get("strengths", []):
                        st.markdown(f"- {s}")
                with c_b:
                    st.markdown("**Areas to improve:**")
                    for imp in ev.get("areas_to_improve", []):
                        st.markdown(f"- {imp}")
                
                if ev.get("ideal_answer"):
                    st.markdown("""<div class="ideal-answer-box"><b>Exemplary Model Answer:</b><br>""" + html.escape(ev['ideal_answer']) + "</div>", unsafe_allow_html=True)

        # PDF Download CTA
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        with st.spinner("Generating styled PDF interview report..."):
            try:
                pdf_bytes = generate_interview_pdf(summary)
                st.download_button(
                    label="Download Interview Performance Audit (.pdf)",
                    data=pdf_bytes,
                    file_name=f"DevPilot_Interview_Audit_{st.session_state.get('session_role', 'Engineering').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
            except Exception as pdf_err:
                st.error(f"PDF generation error: {pdf_err}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Another Interview Loop", use_container_width=True):
            st.session_state["interview_active"] = False
            st.session_state["interview_session"] = None
            st.session_state["interview_evaluations"] = []
            st.session_state["current_q_index"] = 0
            st.session_state["candidate_answers"] = {}
            st.rerun()

    else:
        # Active question view
        curr_q = questions[curr_idx]

        # Top progress bar
        progress_val = int(((curr_idx + 1) / total_q) * 100)
        st.progress(progress_val, text=f"Question {curr_idx + 1} of {total_q}")

        # Question Header Card
        q_cat = html.escape(str(curr_q.get('category', 'Technical Question')))
        q_text = html.escape(str(curr_q.get('question', '')))
        q_ctx = html.escape(str(curr_q.get('context_reason', 'Evaluates core engineering capabilities.')))
        st.markdown(f"""
<div class="question-card">
    <span class="question-category">{q_cat}</span>
    <div class="question-text">{q_text}</div>
    <div class="question-context"><b>Context:</b> {q_ctx}</div>
</div>
""", unsafe_allow_html=True)

        with st.expander("💡 Interviewer Expectations & Suggested Framework"):
            st.markdown(f"**Recommended Framework:** `{curr_q.get('suggested_framework', 'STAR Method (Situation, Task, Action, Result)')}`")
            st.markdown("**Key concepts senior interviewers listen for:**")
            for exp in curr_q.get("key_expectations", []):
                st.markdown(f"- {exp}")

        # Candidate Response Input Section
        st.markdown("#### Your Response")
        st.caption("You can speak using your microphone, type directly, or combine both.")

        ans_key = f"answer_text_q_{curr_q['id']}"
        saved_text = st.session_state["candidate_answers"].get(curr_q['id'], "")

        # Microphone input using native Streamlit audio_input
        audio_val = st.audio_input("🎤 Record your spoken answer (optional)", key=f"audio_q_{curr_q['id']}")
        
        # Audio transcription button if Gemini key available
        if audio_val is not None:
            ai_key = get_active_gemini_key()
            if ai_key and st.button("Transcribe Audio to Text with Gemini AI", key=f"transcribe_btn_{curr_q['id']}"):
                with st.spinner("Transcribing spoken audio..."):
                    try:
                        from google.genai import types
                        from utils.gemini_client import _get_client
                        sdk_type, client = _get_client(ai_key)
                        if sdk_type == "new":
                            audio_bytes = audio_val.read()
                            part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
                            resp = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=["Please transcribe this candidate's spoken interview answer accurately into English text. Return only the transcription without commentary.", part]
                            )
                            if resp.text:
                                saved_text = resp.text.strip()
                                st.session_state["candidate_answers"][curr_q['id']] = saved_text
                                st.success("Audio transcribed successfully!")
                    except Exception as e:
                        st.warning(f"Audio transcription note: {e}. You can type or edit your answer directly below.")

        candidate_text = st.text_area(
            "Type or edit your response:",
            value=saved_text,
            height=180,
            key=ans_key,
            placeholder="Structure your answer clearly. For behavioral: describe the Situation, Task, Actions you took, and measurable Results. For technical: explain architecture, data flow, tradeoffs, and testing...",
        )
        st.session_state["candidate_answers"][curr_q['id']] = candidate_text

        # Real-time Communication Meter (live filler word counter)
        if candidate_text and len(candidate_text.strip()) > 20:
            comm_preview = analyze_communication_delivery(candidate_text)
            c_p1, c_p2, c_p3 = st.columns(3)
            with c_p1:
                st.caption(f"📝 Word Count: **{comm_preview['word_count']} words**")
            with c_p2:
                fill_color = "#22c55e" if comm_preview['total_fillers'] <= 1 else "#eab308" if comm_preview['total_fillers'] <= 3 else "#ef4444"
                st.caption(f"🗣️ Filler Words: <span style='color:{fill_color}; font-weight:700;'>{comm_preview['total_fillers']} detected</span>", unsafe_allow_html=True)
            with c_p3:
                st.caption(f"⏱️ Pacing: **{comm_preview['pacing_verdict'][:30]}...**")

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([1, 1])

        with col_btn1:
            eval_clicked = st.button("Submit & Evaluate Answer", type="primary", use_container_width=True)

        with col_btn2:
            if curr_idx < total_q - 1:
                skip_btn = st.button("Next Question →", use_container_width=True)
                if skip_btn:
                    st.session_state["current_q_index"] += 1
                    st.rerun()
            else:
                finish_btn = st.button("Complete Interview & View Scorecard →", use_container_width=True)
                if finish_btn:
                    st.session_state["current_q_index"] = total_q
                    st.rerun()

        # Handle Answer Submission & Evaluation
        if eval_clicked:
            if not candidate_text.strip():
                st.warning("Please type or record a response before submitting.")
            else:
                with st.spinner("Staff Engineer AI is analyzing your response across 4 dimensions..."):
                    ai_key = get_active_gemini_key()
                    eval_engine = st.session_state.get("session_engine", st.session_state.get("interview_engine", "hf"))
                    evaluation = evaluate_candidate_answer(
                        question_obj=curr_q,
                        candidate_answer=candidate_text,
                        role=st.session_state.get("session_role", "Software Engineer"),
                        company_style=st.session_state.get("session_style", "General Tech"),
                        api_key=ai_key,
                        engine=eval_engine,
                    )

                    # Update or append evaluation in session state
                    existing_idx = next((i for i, e in enumerate(st.session_state["interview_evaluations"]) if e["question_id"] == curr_q["id"]), None)
                    if existing_idx is not None:
                        st.session_state["interview_evaluations"][existing_idx] = evaluation
                    else:
                        st.session_state["interview_evaluations"].append(evaluation)

                    # Also update interview_session in session_state for real-time sidebar KPI
                    st.session_state["interview_session"] = summarize_interview_session(
                        evaluations=st.session_state["interview_evaluations"],
                        role=st.session_state.get("session_role", "Software Engineer"),
                        company_style=st.session_state.get("session_style", "General Tech"),
                    )

        # Display Evaluation if already evaluated for this question
        curr_eval = next((e for e in st.session_state["interview_evaluations"] if e["question_id"] == curr_q["id"]), None)
        if curr_eval:
            eng_tag = curr_eval.get("ai_engine", "AI Evaluator")
            st.markdown(f"""
<div class="feedback-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.5rem;">
        <div>
            <span style="font-size:1.1rem; font-weight:700; color:#f8fafc;">Question Scorecard</span>
            <span style="font-size:0.75rem; background:rgba(99,102,241,0.18); border:1px solid rgba(99,102,241,0.4); color:#a5b4fc; padding:2px 8px; border-radius:12px; margin-left:8px; font-weight:600;">{eng_tag}</span>
        </div>
        <span class="stat-pill" style="border-color:#6366f1; color:#818cf8; font-weight:800; font-size:1rem;">
            {curr_eval['overall_score']} / 100 ({curr_eval['verdict']})
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

            d_cols = st.columns(4)
            d_keys = [
                ("technical_depth", "Technical Depth"),
                ("structure", "Structure / STAR"),
                ("communication", "Delivery & Pacing"),
                ("tradeoffs_metrics", "Tradeoffs & Metrics"),
            ]
            for idx, (dkey, dlabel) in enumerate(d_keys):
                d_score = curr_eval["dimension_scores"].get(dkey, 0)
                with d_cols[idx]:
                    st.metric(dlabel, f"{d_score} / 25")

            st.markdown("<br>", unsafe_allow_html=True)
            col_pos, col_neg = st.columns(2)
            with col_pos:
                st.markdown("##### Strengths:")
                for s in curr_eval.get("strengths", []):
                    st.markdown(f"<div class='strength-item'>✓ {html.escape(str(s))}</div>", unsafe_allow_html=True)
            with col_neg:
                st.markdown("##### Missing Points & Improvements:")
                for imp in curr_eval.get("areas_to_improve", []):
                    st.markdown(f"<div class='weakness-item'>• {html.escape(str(imp))}</div>", unsafe_allow_html=True)

            if curr_eval.get("ideal_answer"):
                st.markdown(f"""
<div class="ideal-answer-box">
    <b>💡 Exemplary Model Answer (How a Senior / Staff Engineer would answer):</b><br><br>
    {html.escape(curr_eval['ideal_answer'])}
</div>
""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if curr_idx < total_q - 1:
                if st.button("Continue to Next Question →", type="primary", use_container_width=True):
                    st.session_state["current_q_index"] += 1
                    st.rerun()
            else:
                if st.button("Complete Interview & View Final Scorecard →", type="primary", use_container_width=True):
                    st.session_state["current_q_index"] = total_q
                    st.rerun()
