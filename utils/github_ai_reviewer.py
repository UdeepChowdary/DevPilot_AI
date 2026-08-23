"""
🧠 GitHub AI Portfolio Reviewer & Resume Translator — DevPilot AI
Generates LLM-powered portfolio critiques, recruiter elevator pitches,
and transforms GitHub repositories into Silicon-Valley-ready XYZ resume bullet points.
Falls back seamlessly to offline heuristic rule-based recommendations.
"""

from typing import Dict, List, Any, Optional
import json
import os
from utils.gemini_client import ask_json


def generate_rule_based_critique(
    profile_data: Dict[str, Any],
    audit_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    100% offline heuristic generator for portfolio critique and resume bullets.
    """
    profile = profile_data.get("profile", {})
    top_repos = profile_data.get("top_repos", [])
    username = profile.get("login", "Developer")
    name = profile.get("name") or username

    # Languages
    lang_bytes = profile_data.get("language_bytes", {})
    top_langs = sorted(lang_bytes.keys(), key=lambda x: lang_bytes[x], reverse=True)[:3]
    lang_str = ", ".join(top_langs) if top_langs else "modern software engineering tools"

    # Pitch
    elevator_pitch = (
        f"Hi, I'm {name}, a software engineer specializing in {lang_str}. "
        f"Across my GitHub, I focus on building practical applications with clean architecture and scalable backends. "
        f"My featured work includes {top_repos[0]['name'] if top_repos else 'interactive web applications'}, "
        f"where I engineered core modules emphasizing reliability and developer experience."
    )

    # Resume Bullets for Top Repos
    resume_bullets = []
    for r in top_repos[:3]:
        r_name = r.get("name", "Project")
        r_lang = r.get("language", "Python")
        r_desc = r.get("description") or "full-stack application"
        stars = r.get("stargazers_count", 0)

        metric_hint = f"earning {stars} GitHub stars and positive developer adoption" if stars > 2 else "reducing latency by ~35% through modular design"

        resume_bullets.append({
            "repo_name": r_name,
            "language": r_lang,
            "bullet_xyz": f"Architected **{r_name}**, a {r_desc.lower().rstrip('.')}, utilizing **{r_lang}**; achieved optimized throughput and responsive UX ({metric_hint}).",
            "recruiter_tip": f"Highlight system architecture decisions, data structures used, and any deployed demo links when discussing {r_name} in technical interviews.",
        })

    # Recommended next project
    has_ml = any("python" in str(r.get("language", "")).lower() or "ai" in str(r.get("name", "")).lower() for r in top_repos)
    has_web = any(r.get("language") in ["TypeScript", "JavaScript", "React", "HTML"] for r in top_repos)

    if has_ml and not has_web:
        capstone_suggestion = "Build a Full-Stack AI SaaS: Wrap your ML models in a FastAPI backend with a modern React/Next.js frontend and deploy it to production with auth & telemetry."
    elif has_web and not has_ml:
        capstone_suggestion = "Build a Real-Time Distributed System: Create an event-driven architecture using WebSockets, Redis caching, and PostgreSQL with Dockerized CI/CD pipelines."
    else:
        capstone_suggestion = "Build a Production-Grade Cloud Microservice: Implement an end-to-end service featuring JWT authentication, automated test suites (pytest/jest), and GitHub Actions CI/CD."

    return {
        "is_ai_generated": False,
        "executive_summary": f"Portfolio shows strong technical foundation in {lang_str} with {len(top_repos)} original projects. Prioritizing live deployment links and detailed README architecture diagrams will significantly increase recruiter callbacks.",
        "elevator_pitch": elevator_pitch,
        "resume_bullets": resume_bullets,
        "capstone_recommendation": capstone_suggestion,
        "interview_talking_points": [
            f"Explain how you structured the state management and API contracts in {top_repos[0]['name'] if top_repos else 'your primary project'}.",
            "Discuss trade-offs you made between different libraries, databases, or frameworks.",
            "Walk through a challenging bug or performance bottleneck you resolved in one of your public repositories.",
        ],
    }


def generate_ai_critique(
    profile_data: Dict[str, Any],
    audit_data: Dict[str, Any],
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an AI-powered portfolio critique using Google Gemini.
    Falls back to rule-based critique on error or missing API key.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or not key.strip():
        return generate_rule_based_critique(profile_data, audit_data)

    profile = profile_data.get("profile", {})
    top_repos = profile_data.get("top_repos", [])[:4]
    stats = profile_data.get("stats", {})
    score = audit_data.get("total_score", 0)

    repos_context = []
    for r in top_repos:
        repos_context.append({
            "name": r.get("name"),
            "language": r.get("language"),
            "description": r.get("description"),
            "stars": r.get("stargazers_count", 0),
            "has_homepage": bool(r.get("homepage")),
            "topics": r.get("topics", []),
        })

    prompt = f"""
You are a Senior Tech Recruiter and Principal Software Engineering Hiring Manager at top tech companies.
Review this software engineer candidate's GitHub portfolio data and provide strategic career guidance.

Candidate Data:
- Username: {profile.get('login')}
- Name: {profile.get('name', 'Developer')}
- Bio: {profile.get('bio', 'None')}
- Portfolio Link: {profile.get('blog', 'None')}
- Developer Readiness Score: {score}/100
- Public Original Repos: {stats.get('original_repo_count', 0)}
- Top Languages: {list(profile_data.get('language_bytes', {}).keys())[:4]}
- Top Repositories: {json.dumps(repos_context, indent=2)}

Return a strict JSON object with this EXACT structure (no markdown fences, just pure JSON):
{{
  "executive_summary": "2-3 concise sentences evaluating the candidate's portfolio strengths and recruiter appeal.",
  "elevator_pitch": "A polished 30-45 second spoken intro ('Tell me about yourself / walk me through your GitHub') tailored to their actual projects.",
  "resume_bullets": [
    {{
      "repo_name": "RepoName",
      "language": "Primary Language",
      "bullet_xyz": "Accomplished [X], as measured by [Y], by doing [Z] bullet point formatted with strong action verb and technical depth.",
      "recruiter_tip": "Specific advice on what to emphasize about this project in technical interviews."
    }}
  ],
  "capstone_recommendation": "1 specific high-value project idea the candidate should build next to fill any obvious portfolio gap.",
  "interview_talking_points": [
    "3 specific, insightful technical interview questions a hiring manager would ask based on their repos."
  ]
}}
"""

    try:
        result = ask_json(prompt, api_key=key.strip())
        if isinstance(result, dict) and "executive_summary" in result and "resume_bullets" in result:
            result["is_ai_generated"] = True
            return result
    except Exception:
        # Fall back gracefully to rule-based on any LLM parsing/network failure
        pass

    return generate_rule_based_critique(profile_data, audit_data)
