import os
import re
import json
import logging
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def _get_client(api_key: Optional[str] = None):
    """
    Return a thread-isolated genai.Client instance.
    Uses google-genai (new SDK) first, falls back to legacy google-generativeai if unavailable.
    """
    key = (api_key or "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise ValueError("GEMINI_API_KEY not found. Please provide a valid Gemini API key.")

    try:
        # New SDK: google-genai
        from google import genai
        client = genai.Client(api_key=key)
        return ("new", client)
    except ImportError:
        # Legacy SDK: google-generativeai
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=key)
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")
        return ("legacy", model)


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
    Robustly extracts JSON from markdown code fences or raw object/array strings.
    Returns None if the response is empty or cannot be parsed.
    """
    raw = ask(prompt, api_key=api_key)
    if not raw:
        return None

    cleaned = raw.strip()

    # Extract JSON inside ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    else:
        # Fallback: extract the first contiguous JSON object or array
        obj_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if obj_match:
            cleaned = obj_match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gemini JSON response: %s", e)
        return None
