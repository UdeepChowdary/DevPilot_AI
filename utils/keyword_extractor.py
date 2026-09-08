"""
Keyword Extractor — extracts and compares keywords using RAKE + spaCy + comprehensive tech taxonomy.
No model training required. Fully offline with smart token preservation.
"""

import re
import nltk
from rake_nltk import Rake

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Try loading spaCy model; fall back gracefully if not installed
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    _nlp = None

# Whitelist of valid 1-2 character tech skills and abbreviations
SHORT_TECH_WHITELIST = {
    "c", "r", "go", "ai", "ml", "ci", "cd", "ui", "ux", "qa", "db", "os", "js", "ts",
    "c++", "c#", ".net", "git", "sql", "aws", "gcp", "npm", "pip", "k8s", "iam",
}

# Comprehensive software engineering tech taxonomy
TECH_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "dart", "html", "html5", "css", "css3", "sass", "sql",

    # Frontend Frameworks & Libraries
    "react", "react.js", "react native", "next.js", "vue", "vue.js", "nuxt.js", "angular", "svelte", "sveltekit",
    "tailwind", "tailwind css", "bootstrap", "material-ui", "shadcn", "redux", "zustand", "mobx",
    "webpack", "vite", "babel",

    # Backend & Frameworks
    "node.js", "express", "express.js", "nestjs", "django", "flask", "fastapi", "spring", "spring boot",
    ".net", "asp.net", "ruby on rails", "laravel", "gin", "fiber", "actix", "graphql", "rest", "restful api",
    "grpc", "websocket", "microservices", "serverless",

    # Databases & Caching
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "dynamodb", "cassandra", "supabase", "firebase", "firestore", "prisma", "drizzle", "sqlalchemy",

    # DevOps, Cloud & Infrastructure
    "aws", "amazon web services", "gcp", "google cloud", "azure", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "ci/cd", "continuous integration", "github actions", "gitlab ci", "jenkins",
    "linux", "bash", "shell scripting", "nginx", "apache", "prometheus", "grafana", "datadog",

    # Data Science & AI / ML
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
    "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "opencv", "hugging face", "transformers", "llm", "large language models", "rag", "langchain", "llamaindex",
    "spark", "apache spark", "hadoop", "kafka", "apache kafka", "airflow",

    # Methodologies & Tools
    "git", "github", "gitlab", "jira", "confluence", "agile", "scrum", "kanban", "tdd", "unit testing",
    "jest", "pytest", "cypress", "playwright", "figma", "postman", "system design", "data structures",
    "algorithms", "object-oriented programming", "oop", "clean architecture",
}

# Precompile all skill patterns at module load time for O(1) lookup per call
_SKILL_PATTERNS: list[tuple[str, re.Pattern]] = []
for _skill in TECH_SKILLS:
    if " " in _skill or "." in _skill or "+" in _skill or "#" in _skill:
        _SKILL_PATTERNS.append(
            (_skill, re.compile(
                rf"(?:^|[\s,;/\(\)\[\]]){re.escape(_skill)}(?:$|[\s,;/\(\)\[\]])",
                re.IGNORECASE,
            ))
        )
    else:
        _SKILL_PATTERNS.append(
            (_skill, re.compile(rf"\b{re.escape(_skill)}\b", re.IGNORECASE))
        )

def _clean_token(term: str) -> str:
    """Normalize term for comparison."""
    return term.strip().lower()


def _rake_keywords(text: str, max_keywords: int = 25) -> list[str]:
    """Extract top phrases using RAKE algorithm (thread-safe, local instance)."""
    rake = Rake(min_length=1, max_length=3)
    rake.extract_keywords_from_text(text)
    ranked = rake.get_ranked_phrases()
    cleaned = []
    for phrase in ranked:
        norm = _clean_token(phrase)
        if norm.isdigit():
            continue
        if norm in SHORT_TECH_WHITELIST or len(norm) > 2:
            cleaned.append(norm)
        if len(cleaned) >= max_keywords:
            break
    return cleaned


def _spacy_entities(text: str) -> list[str]:
    """Extract named entities and noun chunks using spaCy (if available)."""
    if not SPACY_AVAILABLE or _nlp is None:
        return []
    doc = _nlp(text[:50000])  # limit for performance
    entities = [ent.text.lower().strip() for ent in doc.ents
                if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART", "GPE", "LANGUAGE", "LAW")]
    noun_chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks
                   if 1 <= len(chunk.text.split()) <= 3]
    return list(set(entities + noun_chunks))


def _tech_skills_in_text(text: str) -> list[str]:
    """
    Find known tech skills mentioned in the text using precompiled patterns.
    O(n) where n = number of skills — patterns are compiled at module load time.
    """
    found = []
    for skill, pattern in _SKILL_PATTERNS:
        if pattern.search(text):
            found.append(skill)
    return found


def extract_keywords(text: str, max_keywords: int = 35) -> list[str]:
    """
    Extract top keywords from a block of text.
    Combines known tech skills + RAKE phrases + spaCy entities.
    Returns a deduplicated list.
    """
    tech_kws  = _tech_skills_in_text(text)
    rake_kws  = _rake_keywords(text, max_keywords)
    spacy_kws = _spacy_entities(text)

    # Tech skills take highest priority, then RAKE, then spaCy
    combined = []
    seen = set()
    for kw in tech_kws + rake_kws + spacy_kws:
        norm = _clean_token(kw)
        if not norm or norm in seen or norm.isdigit():
            continue
        if len(norm) > 2 or norm in SHORT_TECH_WHITELIST:
            seen.add(norm)
            combined.append(norm)

    return sorted(combined[:max_keywords])


def compare_keywords(resume_text: str, jd_text: str) -> dict:
    """
    Compare resume keywords against a job description.

    Returns:
        {
            "matched": [str],
            "missing": [str],
            "resume_only": [str],
            "jd_keywords": [str],
            "resume_keywords": [str],
            "match_rate": float (0.0 - 1.0)
        }
    """
    resume_kws = set(extract_keywords(resume_text, 50))
    jd_kws     = set(extract_keywords(jd_text, 50))
    resume_lower = resume_text.lower()

    matched = []
    missing = []

    def _matches_in_text(term: str, target: str) -> bool:
        if " " in term:
            return term in target
        if re.search(r"[\+\#\.]", term):
            return bool(re.search(rf"(?:^|[\s,;/\(\)\[\]]){re.escape(term)}(?:$|[\s,;/\(\)\[\]])", target))
        return bool(re.search(rf"\b{re.escape(term)}\b", target))

    for kw in jd_kws:
        if kw in resume_kws or _matches_in_text(kw, resume_lower):
            matched.append(kw)
        else:
            missing.append(kw)

    matched = sorted(list(set(matched)))
    missing = sorted(list(set(missing)))
    # resume_only = keywords in resume but not matched with JD
    resume_only = sorted(list(resume_kws - set(matched) - set(missing)))

    total_jd = max(len(jd_kws), 1)
    match_rate = round(len(matched) / total_jd, 2)

    return {
        "matched": matched,
        "missing": missing,
        "resume_only": resume_only,
        "jd_keywords": sorted(list(jd_kws)),
        "resume_keywords": sorted(list(resume_kws)),
        "match_rate": match_rate,
    }
