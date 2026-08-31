"""
📊 GitHub Profile Scorer & Auditor — DevPilot AI
Computes a normalized Developer Portfolio Readiness Score (0–100) across 5 core dimensions:
1. Profile Completeness (15 pts)
2. Repository Quality & Hygiene (35 pts)
3. Activity & Consistency (25 pts)
4. Language & Tech Stack Depth (15 pts)
5. Community & Impact (10 pts)
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone
import re


def _parse_iso_date(date_str: str) -> datetime:
    """Parse GitHub ISO 8601 timestamps safely."""
    try:
        # Handle 'Z' suffix or standard ISO formats
        if date_str.endswith("Z"):
            date_str = date_str[:-1] + "+00:00"
        return datetime.fromisoformat(date_str)
    except Exception:
        return datetime.now(timezone.utc)


def score_profile_completeness(profile: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
    """
    Score profile metadata completeness out of 15.
    Returns (score, strengths, improvements).
    """
    score = 0.0
    strengths = []
    improvements = []

    # Bio check (up to 4 pts)
    bio = (profile.get("bio") or "").strip()
    if len(bio) >= 20:
        score += 4.0
        strengths.append("Professional, descriptive GitHub bio present.")
    elif len(bio) > 0:
        score += 2.0
        improvements.append("Expand your GitHub bio to mention your target engineering role or tech specialties.")
    else:
        improvements.append("Add a GitHub bio highlighting your primary engineering skills and focus areas.")

    # Name check (2 pts)
    name = (profile.get("name") or "").strip()
    if name and name.lower() != (profile.get("login") or "").lower():
        score += 2.0
        strengths.append(f"Full display name configured ({name}).")
    elif name:
        score += 1.0
    else:
        improvements.append("Set your full real name on your profile so recruiters can identify you.")

    # Avatar check (2 pts)
    avatar_url = profile.get("avatar_url") or ""
    if avatar_url and "identicon" not in avatar_url and "gravatar.com/avatar/?d=" not in avatar_url:
        score += 2.0
    else:
        improvements.append("Upload a clear, professional profile picture instead of default avatar.")

    # Portfolio / Blog link (3 pts)
    blog = (profile.get("blog") or "").strip()
    if blog:
        score += 3.0
        strengths.append("External portfolio/LinkedIn/blog link is prominently linked.")
    else:
        improvements.append("Link your LinkedIn, personal website, or portfolio in your GitHub profile header.")

    # Location (2 pts)
    location = (profile.get("location") or "").strip()
    if location:
        score += 2.0
        strengths.append(f"Location configured ({location}).")
    else:
        improvements.append("Specify your location or timezone to help recruiters target local/remote roles.")

    # Company / University (2 pts)
    company = (profile.get("company") or "").strip()
    if company:
        score += 2.0
        strengths.append(f"Organization / University affiliation specified ({company}).")
    else:
        improvements.append("Add your university or current organization to the company field.")

    return min(score, 15.0), strengths, improvements


def score_repo_quality(
    original_repos: List[Dict[str, Any]],
    forked_repos: List[Dict[str, Any]],
) -> Tuple[float, List[str], List[str], List[Dict[str, Any]]]:
    """
    Score repository hygiene, documentation, licenses, and demo links out of 35.
    Returns (score, strengths, improvements, repo_audits).
    """
    score = 0.0
    strengths = []
    improvements = []
    repo_audits = []

    total_orig = len(original_repos)
    total_forks = len(forked_repos)
    total_all = total_orig + total_forks

    if total_all == 0:
        return 0.0, [], ["No public repositories found. Create and publish project code to showcase."], []

    # 1. Original vs Fork ratio (up to 7 pts)
    orig_ratio = total_orig / total_all if total_all > 0 else 0
    if orig_ratio >= 0.7 and total_orig >= 3:
        score += 7.0
        strengths.append(f"Strong portfolio ownership ({total_orig} original projects, {orig_ratio*100:.0f}% original).")
    elif orig_ratio >= 0.4:
        score += 4.5
        improvements.append("Focus on showcasing original personal/team projects rather than forking repositories.")
    else:
        score += 2.0
        improvements.append("Most repositories are forks. Build and pin standalone original engineering projects.")

    # 2. Description coverage (up to 8 pts)
    repos_with_desc = [r for r in original_repos if r.get("description") and len(r["description"].strip()) >= 10]
    desc_ratio = len(repos_with_desc) / total_orig if total_orig > 0 else 0
    if desc_ratio >= 0.8:
        score += 8.0
        strengths.append(f"Excellent description coverage: {desc_ratio*100:.0f}% of projects have concise summaries.")
    elif desc_ratio >= 0.5:
        score += 5.0
        improvements.append("Add 1-line clear descriptions to all repository headers explaining what each project does.")
    else:
        score += 2.0
        improvements.append("Critical: Multiple repositories lack descriptions. Recruiters scan repo taglines first.")

    # 3. Open Source Licenses (up to 5 pts)
    repos_with_license = [r for r in original_repos if r.get("license")]
    lic_ratio = len(repos_with_license) / total_orig if total_orig > 0 else 0
    if lic_ratio >= 0.6:
        score += 5.0
        strengths.append("Great open-source hygiene with recognized OSS licenses (MIT/Apache).")
    elif lic_ratio >= 0.25:
        score += 3.0
        improvements.append("Add an open-source license (e.g. MIT License) to your main repositories.")
    else:
        score += 1.0
        improvements.append("Add an open source license (MIT / Apache 2.0) to demonstrate production hygiene.")

    # 4. Live Demos & Deployment URLs (up to 8 pts)
    repos_with_demo = [
        r for r in original_repos
        if r.get("homepage") and r["homepage"].strip().startswith("http")
    ]
    if len(repos_with_demo) >= 3:
        score += 8.0
        strengths.append(f"Outstanding! {len(repos_with_demo)} projects have live deployed URLs / documentation links.")
    elif len(repos_with_demo) >= 1:
        score += 5.0
        improvements.append("Deploy more of your web/API/app projects to free tiers (Vercel, Render, HF Spaces, Railway).")
    else:
        score += 1.0
        improvements.append("High Impact: 0 projects have live demo links. Deploy your top projects so recruiters can test them.")

    # 5. Topic Tags Usage (up to 4 pts)
    repos_with_topics = [r for r in original_repos if r.get("topics") and len(r["topics"]) > 0]
    topic_ratio = len(repos_with_topics) / total_orig if total_orig > 0 else 0
    if topic_ratio >= 0.5:
        score += 4.0
        strengths.append("Repositories are well-tagged with relevant tech keywords & topics.")
    elif topic_ratio > 0:
        score += 2.0
        improvements.append("Add GitHub topic tags (e.g. `react`, `fastapi`, `machine-learning`) to boost searchability.")
    else:
        improvements.append("Add GitHub repository topics/tags to highlight your tech stacks at a glance.")

    # 6. Repository-level health audits (up to 20 repos for broader coverage)
    for r in original_repos[:20]:
        has_desc = bool(r.get("description") and len(r["description"].strip()) >= 10)
        has_lic = bool(r.get("license"))
        has_demo = bool(r.get("homepage") and r["homepage"].strip().startswith("http"))
        has_top = bool(r.get("topics") and len(r["topics"]) > 0)
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)

        # Health calc for single repo
        repo_h = 25  # base
        if has_desc: repo_h += 25
        if has_lic:  repo_h += 15
        if has_demo: repo_h += 20
        if has_top:  repo_h += 15

        repo_suggestions = []
        if not has_desc:
            repo_suggestions.append("Add a concise description explaining the problem and tech stack.")
        if not has_demo:
            repo_suggestions.append("Provide a live demo URL or hosted preview link.")
        if not has_lic:
            repo_suggestions.append("Add an open-source MIT or Apache 2.0 license file.")
        if not has_top:
            repo_suggestions.append("Add 3-5 topic keywords (e.g., #python, #fullstack).")

        repo_audits.append({
            "name": r.get("name"),
            "full_name": r.get("full_name"),
            "html_url": r.get("html_url"),
            "description": r.get("description") or "No description provided.",
            "language": r.get("language") or "Other",
            "stars": stars,
            "forks": forks,
            "has_description": has_desc,
            "has_license": has_lic,
            "has_homepage": has_demo,
            "has_topics": has_top,
            "homepage": r.get("homepage"),
            "health_score": min(repo_h, 100),
            "suggestions": repo_suggestions,
            "updated_at": r.get("updated_at"),
            "pushed_at": r.get("pushed_at"),
        })

    # README / documentation bonus (up to 3 pts)
    # Only awarded when a meaningful portion of repos have substantial descriptions
    if total_orig > 0 and desc_ratio >= 0.5:
        score += 3.0
    elif total_orig > 0 and desc_ratio >= 0.25:
        score += 1.5
    # else 0 — no free points for bare repositories

    return min(score, 35.0), strengths, improvements, repo_audits


def score_activity_consistency(
    original_repos: List[Dict[str, Any]],
    profile: Dict[str, Any],
) -> Tuple[float, List[str], List[str]]:
    """
    Score commit recency, account maturity, and update patterns out of 25.
    """
    score = 0.0
    strengths = []
    improvements = []

    now = datetime.now(timezone.utc)

    # 1. Push recency across any original repository (up to 12 pts)
    most_recent_push = None
    for r in original_repos:
        pushed_str = r.get("pushed_at") or r.get("updated_at")
        if pushed_str:
            dt = _parse_iso_date(pushed_str)
            if most_recent_push is None or dt > most_recent_push:
                most_recent_push = dt

    if most_recent_push:
        days_since_push = max(0, (now - most_recent_push).days)
        if days_since_push <= 14:
            score += 12.0
            strengths.append("High recent activity: Active pushes detected within the last 14 days.")
        elif days_since_push <= 45:
            score += 9.0
            strengths.append(f"Recent coding activity: Pushed code {days_since_push} days ago.")
        elif days_since_push <= 90:
            score += 6.0
            improvements.append(f"Last commit was {days_since_push} days ago. Push code regularly to maintain green streak.")
        elif days_since_push <= 180:
            score += 3.0
            improvements.append(f"Inactivity warning: No code pushed in ~{days_since_push // 30} months. Resume active commits.")
        else:
            score += 1.0
            improvements.append("Critical Inactivity: No commits detected in over 6 months. Maintain active coding cadence.")
    else:
        improvements.append("No recent push dates found on public repositories.")

    # 2. Account Longevity & Maturity (up to 5 pts)
    created_str = profile.get("created_at")
    if created_str:
        created_dt = _parse_iso_date(created_str)
        account_days = (now - created_dt).days
        if account_days >= 730:
            score += 5.0
            strengths.append(f"Established developer profile ({account_days // 365}+ years on GitHub).")
        elif account_days >= 365:
            score += 4.0
            strengths.append(f"Active account history ({account_days // 365} year).")
        elif account_days >= 180:
            score += 3.0
        else:
            score += 2.0
            improvements.append("New account: Continue building and committing consistently to build track record.")

    # 3. Active Repo Breadth (up to 8 pts)
    recent_3m_repos = 0
    for r in original_repos:
        pushed_str = r.get("pushed_at")
        if pushed_str:
            dt = _parse_iso_date(pushed_str)
            if (now - dt).days <= 90:
                recent_3m_repos += 1

    if recent_3m_repos >= 4:
        score += 8.0
        strengths.append(f"Broad active development: {recent_3m_repos} distinct repositories updated in the last 90 days.")
    elif recent_3m_repos >= 2:
        score += 6.0
        strengths.append(f"{recent_3m_repos} repositories actively maintained in the last quarter.")
    elif recent_3m_repos >= 1:
        score += 4.0
        improvements.append("Iterate and update multiple repositories rather than abandoning past projects.")
    else:
        score += 1.0
        improvements.append("Update and refine your featured repositories to demonstrate ongoing maintenance.")

    return min(score, 25.0), strengths, improvements


def score_language_diversity(
    language_bytes: Dict[str, int],
    language_counts: Dict[str, int],
) -> Tuple[float, List[str], List[str]]:
    """
    Score language proficiency and polyglot balance out of 15.
    """
    score = 0.0
    strengths = []
    improvements = []

    total_bytes = sum(language_bytes.values())
    num_languages = len(language_bytes)

    if total_bytes == 0 or num_languages == 0:
        return 2.0, [], ["No language statistics detected. Publish code in recognized programming languages."]

    # Calculate primary language percentage
    sorted_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)
    top_lang, top_bytes = sorted_langs[0]
    top_share = top_bytes / total_bytes if total_bytes > 0 else 0

    # 1. Primary Depth (up to 8 pts)
    if top_share >= 0.40:
        score += 8.0
        strengths.append(f"Clear primary specialization in **{top_lang}** ({top_share*100:.1f}% of codebase).")
    elif top_share >= 0.25:
        score += 6.0
        strengths.append(f"Primary language focus in **{top_lang}** ({top_share*100:.1f}%).")
    else:
        score += 4.0
        improvements.append("Establish a stronger core specialization in one primary language (e.g. Python, Java, TypeScript).")

    # 2. Versatility & Full-Stack Diversity (up to 7 pts)
    # Meaningful languages (>3% share)
    significant_langs = [k for k, v in language_bytes.items() if (v / total_bytes) >= 0.03]
    count_sig = len(significant_langs)

    if 3 <= count_sig <= 6:
        score += 7.0
        lang_list = ", ".join(significant_langs[:4])
        strengths.append(f"Well-balanced full-stack polyglot proficiency across {count_sig} languages ({lang_list}).")
    elif count_sig >= 2:
        score += 5.0
        strengths.append(f"Multi-language proficiency across {count_sig} languages.")
    elif count_sig == 1:
        score += 3.0
        improvements.append("Broaden your tech stack with complementary skills (e.g. add backend API or database integration).")
    else:
        score += 3.0

    return min(score, 15.0), strengths, improvements


def score_community_impact(
    original_repos: List[Dict[str, Any]],
    profile: Dict[str, Any],
) -> Tuple[float, List[str], List[str]]:
    """
    Score community reception, stars, forks, and followers out of 10.
    """
    score = 0.0
    strengths = []
    improvements = []

    total_stars = sum(r.get("stargazers_count", 0) for r in original_repos)
    total_forks = sum(r.get("forks_count", 0) for r in original_repos)
    followers = profile.get("followers", 0)

    # Stars (up to 5 pts)
    if total_stars >= 50:
        score += 5.0
        strengths.append(f"High community validation: {total_stars} stars earned across repositories.")
    elif total_stars >= 15:
        score += 4.0
        strengths.append(f"Great project reception: {total_stars} stars earned on GitHub.")
    elif total_stars >= 3:
        score += 3.0
        strengths.append(f"{total_stars} stars collected across projects.")
    elif total_stars >= 1:
        score += 2.0
    else:
        improvements.append("Share your projects on LinkedIn, Dev.to, or Reddit to gain stars and early users.")

    # Forks / Collaboration (up to 3 pts)
    if total_forks >= 10:
        score += 3.0
        strengths.append(f"Projects have been forked {total_forks} times for reuse or contribution.")
    elif total_forks >= 2:
        score += 2.0
    elif total_forks >= 1:
        score += 1.0

    # Followers / Reach (up to 2 pts)
    if followers >= 25:
        score += 2.0
        strengths.append(f"Healthy developer following ({followers} followers).")
    elif followers >= 5:
        score += 1.0
    else:
        improvements.append("Engage in open-source discussions and follow peers to grow your developer network.")

    return min(score, 10.0), strengths, improvements


def audit_github_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full evaluation pipeline orchestrator.
    Consolidates dimension scores, flags, and generates a structured candidate readiness report.
    """
    profile = data.get("profile", {})
    original_repos = data.get("original_repos", [])
    forked_repos = data.get("forked_repos", [])
    language_bytes = data.get("language_bytes", {})
    language_counts = data.get("language_repo_counts", {})

    p_score, p_str, p_imp = score_profile_completeness(profile)
    r_score, r_str, r_imp, repo_audits = score_repo_quality(original_repos, forked_repos)
    a_score, a_str, a_imp = score_activity_consistency(original_repos, profile)
    l_score, l_str, l_imp = score_language_diversity(language_bytes, language_counts)
    c_score, c_str, c_imp = score_community_impact(original_repos, profile)

    total_score = round(p_score + r_score + a_score + l_score + c_score, 1)

    # Determine Grade and Color
    if total_score >= 85:
        grade = "⭐ Silicon Valley Ready"
        verdict = "Outstanding developer portfolio! Strong project hygiene, active commits, and great presentation."
        grade_color = "#22c55e"
    elif total_score >= 70:
        grade = "🚀 Strong Placement Candidate"
        verdict = "Solid foundation with good coding depth. A few documentation and demo tweaks will make it elite."
        grade_color = "#6366f1"
    elif total_score >= 50:
        grade = "⚡ Emerging Developer"
        verdict = "Promising projects in place, but lacks critical recruiter signals (descriptions, live demos, licenses)."
        grade_color = "#eab308"
    else:
        grade = "🛠️ Needs Polish & Structure"
        verdict = "Your GitHub needs significant hygiene improvements (bio, READMEs, descriptions, live links) to pass recruiter screenings."
        grade_color = "#ef4444"

    # Aggregate flags
    red_flags = []
    green_flags = []

    # Red flag detections
    if len(original_repos) < 2:
        red_flags.append("Fewer than 2 original public repositories visible.")
    if sum(1 for r in original_repos if r.get("homepage") and r["homepage"].strip().startswith("http")) == 0 and len(original_repos) > 0:
        red_flags.append("0 repositories have live deployment/demo links.")
    if sum(1 for r in original_repos if r.get("description")) == 0 and len(original_repos) > 0:
        red_flags.append("No repository descriptions set across your projects.")
    if (profile.get("bio") or "").strip() == "":
        red_flags.append("Profile bio is empty.")
    if (profile.get("blog") or "").strip() == "":
        red_flags.append("No LinkedIn or personal portfolio website linked.")

    # Green flag detections
    if a_score >= 18:
        green_flags.append("Consistent, recent coding activity on public repositories.")
    if r_score >= 25:
        green_flags.append("High project hygiene (descriptions, licenses, and topic tags).")
    if l_score >= 12:
        green_flags.append("Solid tech stack depth and specialized language focus.")
    if p_score >= 12:
        green_flags.append("Polished developer profile with full bio, links, and contact info.")

    # Generate Prioritized Action Checklist
    action_checklist = []
    if (profile.get("bio") or "").strip() == "":
        action_checklist.append({
            "task": "Write a 1-sentence bio with your target role and top skills",
            "impact": "High",
            "effort": "2 mins",
            "category": "Profile",
        })
    if (profile.get("blog") or "").strip() == "":
        action_checklist.append({
            "task": "Add your LinkedIn or Portfolio URL in the profile website field",
            "impact": "High",
            "effort": "1 min",
            "category": "Profile",
        })
    
    missing_desc_repos = [r["name"] for r in repo_audits if not r["has_description"]]
    if missing_desc_repos:
        action_checklist.append({
            "task": f"Add concise descriptions to: {', '.join(missing_desc_repos[:3])}",
            "impact": "High",
            "effort": "5 mins",
            "category": "Repositories",
        })

    missing_demo_repos = [r["name"] for r in repo_audits if not r["has_homepage"]]
    if missing_demo_repos:
        action_checklist.append({
            "task": f"Deploy a live demo (Vercel/Render/Pages) for: {missing_demo_repos[0]}",
            "impact": "High",
            "effort": "15 mins",
            "category": "Deployment",
        })

    missing_lic_repos = [r["name"] for r in repo_audits if not r["has_license"]]
    if missing_lic_repos:
        action_checklist.append({
            "task": f"Add an MIT License to: {', '.join(missing_lic_repos[:2])}",
            "impact": "Medium",
            "effort": "3 mins",
            "category": "Hygiene",
        })

    if not action_checklist:
        action_checklist.append({
            "task": "Pin your top 3-4 best projects to your GitHub profile overview",
            "impact": "Medium",
            "effort": "2 mins",
            "category": "Showcase",
        })
        action_checklist.append({
            "task": "Write comprehensive READMEs with architectural flowcharts and setup guides",
            "impact": "High",
            "effort": "30 mins",
            "category": "Documentation",
        })

    all_strengths = p_str + r_str + a_str + l_str + c_str
    all_improvements = p_imp + r_imp + a_imp + l_imp + c_imp

    return {
        "total_score": total_score,
        "grade": grade,
        "grade_color": grade_color,
        "verdict": verdict,
        "dimensions": {
            "profile_completeness": {
                "score": round(p_score, 1),
                "max": 15,
                "label": "Profile Completeness",
                "strengths": p_str,
                "improvements": p_imp,
            },
            "repo_quality": {
                "score": round(r_score, 1),
                "max": 35,
                "label": "Repo Quality & Hygiene",
                "strengths": r_str,
                "improvements": r_imp,
            },
            "activity_consistency": {
                "score": round(a_score, 1),
                "max": 25,
                "label": "Activity & Consistency",
                "strengths": a_str,
                "improvements": a_imp,
            },
            "language_diversity": {
                "score": round(l_score, 1),
                "max": 15,
                "label": "Language & Tech Stack",
                "strengths": l_str,
                "improvements": l_imp,
            },
            "community_impact": {
                "score": round(c_score, 1),
                "max": 10,
                "label": "Community & Impact",
                "strengths": c_str,
                "improvements": c_imp,
            },
        },
        "strengths": all_strengths,
        "improvements": all_improvements,
        "red_flags": red_flags,
        "green_flags": green_flags,
        "action_checklist": action_checklist,
        "repo_audits": repo_audits,
    }


