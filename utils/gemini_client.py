import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None


def _get_model():
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-1.5-flash")
    return _model


def ask(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    model = _get_model()
    response = model.generate_content(prompt)
    return response.text


def ask_json(prompt: str) -> dict | list:
    """
    Send a prompt expecting a JSON response.
    Strips markdown fences if present and parses to Python object.
    """
    raw = ask(prompt)
    # Strip ```json ... ``` or ``` ... ``` fences
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Remove first and last fence lines
        cleaned = "\n".join(lines[1:-1]).strip()
    return json.loads(cleaned)
