import os
import json
import logging
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_cached_client = None
_cached_key = None


def _get_client(api_key: Optional[str] = None):
    """
    Return a cached genai.Client.
    Uses google-genai (new SDK) first, falls back to legacy google-generativeai if unavailable.
    """
    global _cached_client, _cached_key
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or not key.strip():
        raise ValueError("GEMINI_API_KEY not found. Please provide a valid Gemini API key.")

    clean_key = key.strip()
    if _cached_client is not None and _cached_key == clean_key:
        return _cached_client

    try:
        # New SDK: google-genai
        from google import genai
        client = genai.Client(api_key=clean_key)
        _cached_client = ("new", client)
    except ImportError:
        # Legacy SDK: google-generativeai
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=clean_key)
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")
        _cached_client = ("legacy", model)

    _cached_key = clean_key
    return _cached_client


def ask(prompt: str, api_key: Optional[str] = None) -> Optional[str]:
    """
    Send a prompt to Gemini and return the text response.
    Returns None on any API error (except missing key) so callers can degrade gracefully.
    """
    try:
        sdk_type, client = _get_client(api_key)

        if sdk_type == "new":
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            text = response.text
        else:
            # Legacy fallback
            response = client.generate_content(prompt)
            text = response.text

        if not text:
            logger.warning("Gemini returned an empty or blocked response.")
            return None
        return text

    except ValueError:
        raise
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return None


def ask_json(prompt: str, api_key: Optional[str] = None) -> Any:
    """
    Send a prompt expecting a JSON response.
    Robustly strips markdown code fences (```json ... ``` or ``` ... ```) before parsing.
    Returns None if the response is empty or cannot be parsed.
    """
    raw = ask(prompt, api_key=api_key)
    if not raw:
        return None

    cleaned = raw.strip()

    # Strip leading code fence line (```json or ```) and trailing ```
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        inner_lines = lines[1:]
        if inner_lines and inner_lines[-1].strip() == "```":
            inner_lines = inner_lines[:-1]
        cleaned = "\n".join(inner_lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gemini JSON response: %s\nRaw: %s", e, cleaned[:500])
        return None
