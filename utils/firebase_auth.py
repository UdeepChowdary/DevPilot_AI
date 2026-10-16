"""
🔐 Firebase Authentication Module — DevPilot AI
Provides Email/Password sign up, sign in, password reset, and token management
via Firebase Auth REST API (Identity Toolkit).
Integrates seamlessly into Streamlit session state with Guest Mode fallback.
"""

import logging
import requests
import os
import time
import hmac
import hashlib
import json
import base64
from typing import Optional, Dict, Any, Tuple
from utils.firebase_client import get_firebase_web_api_key, is_firebase_auth_configured

logger = logging.getLogger(__name__)

SESSION_QUERY_PARAM = "auth_session"

FIREBASE_AUTH_BASE = "https://identitytoolkit.googleapis.com/v1"
FIREBASE_TOKEN_BASE = "https://securetoken.googleapis.com/v1"

# Friendly error messages for Firebase Auth error codes
AUTH_ERROR_MESSAGES = {
    "EMAIL_EXISTS": "An account with this email address already exists. Please sign in instead.",
    "OPERATION_NOT_ALLOWED": "Password sign-in is not enabled in Firebase Console. Please enable it under Authentication > Sign-in method.",
    "CONFIGURATION_NOT_FOUND": "Firebase Authentication is not activated yet in Firebase Console. Please open your Firebase Console (Build > Authentication), click 'Get Started', and enable Email/Password.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Access to this account has been temporarily disabled. Try again later.",
    "EMAIL_NOT_FOUND": "No account found with this email address.",
    "INVALID_PASSWORD": "Incorrect password. Please try again.",
    "INVALID_LOGIN_CREDENTIALS": "Invalid email or password. Please verify your credentials.",
    "USER_DISABLED": "This user account has been disabled by an administrator.",
    "WEAK_PASSWORD : Password should be at least 6 characters": "Password must be at least 6 characters long.",
    "INVALID_EMAIL": "Please enter a valid email address.",
    "MISSING_PASSWORD": "Password field cannot be empty.",
    "MISSING_EMAIL": "Email field cannot be empty.",
}


def _parse_error(response_data: Dict[str, Any]) -> str:
    """Extract a user-friendly error message from Firebase REST response."""
    error = response_data.get("error", {})
    message = error.get("message", "An unexpected authentication error occurred.")
    return AUTH_ERROR_MESSAGES.get(message, message)


def sign_up(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Register a new user with email and password via Firebase Auth REST API.
    Returns: (success: bool, message: str, user_data: Optional[dict])
    """
    clean_email = (email or "").strip()
    if not clean_email or not password:
        return False, "Please enter both an email address and password.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    api_key = get_firebase_web_api_key()
    if not api_key:
        return False, "Firebase Web API Key is not configured. Running in offline Guest Mode.", None

    url = f"{FIREBASE_AUTH_BASE}/accounts:signUp?key={api_key}"
    payload = {
        "email": clean_email,
        "password": password,
        "returnSecureToken": True,
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200:
            user_data = {
                "uid": data.get("localId"),
                "email": data.get("email"),
                "id_token": data.get("idToken"),
                "refresh_token": data.get("refreshToken"),
                "expires_in": data.get("expiresIn"),
            }
            return True, "Account created successfully!", user_data
        else:
            return False, _parse_error(data), None
    except requests.RequestException as e:
        logger.error("Network error during Firebase sign_up: %s", e)
        return False, f"Network error connecting to Firebase: {e}", None


def sign_in(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate a user with email and password via Firebase Auth REST API.
    Returns: (success: bool, message: str, user_data: Optional[dict])
    """
    clean_email = (email or "").strip()
    if not clean_email or not password:
        return False, "Please enter both email and password.", None

    api_key = get_firebase_web_api_key()
    if not api_key:
        return False, "Firebase Web API Key is not configured. Running in offline Guest Mode.", None

    url = f"{FIREBASE_AUTH_BASE}/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": clean_email,
        "password": password,
        "returnSecureToken": True,
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200:
            user_data = {
                "uid": data.get("localId"),
                "email": data.get("email"),
                "display_name": data.get("displayName") or clean_email.split("@")[0],
                "id_token": data.get("idToken"),
                "refresh_token": data.get("refreshToken"),
                "expires_in": data.get("expiresIn"),
            }
            return True, "Signed in successfully!", user_data
        else:
            return False, _parse_error(data), None
    except requests.RequestException as e:
        logger.error("Network error during Firebase sign_in: %s", e)
        return False, f"Network error connecting to Firebase: {e}", None


def send_password_reset(email: str) -> Tuple[bool, str]:
    """
    Trigger a password reset email via Firebase Auth REST API.
    Returns: (success: bool, message: str)
    """
    clean_email = (email or "").strip()
    if not clean_email:
        return False, "Please provide your account email address."

    api_key = get_firebase_web_api_key()
    if not api_key:
        return False, "Firebase Web API Key is not configured."

    url = f"{FIREBASE_AUTH_BASE}/accounts:sendOobCode?key={api_key}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": clean_email,
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200:
            return True, "Password reset email sent! Check your inbox."
        else:
            return False, _parse_error(data)
    except requests.RequestException as e:
        return False, f"Network error sending password reset: {e}"


# ─── Streamlit Session State Integration ──────────────────────────────────────

SESSION_CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".devpilot_session.json")
USER_SESSION_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".devpilot_session.json")


