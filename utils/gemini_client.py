import os
import json
from typing import Optional, Any, Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_cached_model = None
_cached_key = None


def _get_model(api_key: Optional[str] = None):
    global _cached_model, _cached_key
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or not key.strip():
        raise ValueError("GEMINI_API_KEY not found. Please provide a valid Gemini API key.")
    
    clean_key = key.strip()
    if _cached_model is None or _cached_key != clean_key:
        genai.configure(api_key=clean_key)
        # Prefer gemini-1.5-flash as default lightweight model
        _cached_model = genai.GenerativeModel("gemini-1.5-flash")
        _cached_key = clean_key
    return _cached_model


def ask(prompt: str, api_key: Optional[str] = None) -> str:
    """Send a prompt to Gemini and return the text response."""
    model = _get_model(api_key)
    response = model.generate_content(prompt)
    return response.text


def ask_json(prompt: str, api_key: Optional[str] = None) -> Any:
    """
    Send a prompt expecting a JSON response.
    Strips markdown fences if present and parses to Python object.
    """
    raw = ask(prompt, api_key=api_key)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Remove opening ```json / ``` and closing ```
        if len(lines) >= 2:
            cleaned = "\n".join(lines[1:-1]).strip()
    return json.loads(cleaned)
