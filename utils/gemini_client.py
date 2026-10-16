import os
import re
import json
import logging
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_active_gemini_key(api_key: Optional[str] = None) -> str:
    """
    Retrieve the active Gemini API key from explicit argument,
    Streamlit session_state, or environment variables in priority order.
    """
    key = (api_key or "").strip()
    if not key:
        try:
            import streamlit as st
            key = (st.session_state.get("gemini_api_key") or "").strip()
            if not key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                key = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass
    if not key:
        key = os.getenv("GEMINI_API_KEY", "").strip()
    return key


def set_active_gemini_key(new_key: str) -> None:
    """
    Persist the Gemini API key in the user's Streamlit session state
    so all sub-apps in the current session immediately share it, without
    contaminating process-global environment variables across other user sessions.
    """
    cleaned = (new_key or "").strip()
    try:
        import streamlit as st
        st.session_state["gemini_api_key"] = cleaned
    except Exception:
        pass


def clear_active_gemini_key() -> None:
    """Clear the active Gemini API key from the current user session state."""
    try:
        import streamlit as st
        st.session_state["gemini_api_key"] = ""
    except Exception:
        pass


def render_byok_section(widget_key: str = "byok_gemini", compact: bool = False, title: Optional[str] = None) -> str:
    """
    Renders an interactive 'Bring Your Own Key' UI widget for Gemini API.
    Saves the key to st.session_state["gemini_api_key"] and os.environ["GEMINI_API_KEY"]
    so that it immediately becomes active across all sub-apps in the current session.
    Returns the active API key string.
    """
    import streamlit as st

    active_key = get_active_gemini_key()

    if active_key:
        masked = active_key[:6] + "..." + active_key[-4:] if len(active_key) > 10 else "***"
        if compact:
            st.markdown(
                f"""
<div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 8px; padding: 0.55rem 0.8rem; margin: 0.4rem 0;">
    <div style="font-size: 0.78rem; color: #4ade80; font-weight: 600;">
        <span style="display:inline-block; width:7px; height:7px; background:#22c55e; border-radius:50%; margin-right:5px;"></span>Gemini Key Active (<code style="color:#86efac; font-size:0.75rem;">{masked}</code>)
    </div>
    <div style="font-size: 0.7rem; color: #94a3b8; margin-top:2px;">Shared across all sub-apps</div>
</div>
""",
                unsafe_allow_html=True,
            )
            col_chg, col_clr = st.columns([1, 1])
            with col_chg:
                show_edit = st.toggle("Change", key=f"{widget_key}_toggle_edit")
            with col_clr:
                if st.button("Clear Key", key=f"{widget_key}_clear_btn", use_container_width=True):
                    clear_active_gemini_key()
                    st.rerun()
            if show_edit:
                new_input = st.text_input(
                    "New Gemini API Key",
                    type="password",
                    placeholder="AIzaSy...",
                    key=f"{widget_key}_edit_input",
                )
                if new_input.strip():
                    set_active_gemini_key(new_input)
                if st.button("Update Key", key=f"{widget_key}_save_edit", type="primary", use_container_width=True):
                    if new_input.strip():
                        set_active_gemini_key(new_input)
                        st.success("✅ Key updated across all sub-apps!")
                        st.rerun()
                    else:
                        st.warning("Please paste a valid key first.")
        else:
            st.markdown(
                f"""
<div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.8rem;">
    <div style="display:flex; align-items:center; justify-content:space-between;">
        <div>
            <div style="font-size: 0.86rem; color: #4ade80; font-weight: 700;">
                <span style="display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; margin-right:6px;"></span>Gemini API Key Connected
            </div>
            <div style="font-size: 0.75rem; color: #cbd5e1; font-family:'JetBrains Mono',monospace; margin-top: 3px;">
                Active Key: <code style="color:#86efac;">{masked}</code>
            </div>
        </div>
    </div>
    <div style="font-size: 0.73rem; color: #94a3b8; margin-top: 4px;">
        ✅ This key is actively powering Gemini AI analysis across all 5 sub-apps.
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                edit_opt = st.toggle("Update Key", key=f"{widget_key}_edit_toggle")
            with c2:
                if st.button("Remove Key", key=f"{widget_key}_remove_btn", use_container_width=True):
                    clear_active_gemini_key()
                    st.rerun()

            if edit_opt:
                new_k = st.text_input("Paste new Gemini API Key:", type="password", placeholder="AIzaSy...", key=f"{widget_key}_new_val")
                if new_k.strip():
                    set_active_gemini_key(new_k)
                if st.button("Save New Key", key=f"{widget_key}_save_btn", type="primary"):
                    if new_k.strip():
                        set_active_gemini_key(new_k)
                        st.success("✅ Key updated across all sub-apps!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid key.")
        return active_key

    # When no key is active:
    section_title = title or "🔑 Bring Your Own Key (BYOK) — Google Gemini AI"
    st.markdown(
        f"""
<div style="background: rgba(99, 102, 241, 0.07); border: 1px dashed rgba(99, 102, 241, 0.4); border-radius: 10px; padding: 0.85rem 1rem; margin: 0.5rem 0;">
    <div style="font-size: 0.88rem; font-weight: 700; color: #c4b5fd; margin-bottom: 0.25rem;">
        {section_title}
    </div>
    <div style="font-size: 0.76rem; color: #cbd5e1; line-height: 1.5;">
        Paste your Google Gemini API key once below. It will automatically activate Gemini AI analysis across <b>all 5 sub-apps</b> for this entire session.
    </div>
    <div style="margin-top: 0.4rem; font-size: 0.73rem;">
        <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #818cf8; text-decoration: none; font-weight: 600;">
            Get a free Gemini API key at Google AI Studio ↗
        </a>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    input_key = st.text_input(
        "Paste Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        key=f"{widget_key}_input_slot",
        help="Your key is kept strictly in memory for this session and never written to disk or sent to third parties.",
    )
    if input_key and input_key.strip():
        set_active_gemini_key(input_key.strip())

    if st.button("Activate Key Across All Sub-Apps", key=f"{widget_key}_activate_btn", type="primary", use_container_width=True):
        if input_key and input_key.strip():
            set_active_gemini_key(input_key.strip())
            st.success("✅ Gemini Key activated! Ready to use across all sub-apps.")
            st.rerun()
        else:
            st.warning("Please paste a valid Gemini API key first.")

    return get_active_gemini_key()


def _get_client(api_key: Optional[str] = None):
    """
    Return a thread-isolated genai.Client instance.
    Uses google-genai (new SDK) first, falls back to legacy google-generativeai if unavailable.
    """
    key = get_active_gemini_key(api_key)
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
