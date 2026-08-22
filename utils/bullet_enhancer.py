"""
Bullet Enhancer — rewrites weak resume bullets using:
1. Smart Rule-Based Engine (instant, zero-dependency)
2. Gemini AI Engine (high-precision Google XYZ formula rewrites)
3. Local HuggingFace T5 (offline neural fallback)
"""

import re
import os
import json

# ─── Verb substitution table ──────────────────────────────────────────────────
VERB_SUBSTITUTIONS = {
    "was responsible for": "Owned",
    "responsible for":     "Spearheaded",
    "worked on developing":"Developed",
    "worked on building":  "Engineered",
    "worked on":           "Engineered",
    "worked with":         "Partnered with",
    "worked":              "Contributed",
    "helped to build":     "Constructed",
    "helped build":        "Engineered",
    "helped to create":    "Developed",
    "helped":              "Spearheaded",
    "assisted with":       "Collaborated on",
    "assisted in":         "Co-developed",
    "assisted":            "Coordinated",
    "did the":             "Executed the",
    "did":                 "Executed",
    "made":                "Produced",
    "got":                 "Secured",
    "had":                 "Maintained",
    "tried":               "Piloted",
    "supported":           "Enabled",
    "participated in":     "Contributed to",
    "participated":        "Contributed to",
    "involved in":         "Drove",
    "was part of":         "Contributed to",
    "used":                "Leveraged",
    "handled":             "Managed",
    "fixed":               "Resolved",
    "wrote":               "Authored",
    "built":               "Engineered",
    "created":             "Architected",
    "updated":             "Modernized",
    "improved":            "Optimized",
    "tested":              "Validated",
    "set up":              "Configured",
    "looked after":        "Maintained",
}

WEAK_VERB_RE = re.compile(
    r"^(" + "|".join(re.escape(v) for v in sorted(VERB_SUBSTITUTIONS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def _has_metric(text: str) -> bool:
    """Check if a bullet contains a measurable metric (%, ms, $, scale, multiplier, numbers)."""
    patterns = [
        r"\$\s*\d+",                                             # $100, $50k
        r"\b\d+[\.,]?\d*\s*%",                                   # 45%, 30.5 %
        r"\b\d+[\.,]?\d*\s*[xX]\b",                              # 3x, 2X
        r"\b\d+[\.,]?\d*\s*(?:k|m|million|billion)\b",           # 10k, 5M, 2 million
        r"\b\d+\s*\+",                                           # 100+, 5k+
        r"\b\d+[\.,]?\d*\s*(?:ms|sec|seconds|minutes|hours|days|fps|qps|rps)\b", # 500ms, 2 seconds
        r"\b\d+[\.,]?\d*\s*(?:users|clients|customers|requests|events|queries|tickets|nodes|services|endpoints|repos)\b", # 10k users
        r"(?:reduced|increased|boosted|improved|saved|scaled|decreased|cut)\s+(?:by|to)?\s*\d+", # reduced by 40
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _rule_based_enhance(bullet: str) -> tuple[str, str]:
    """
    Apply rule-based improvements to a single bullet point.
    Returns (enhanced_text, explanation).
    """
    bullet = bullet.strip()
    enhanced = bullet
    action_changed = False
    weak_found = ""
    strong_applied = ""

    # Replace weak verb at the start
    match = WEAK_VERB_RE.match(bullet)
    if match:
        weak = match.group(1)
        strong = VERB_SUBSTITUTIONS.get(weak.lower(), "Spearheaded")
        # Ensure capitalization and splice cleanly
        suffix = bullet[len(weak):]
        # Clean potential grammatical leftover: "to build" -> "building" or strip "to"
        if suffix.startswith(" to "):
            suffix = suffix[4:]
        enhanced = strong + suffix
        action_changed = True
        weak_found = weak
        strong_applied = strong

    # Ensure first word is capitalized
    if enhanced and not enhanced[0].isupper():
        enhanced = enhanced[0].upper() + enhanced[1:]

    # Remove trailing period inconsistencies
    if not enhanced.endswith("."):
        enhanced = enhanced + "."

    if action_changed:
        explanation = f"Upgraded action verb ('{weak_found}' -> '{strong_applied}')"
    else:
        explanation = "Action verb preserved"

    return enhanced, explanation


# ─── Gemini AI Enhancement ───────────────────────────────────────────────────

def _gemini_enhance_batch(bullets: list[str]) -> dict[str, str]:
    """
    Batch enhance bullets using Gemini AI adhering to Google's XYZ formula:
    'Accomplished [X] as measured by [Y], by doing [Z]'
    """
    try:
        from utils.gemini_client import ask_json
        prompt = f"""
You are an elite Silicon Valley Tech Recruiter and Resume Writer.
Rewrite the following resume bullet points to make them high-impact, professional, and accomplishment-oriented following Google's XYZ formula ('Accomplished [X] as measured by [Y], by doing [Z]').

Input Bullets:
{json.dumps(bullets, indent=2)}

Return a valid JSON object mapping each EXACT original bullet string to its enhanced professional rewrite.
Example format:
{{
  "original bullet 1": "Enhanced high-impact bullet 1",
  "original bullet 2": "Enhanced high-impact bullet 2"
}}
Return ONLY JSON without markdown formatting or code fences.
"""
        result = ask_json(prompt)
        if isinstance(result, dict):
            return result
        return {}
    except Exception:
        return {}


# ─── T5 Local Model (Lazy Loaded) ─────────────────────────────────────────────

_t5_pipeline = None


def _get_t5_pipeline():
    """Lazy-load T5 text2text pipeline."""
    global _t5_pipeline
    if _t5_pipeline is None:
        from transformers import pipeline
        _t5_pipeline = pipeline(
            "text2text-generation",
            model="t5-small",
            max_length=128,
            do_sample=False,
        )
    return _t5_pipeline


def _t5_enhance(bullet: str) -> str:
    """Offline neural rewrite fallback."""
    prompt = f"summarize and professionalize: {bullet}"
    try:
        pipe = _get_t5_pipeline()
        result = pipe(prompt, max_length=100, num_beams=3, early_stopping=True)
        return result[0]["generated_text"].strip()
    except Exception:
        return bullet


# ─── Public API ───────────────────────────────────────────────────────────────

def enhance_bullets(
    bullets: list[str],
    mode: str = "rule_based",  # "rule_based", "gemini", or "t5"
) -> list[dict]:
    """
    Enhance a list of resume bullet points.

    Args:
        bullets: List of raw bullet point strings.
        mode: "rule_based", "gemini", or "t5".

    Returns:
        List of dicts with original, enhanced, ai_suggestion, has_metric, and explanation.
    """
    results = []
    gemini_map = {}

    if mode == "gemini":
        gemini_map = _gemini_enhance_batch([b for b in bullets if b.strip()])

    for bullet in bullets:
        if not bullet.strip():
            continue

        rule_enhanced, explanation = _rule_based_enhance(bullet)
        ai_suggestion = None

        if mode == "gemini" and bullet in gemini_map:
            ai_suggestion = gemini_map[bullet]
        elif mode == "t5":
            t5_res = _t5_enhance(bullet)
            if t5_res.lower().strip() != bullet.lower().strip():
                ai_suggestion = t5_res

        best_output = ai_suggestion or rule_enhanced

        results.append({
            "original":      bullet,
            "enhanced":      best_output,
            "rule_enhanced": rule_enhanced,
            "ai_suggestion": ai_suggestion,
            "has_metric":    _has_metric(bullet),
            "explanation":   explanation,
            "mode_used":     mode if ai_suggestion else "rule_based",
        })

    return results
