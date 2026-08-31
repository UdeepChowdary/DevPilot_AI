"""
ATS Scorer — scores a resume using TF-IDF, cosine similarity, action verbs, quantification, and heuristics.
No model training required. Fully offline with sklearn + NLTK.
"""

import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data on first use (silent)
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

from nltk.corpus import stopwords
from utils.constants import ACTION_VERBS, WEAK_VERBS

STOPWORDS = set(stopwords.words("english"))

EXPECTED_SECTIONS = {"experience", "education", "skills", "projects"}
KNOWN_HEADERS = {
    "EXPERIENCE", "EDUCATION", "SKILLS", "PROJECTS", "CERTIFICATIONS",
    "SUMMARY", "OBJECTIVE", "TECHNICAL SKILLS", "WORK EXPERIENCE",
    "PROFESSIONAL EXPERIENCE", "ACADEMIC BACKGROUND", "ACHIEVEMENTS",
    "PUBLICATIONS", "LEADERSHIP", "EXTRACURRICULAR", "AWARDS",
}

# Precompiled quantification patterns — each pattern is distinct to avoid double-counting.
# Order matters: more specific patterns are listed first.
_QUANT_PATTERNS = [
    re.compile(r"\$\s*\d+[\.,]?\d*", re.IGNORECASE),                                          # $100, $50k
    re.compile(r"\b\d+[\.,]?\d*\s*%", re.IGNORECASE),                                         # 45%, 30.5%
    re.compile(r"\b\d+[\.,]?\d*\s*[xX]\b", re.IGNORECASE),                                    # 3x, 2X
    re.compile(r"\b\d+[\.,]?\d*\s*(?:k|m|million|billion)\b", re.IGNORECASE),                  # 10k, 5M
    re.compile(r"\b\d+\s*\+(?!\d)", re.IGNORECASE),                                           # 100+  (not 100+200)
    re.compile(                                                                                 # 500ms, 2 seconds
        r"\b\d+[\.,]?\d*\s*(?:ms|s|sec|seconds|minutes|hours|days|fps|qps|rps)\b",
        re.IGNORECASE,
    ),
    re.compile(                                                                                 # 10k users
        r"\b\d+[\.,]?\d*\s*(?:users|clients|customers|requests|events|queries|tickets|nodes|services|endpoints|repos)\b",
        re.IGNORECASE,
    ),
    # NOTE: kept separate to avoid double-counting with % pattern above
    re.compile(
        r"(?:reduced|increased|boosted|improved|saved|scaled|decreased|cut)\s+(?:by|to)?\s*\d+(?!\s*%)",
        re.IGNORECASE,
    ),
]

# Phone regex — requires 10+ consecutive digit characters to avoid matching GPA, years, etc.
_PHONE_RE = re.compile(r"\+?[\d][\d\s\-\(\)\.]{9,}\d")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def _count_quantifications(text: str) -> int:
    """
    Count distinct occurrences of meaningful quantified metrics.
    Uses non-overlapping matches and deduplicates by span to avoid double-counting
    bullets that match multiple patterns (e.g. 'reduced by 45%').
    """
    matched_spans: set[tuple[int, int]] = set()
    for pattern in _QUANT_PATTERNS:
        for m in pattern.finditer(text):
            span = (m.start(), m.end())
            # Only count if this span doesn't significantly overlap an already-counted one
            overlaps = any(
                abs(span[0] - s[0]) < 5  # within 5 chars = same metric
                for s in matched_spans
            )
            if not overlaps:
                matched_spans.add(span)
    return len(matched_spans)


def _count_action_verbs(text: str) -> int:
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    return len(tokens & ACTION_VERBS)


def _count_weak_verbs(text: str) -> int:
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    return len(tokens & WEAK_VERBS)


def _word_count(text: str) -> int:
    return len(text.split())


# ─── Scoring Components ───────────────────────────────────────────────────────

def _score_keyword_match(resume_text: str, jd_text: str | None) -> dict:
    """
    TF-IDF cosine similarity between resume and job description.
    If no JD provided, estimates keyword density and vocabulary breadth (Max 30 pts).
    """
    if jd_text and len(jd_text.strip()) > 50:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Similarity of 0.25+ is considered a strong match in TF-IDF
            score = round(min(similarity * 100 * 2.0, 30))
        except Exception:
            score = 18
        return {"score": score, "max": 30, "label": "Keyword Alignment (vs JD)"}
    else:
        # Without JD: score based on tech & vocabulary richness scaled to 30.
        # Normalize by word count bracket to avoid penalizing short but dense resumes.
        tokens = _tokenize(resume_text)
        wc = max(len(tokens), 1)
        unique_ratio = len(set(tokens)) / wc
        # Target ratio: 0.4–0.6 for a well-written tech resume
        normalized = min(unique_ratio / 0.45, 1.0)
        score = round(max(normalized * 25, 10))
        score = min(score, 30)
        return {"score": score, "max": 30, "label": "Keyword & Vocabulary Richness"}