def generate_markdown_report(
    profile_data: Dict[str, Any],
    audit_data: Dict[str, Any],
) -> str:
    """Generate a clean, exportable Markdown audit report."""
    profile = profile_data.get("profile", {})
    username = profile.get("login", "Candidate")
    name = profile.get("name") or username
    score = audit_data.get("total_score", 0)
    grade = audit_data.get("grade", "")

    lines = [
        f"# 🐙 DevPilot AI — GitHub Portfolio Audit Report",
        f"**Candidate:** {name} (`@{username}`)  ",
        f"**Audit Date:** {datetime.now().strftime('%B %d, %Y')}  ",
        f"**Developer Portfolio Score:** **{score}/100** — *{grade}*  ",
        "",
        "---",
        "",
        "## 📊 Dimension Breakdown",
        "| Dimension | Score | Max | Status |",
        "| :--- | :---: | :---: | :--- |",
    ]

    for key, dim in audit_data.get("dimensions", {}).items():
        pct = (dim["score"] / dim["max"]) * 100
        icon = "🟢" if pct >= 75 else "🟡" if pct >= 50 else "🔴"
        lines.append(f"| {dim['label']} | **{dim['score']}** | {dim['max']} | {icon} {pct:.0f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 🚩 Recruiter Diagnostic Flags",
    ])

    if audit_data.get("green_flags"):
        lines.append("### 🟢 Green Flags (Recruiter Favorites)")
        for gf in audit_data["green_flags"]:
            lines.append(f"- ✅ {gf}")
        lines.append("")

    if audit_data.get("red_flags"):
        lines.append("### 🔴 Red Flags (Immediate Fixes Recommended)")
        for rf in audit_data["red_flags"]:
            lines.append(f"- ⚠️ {rf}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 📋 Prioritized Action Plan",
    ])

    for i, item in enumerate(audit_data.get("action_checklist", []), 1):
        lines.append(f"{i}. **[{item['category']}]** {item['task']} *(Impact: {item['impact']} | Est. Time: {item['effort']})*")

    lines.extend([
        "",
        "---",
        "",
        "## 🛠️ Repository Audit Summary",
    ])

    for repo in audit_data.get("repo_audits", [])[:8]:
        desc = repo.get("description", "No description")
        h_score = repo.get("health_score", 0)
        demo_str = f"[Live Demo]({repo['homepage']})" if repo.get("has_homepage") else "No live demo"
        lic_str = "Licensed" if repo.get("has_license") else "No license"
        lines.append(f"- **[{repo['name']}]({repo['html_url']})** ({repo['language']}) — Health: `{h_score}/100`")
        lines.append(f"  - *{desc}*")
        lines.append(f"  - Status: {lic_str} | {demo_str} | ⭐ {repo['stars']} stars")

    lines.extend([
        "",
        "---",
        "*Generated by DevPilot AI — Engineering Placement Acceleration Dashboard*",
    ])

    return "\n".join(lines)