def get_session_cache_files() -> Tuple[str, ...]:
    """Return all session cache file locations (project root and user home)."""
    return (SESSION_CACHE_FILE, USER_SESSION_CACHE_FILE)


def _get_auth_signing_key() -> str:
    """Retrieve secret key for signing session tokens."""
    return get_firebase_web_api_key() or os.getenv("SECRET_KEY", "devpilot-ai-default-auth-salt")


def generate_session_token(uid: str, email: str, expiry_days: int = 30) -> str:
    """Generate a tamper-proof HMAC-signed session token for persistent browser sessions."""
    payload = {
        "uid": uid,
        "email": email,
        "exp": int(time.time()) + (expiry_days * 86400),
    }
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    sig = hmac.new(_get_auth_signing_key().encode('utf-8'), payload_bytes, hashlib.sha256).digest()
    p_b64 = base64.urlsafe_b64encode(payload_bytes).decode('ascii').rstrip('=')
    s_b64 = base64.urlsafe_b64encode(sig).decode('ascii').rstrip('=')
    return f"{p_b64}.{s_b64}"


def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify an HMAC-signed session token and return user dict if valid and unexpired."""
    try:
        if not token or "." not in token:
            return None
        p_b64, s_b64 = token.split(".", 1)
        # Restore padding
        p_b64 += "=" * ((4 - len(p_b64) % 4) % 4)
        s_b64 += "=" * ((4 - len(s_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(p_b64.encode('ascii'))
        sig = base64.urlsafe_b64decode(s_b64.encode('ascii'))
        expected_sig = hmac.new(_get_auth_signing_key().encode('utf-8'), payload_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        payload = json.loads(payload_bytes.decode('utf-8'))
        if time.time() > payload.get("exp", 0):
            return None
        return {
            "uid": payload["uid"],
            "email": payload["email"],
            "display_name": payload.get("email", "").split("@")[0],
        }
    except Exception:
        return None


def persist_user_session(user_data: Dict[str, Any]) -> None:
    """Persist user session token into Streamlit query params and local cache files so reload (F5) doesn't sign out."""
    if not user_data or not user_data.get("uid"):
        return
    token = generate_session_token(user_data["uid"], user_data.get("email", ""))
    # 1. Browser URL query param
    try:
        import streamlit as st
        st.query_params[SESSION_QUERY_PARAM] = token
    except Exception:
        pass
    # 2. Local session cache files (project root and user home fallback)
    cache_payload = {"token": token, "email": user_data.get("email"), "uid": user_data["uid"]}
    for cache_path in get_session_cache_files():
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f)
        except Exception as e:
            logger.debug("Could not write local session cache to %s: %s", cache_path, e)


def clear_persisted_session() -> None:
    """Remove session token from query params and local cache files upon logout."""
    try:
        import streamlit as st
        if SESSION_QUERY_PARAM in st.query_params:
            del st.query_params[SESSION_QUERY_PARAM]
    except Exception:
        pass
    for cache_path in get_session_cache_files():
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
        except Exception as e:
            logger.debug("Could not remove local session cache at %s: %s", cache_path, e)


def init_auth() -> Optional[Dict[str, Any]]:
    """
    Initialize and recover authenticated user session.
    Checks st.session_state first, then st.query_params, then local cache files.
    If recovered, auto-hydrates data from Firestore.
    """
    import streamlit as st

    current_user = get_current_user()
    if current_user and current_user.get("uid"):
        # Keep query param in sync in case user navigated across pages
        try:
            if SESSION_QUERY_PARAM not in st.query_params:
                persist_user_session(current_user)
        except Exception:
            pass
        return current_user

    token = None
    # 1. Check query_params
    try:
        token = st.query_params.get(SESSION_QUERY_PARAM)
    except Exception:
        pass

    # 2. Check local file caches if query_params was empty (e.g. page navigation stripped it)
    if not token:
        for cache_path in get_session_cache_files():
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, "r", encoding="utf-8") as f:
                        cached = json.load(f)
                        t = cached.get("token")
                        if t:
                            token = t
                            break
                except Exception:
                    continue

    if token:
        user_info = verify_session_token(token)
        if user_info and user_info.get("uid"):
            set_current_user(user_info)
            persist_user_session(user_info)
            try:
                from utils.firebase_db import hydrate_session_from_cloud
                hydrate_session_from_cloud(user_info["uid"])
            except Exception as e:
                logger.error("Error during cloud session hydration: %s", e)
            logger.info("Restored persistent user session for '%s'.", user_info["email"])
            return user_info
        else:
            clear_persisted_session()

    return None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Retrieve the currently authenticated user from Streamlit session_state."""
    try:
        import streamlit as st
        return st.session_state.get("auth_user")
    except Exception:
        return None


def set_current_user(user_data: Dict[str, Any]) -> None:
    """Store the authenticated user profile in Streamlit session_state."""
    try:
        import streamlit as st
        st.session_state["auth_user"] = user_data
    except Exception:
        pass


def logout_user() -> None:
    """Log out the current user and reset authenticated session state."""
    try:
        import streamlit as st
        st.session_state["auth_user"] = None
        st.session_state["cloud_sync_status"] = "offline"
        clear_persisted_session()
        # Reset module session keys so next user or guest does not see lingering data
        keys_to_clear = [
            "resume_results",
            "gh_data", "gh_audit", "gh_user", "gh_target_user", "github_audit", "gh_ai_critique",
            "interview_session", "interview_evaluations", "interview_questions", "candidate_answers", "interview_active",
            "lc_stats", "leetcode_audit", "lc_username", "lc_target_user",
            "placement_readiness", "placement_milestones", "placement_pipeline", "ai_placement_strategy"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    except Exception:
        pass


def render_auth_section(widget_key: str = "sidebar_auth") -> None:
    """
    Renders an interactive Firebase Authentication & Cloud Sync widget in the sidebar.
    Displays active user profile and sync options if logged in,
    or tabbed Sign In / Sign Up / Reset Password forms if in Guest Mode.
    """
    import streamlit as st
    from utils.firebase_client import is_firebase_auth_configured
    from utils.firebase_db import hydrate_session_from_cloud, sync_module_to_cloud

    current_user = init_auth()
    auth_available = is_firebase_auth_configured()

    if current_user:
        email = current_user.get("email", "Candidate")
        masked_email = email if len(email) <= 24 else email[:21] + "..."
        st.markdown(f"""