def _score_impact(resume_text: str) -> dict:
    """Score based on action verbs and quantified achievements (Max 25 pts)."""
    action_count = _count_action_verbs(resume_text)
    quant_count = _count_quantifications(resume_text)
    weak_count = _count_weak_verbs(resume_text)

    # Action verbs: up to 15 points (target: 8+ verbs)
    action_score = min(action_count / 8, 1.0) * 15
    # Quantification: up to 10 points (target: 4+ metrics)
    quant_score = min(quant_count / 4, 1.0) * 10
    # Penalty for weak verbs (up to 5 pts)
    weak_penalty = min(weak_count * 1.0, 5)

    score = round(max(action_score + quant_score - weak_penalty, 0))
    score = min(score, 25)
    return {
        "score": score,
        "max": 25,
        "label": "Impact & Action Verbs",
        "action_verbs": action_count,
        "quantifications": quant_count,
        "weak_verbs": weak_count,
    }


def _score_sections(detected_sections: set[str]) -> dict:
    """Score based on presence of key expected resume sections (Max 20 pts)."""
    found = EXPECTED_SECTIONS & detected_sections
    score = round((len(found) / len(EXPECTED_SECTIONS)) * 20)
    return {
        "score": score,
        "max": 20,
        "label": "Section Completeness",
        "found": list(found),
        "missing": list(EXPECTED_SECTIONS - found),
    }


def _score_length(text: str) -> dict:
    """Score based on resume length for 1-2 pages (Max 15 pts)."""
    wc = _word_count(text)
    if 350 <= wc <= 850:
        score = 15
    elif 250 <= wc < 350 or 850 < wc <= 1100:
        score = 10
    elif 150 <= wc < 250 or 1100 < wc <= 1400:
        score = 6
    else:
        score = 3
    return {"score": score, "max": 15, "label": "Length & Conciseness", "word_count": wc}


def _score_formatting(text: str) -> dict:
    """Score formatting quality heuristics (Max 10 pts)."""
    score = 0
    # Bullet points present (3 pts)
    if re.search(r"[•\-\*\u2022\u25cf\u25e6\u25aa\u25ab\u2192]", text):
        score += 3

    # Contact info: email (2 pts) and phone / LinkedIn (2 pts)
    if re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", text):
        score += 2

    # Phone: require 10+ consecutive digit characters (avoids GPA/year false positives)
    if _PHONE_RE.search(text) or "linkedin.com" in text.lower():
        score += 2

    # ALL CAPS check: ignore recognized standard headers (3 pts)
    excessive_caps = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.isupper() and len(stripped) > 5:
            clean = re.sub(r"[^A-Z\s]", "", stripped).strip()
            if clean not in KNOWN_HEADERS:
                excessive_caps += 1

    if excessive_caps <= 3:
        score += 3

    return {"score": min(score, 10), "max": 10, "label": "Formatting & Contact Info"}


# ─── Main Public Function ─────────────────────────────────────────────────────

def score_resume(resume_text: str, jd_text: str | None, detected_sections: dict) -> dict:
    """
    Run all scoring components and return a structured ATS result normalized to 100.
    """
    section_keys = set(detected_sections.keys())

    kw   = _score_keyword_match(resume_text, jd_text)
    imp  = _score_impact(resume_text)
    sec  = _score_sections(section_keys)
    leng = _score_length(resume_text)
    fmt  = _score_formatting(resume_text)

    total = kw["score"] + imp["score"] + sec["score"] + leng["score"] + fmt["score"]
    total = min(max(total, 0), 100)

    # Human-readable strengths & weaknesses
    strengths, weaknesses = [], []

    # Action verbs
    if imp["action_verbs"] >= 6:
        strengths.append(f"Strong use of {imp['action_verbs']} action verbs (Built, Optimized, Spearheaded, etc.)")
    else:
        weaknesses.append("Too few action verbs — begin bullets with strong verbs like Engineered, Spearheaded, Accelerated")

    # Quantifications
    if imp["quantifications"] >= 3:
        strengths.append(f"{imp['quantifications']} quantified achievements detected (%, $, scale, metrics)")
    else:
        weaknesses.append("Add measurable metrics to your bullets (e.g. reduced latency by 35%, scaled to 10k users)")

    # Weak verbs
    if imp["weak_verbs"] > 0:
        weaknesses.append(f"Found {imp['weak_verbs']} passive/weak verbs (helped, assisted, worked on) — replace with direct impact words")

    # Sections
    if sec["missing"]:
        weaknesses.append(f"Missing core sections: {', '.join(sec['missing']).title()}")
    else:
        strengths.append("All key sections present (Experience, Education, Skills, Projects)")

    # Length
    wc = leng["word_count"]
    if 350 <= wc <= 850:
        strengths.append(f"Ideal resume length ({wc} words)")
    elif wc < 350:
        weaknesses.append(f"Resume is on the shorter side ({wc} words) — elaborate on project impacts and technical stack")
    else:
        weaknesses.append(f"Resume is long ({wc} words) — aim for a concise 1-page format (under 850 words)")

    # Job description alignment
    if jd_text and len(jd_text.strip()) > 50:
        if kw["score"] >= 20:
            strengths.append("High keyword alignment with target Job Description")
        else:
            weaknesses.append("Moderate keyword alignment — mirror key tools and technologies mentioned in the JD")

    return {
        "total": total,
        "breakdown": [kw, imp, sec, leng, fmt],
        "strengths": strengths,
        "weaknesses": weaknesses,
    }
