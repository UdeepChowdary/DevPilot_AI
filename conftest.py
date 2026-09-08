"""
conftest.py — Shared pytest fixtures for DevPilot AI tests.
All fixtures are available to every test module without explicit imports.
"""

import pytest


# ─── Resume Fixtures ──────────────────────────────────────────────────────────

SAMPLE_RESUME_TEXT = """
John Doe
john.doe@email.com | +1-555-123-4567 | linkedin.com/in/johndoe

EXPERIENCE
Software Engineer Intern — Acme Corp (Jan 2023 – Jun 2023)
• Engineered a REST API with FastAPI, reducing response latency by 35%.
• Automated CI/CD pipelines using GitHub Actions, saving 4 hours/week of manual deployments.
• Optimized PostgreSQL queries improving throughput by 2x for 10k+ daily users.

PROJECTS
DevPilot AI — Python, Streamlit, NLP
• Built an ML-powered resume analyzer supporting 200+ tech skill keywords.
• Deployed on Streamlit Cloud achieving 500+ active users within 2 weeks.

EDUCATION
B.Tech Computer Science — IIT Delhi (2020 – 2024)
GPA: 8.9/10

SKILLS
Languages: Python, JavaScript, Go, SQL
Frameworks: FastAPI, React, Streamlit
Tools: Docker, GitHub Actions, PostgreSQL, Redis
"""

SAMPLE_RESUME_SHORT = """
Jane Smith
jane@email.com

EXPERIENCE
Worked on web apps.
Used React.

SKILLS
Python
"""

SAMPLE_RESUME_NO_JD_RICH = """
Alice Johnson
alice@company.com | linkedin.com/in/alice

EXPERIENCE
Senior Engineer — TechCorp (2021 – 2023)
• Architected microservices reducing system latency by 40%.
• Led migration from monolith to Kubernetes, scaling to 50k concurrent users.
• Spearheaded adoption of distributed tracing, improving MTTR by 60%.

PROJECTS
CloudOrchestrator
• Engineered an event-driven pipeline processing 1M+ daily events on AWS Lambda.

EDUCATION
B.S. Computer Science — MIT (2017–2021)

SKILLS
Python, Go, Kubernetes, AWS, Terraform, Prometheus, Grafana
"""


@pytest.fixture
def sample_resume_text():
    """A well-formed resume with action verbs, metrics, and all sections."""
    return SAMPLE_RESUME_TEXT


@pytest.fixture
def sample_resume_short():
    """A very short/weak resume."""
    return SAMPLE_RESUME_SHORT


@pytest.fixture
def sample_resume_sections():
    """Pre-detected sections dict matching SAMPLE_RESUME_TEXT."""
    return {
        "experience": "Engineered a REST API with FastAPI...",
        "projects": "DevPilot AI — Python, Streamlit...",
        "education": "B.Tech Computer Science — IIT Delhi",
        "skills": "Languages: Python, JavaScript...",
    }


# ─── GitHub Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def full_github_profile():
    """A fully populated GitHub profile dict."""
    return {
        "login": "devuser",
        "name": "Dev User",
        "bio": "Full-stack engineer specializing in Python and React.",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4",
        "blog": "https://devuser.dev",
        "location": "Bangalore, India",
        "company": "IIT Delhi",
        "public_repos": 10,
        "followers": 25,
        "following": 30,
    }


@pytest.fixture
def empty_github_profile():
    """A bare-minimum GitHub profile with no optional fields."""
    return {
        "login": "ghost",
        "name": None,
        "bio": None,
        "avatar_url": "https://www.gravatar.com/avatar/?d=identicon",
        "blog": None,
        "location": None,
        "company": None,
        "public_repos": 0,
        "followers": 0,
        "following": 0,
    }


def _make_repo(name, description=None, language="Python", stars=0,
               forks=0, homepage=None, license_key=None, topics=None,
               pushed_at="2024-01-15T10:00:00Z"):
    return {
        "name": name,
        "description": description,
        "language": language,
        "stargazers_count": stars,
        "forks_count": forks,
        "homepage": homepage,
        "license": {"key": license_key} if license_key else None,
        "topics": topics or [],
        "fork": False,
        "pushed_at": pushed_at,
        "created_at": "2023-01-01T00:00:00Z",
    }


@pytest.fixture
def strong_repos():
    """A list of high-quality repos that should score well."""
    return [
        _make_repo("ProjectA", "A REST API for task management",
                   stars=10, homepage="https://projecta.vercel.app",
                   license_key="mit", topics=["python", "fastapi", "rest-api"]),
        _make_repo("ProjectB", "ML-powered resume analyzer",
                   language="Python", stars=5,
                   homepage="https://projectb.streamlit.app",
                   license_key="mit", topics=["machine-learning", "nlp"]),
        _make_repo("ProjectC", "React dashboard for data viz",
                   language="JavaScript", stars=3,
                   homepage="https://projectc.netlify.app",
                   license_key="apache-2.0", topics=["react", "dashboard"]),
    ]


@pytest.fixture
def weak_repos():
    """Repos with no descriptions, licenses, demos, or topics."""
    return [
        _make_repo("repo1"),
        _make_repo("repo2"),
        _make_repo("repo3"),
    ]