<div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 10px; padding: 0.65rem 0.85rem; margin-bottom: 0.5rem;">
    <div style="font-size: 0.78rem; color: #4ade80; font-weight: 700;">
        <span style="display:inline-block; width:7px; height:7px; background:#22c55e; border-radius:50%; margin-right:5px;"></span>Cloud Synced
    </div>
    <div style="font-size: 0.74rem; color: #cbd5e1; font-family:'JetBrains Mono',monospace; margin-top:3px; word-break:break-all;">
        {masked_email}
    </div>
</div>
""", unsafe_allow_html=True)
        col_sync, col_out = st.columns([1, 1])
        with col_sync:
            if st.button("🔄 Sync Now", key=f"{widget_key}_sync_btn", use_container_width=True):
                for mod in ["resume", "github", "interview", "leetcode", "placement"]:
                    sync_module_to_cloud(mod)
                st.success("Synced!")
                st.rerun()
        with col_out:
            if st.button("Log Out", key=f"{widget_key}_logout_btn", use_container_width=True):
                logout_user()
                st.info("Logged out to Guest Mode.")
                st.rerun()
        return

    # User is in Guest Mode
    expander_title = "👤 Account & Sync  " + ("○ Sign In" if auth_available else "○ Guest")
    with st.expander(expander_title, expanded=False):
        if not auth_available:
            st.markdown("""
<div style="font-size: 0.75rem; color: #94a3b8; line-height: 1.5; margin-bottom: 0.5rem;">
    <b>Guest Mode Active:</b> Your scores & pipeline are stored in local session memory. Configure Firebase in <code>.env</code> to activate cloud sync.
</div>
""", unsafe_allow_html=True)
        tab_in, tab_up, tab_reset = st.tabs(["Sign In", "Sign Up", "Reset"])

        with tab_in:
            in_email = st.text_input("Email", key=f"{widget_key}_signin_email", placeholder="you@domain.com")
            in_pass = st.text_input("Password", type="password", key=f"{widget_key}_signin_password")
            if st.button("Sign In to Cloud", key=f"{widget_key}_signin_btn", type="primary", use_container_width=True):
                if in_email and in_pass:
                    ok, msg, udata = sign_in(in_email, in_pass)
                    if ok and udata:
                        set_current_user(udata)
                        persist_user_session(udata)
                        hydrate_session_from_cloud(udata["uid"])
                        st.success("✅ Signed in! Cloud profile restored.")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter your email and password.")

        with tab_up:
            up_email = st.text_input("Email", key=f"{widget_key}_signup_email", placeholder="you@domain.com")
            up_pass = st.text_input("Password (min 6 chars)", type="password", key=f"{widget_key}_signup_password")
            if st.button("Create Account", key=f"{widget_key}_signup_btn", use_container_width=True):
                if up_email and up_pass:
                    ok, msg, udata = sign_up(up_email, up_pass)
                    if ok and udata:
                        set_current_user(udata)
                        persist_user_session(udata)
                        for mod in ["resume", "github", "interview", "leetcode", "placement"]:
                            sync_module_to_cloud(mod)
                        st.success("✅ Account created and synced!")
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter an email and password.")

        with tab_reset:
            rst_email = st.text_input("Email", key=f"{widget_key}_reset_email", placeholder="you@domain.com")
            if st.button("Send Reset Link", key=f"{widget_key}_reset_btn", use_container_width=True):
                if rst_email:
                    ok, msg = send_password_reset(rst_email)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter your account email.")

