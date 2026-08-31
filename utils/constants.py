"""
Shared constants for DevPilot AI — single source of truth for verb sets and other shared data.
Importing from here prevents DRY violations across ats_scorer.py and resume_parser.py.
"""

# Strong action verbs (both past and present tense) associated with high-impact bullets
ACTION_VERBS = {
    # Past Tense
    "achieved", "accelerated", "architected", "automated", "built", "championed", "constructed",
    "created", "decreased", "delivered", "deployed", "designed", "developed", "directed",
    "drove", "enhanced", "engineered", "established", "executed", "formulated", "generated",
    "grew", "implemented", "improved", "increased", "initiated", "integrated", "launched",
    "led", "managed", "mentored", "migrated", "modernized", "optimized", "orchestrated",
    "oversaw", "pioneered", "produced", "programmed", "reduced", "refactored", "resolved",
    "revamped", "scaled", "spearheaded", "standardized", "streamlined", "transformed",
    "authored", "facilitated", "piloted", "conducted", "collaborated",

    # Present Tense (for current roles)
    "achieve", "accelerate", "architect", "automate", "build", "champion", "construct",
    "create", "decrease", "deliver", "deploy", "design", "develop", "direct",
    "drive", "enhance", "engineer", "establish", "execute", "formulate", "generate",
    "grow", "implement", "improve", "increase", "initiate", "integrate", "launch",
    "lead", "manage", "mentor", "migrate", "modernize", "optimize", "orchestrate",
    "oversee", "pioneer", "produce", "program", "reduce", "refactor", "resolve",
    "scale", "spearhead", "streamline", "transform",
}

WEAK_VERBS = {
    "helped", "assisted", "worked", "participated", "was", "did", "made",
    "got", "had", "went", "used", "tried", "supported", "involved", "responsible",
}
