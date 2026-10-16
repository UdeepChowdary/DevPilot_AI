"""
🗄️ Firebase Firestore Database Manager & Cloud Hydrator — DevPilot AI
Manages persistent user data across all 5 DevPilot AI modules in Cloud Firestore:
- users/{uid}/modules/resume
- users/{uid}/modules/github
- users/{uid}/modules/interview
- users/{uid}/modules/leetcode
- users/{uid}/modules/placement (Milestones & Application Pipeline)

Supports non-blocking background auto-saving and full session state hydration upon login.
"""

import logging
import threading
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from utils.firebase_client import get_firestore_client, is_firestore_configured
from utils.firebase_auth import get_current_user

logger = logging.getLogger(__name__)


def _sanitize_data_for_firestore(obj: Any) -> Any:
    """
    Recursively sanitize Python data structures so they are 100% compatible with Firestore.
    Converts unsupported types (tuples, custom objects, sets) into standard lists and dicts.
    """
    if isinstance(obj, dict):
        return {str(k): _sanitize_data_for_firestore(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [_sanitize_data_for_firestore(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    elif isinstance(obj, datetime):
        return obj
    else:
        return str(obj)


def save_module_data(uid: str, module_name: str, data: Dict[str, Any]) -> bool:
    """
    Persist module data to Firestore at users/{uid}/modules/{module_name}.
    Returns True on success, False on failure.
    """
    if not uid or not module_name:
        return False

    client = get_firestore_client()
    if client is None:
        logger.debug("Firestore client unavailable. Skipping cloud write for module '%s'.", module_name)
        return False

    try:
        clean_data = _sanitize_data_for_firestore(data)
        clean_data["updated_at"] = datetime.now(timezone.utc)

        doc_ref = client.collection("users").document(uid).collection("modules").document(module_name)
        doc_ref.set(clean_data, merge=True)
        logger.info("Successfully synced module '%s' for user '%s' to Firestore.", module_name, uid)
        return True
    except Exception as e:
        logger.error("Failed to write module '%s' to Firestore for user '%s': %s", module_name, uid, e)
        return False


def load_module_data(uid: str, module_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve module data from Firestore at users/{uid}/modules/{module_name}.
    Returns document dictionary or None if not found or on error.
    """
    if not uid or not module_name:
        return None

    client = get_firestore_client()
    if client is None:
        return None

    try:
        doc_ref = client.collection("users").document(uid).collection("modules").document(module_name)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error("Failed to read module '%s' from Firestore for user '%s': %s", module_name, uid, e)
        return None


def load_all_user_data(uid: str) -> Dict[str, Any]:
    """
    Fetch all module documents for a user from Firestore.
    Returns a dict mapping module_name -> document data.
    """
    if not uid:
        return {}

    client = get_firestore_client()
    if client is None:
        return {}

    all_data = {}
    try:
        modules_ref = client.collection("users").document(uid).collection("modules")
        docs = modules_ref.stream()
        for doc in docs:
            all_data[doc.id] = doc.to_dict()
        return all_data
    except Exception as e:
        logger.error("Failed to load all Firestore data for user '%s': %s", uid, e)
        return {}


def _extract_module_data_from_session(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Extract full state dictionary for a module from Streamlit session state on the main thread.
    MUST be called on the main thread where st.session_state is available.
    """
    try:
        import streamlit as st
    except ImportError:
        return None

    if module_name == "resume":
        return st.session_state.get("resume_results")

    elif module_name == "github":
        audit = st.session_state.get("gh_audit") or st.session_state.get("github_audit")
        data = st.session_state.get("gh_data")
        username = st.session_state.get("gh_user") or st.session_state.get("gh_target_user")
        if not audit and not data:
            return None
        return {
            "audit": audit,
            "data": data,
            "username": username,
        }

    elif module_name == "interview":
        session = st.session_state.get("interview_session")
        evals = st.session_state.get("interview_evaluations")
        if not session and not evals:
            return None
        return {
            "session": session,
            "evaluations": evals or [],
            "role": st.session_state.get("session_role"),
            "style": st.session_state.get("session_style"),
        }

    elif module_name == "leetcode":
        audit = st.session_state.get("leetcode_audit")
        stats = st.session_state.get("lc_stats")
        username = st.session_state.get("lc_username") or st.session_state.get("lc_target_user")
        if not audit and not stats:
            return None
        return {
            "audit": audit,
            "stats": stats,
            "username": username,
        }

    elif module_name == "placement":
        return {
            "readiness": st.session_state.get("placement_readiness"),
            "milestones": st.session_state.get("placement_milestones"),
            "pipeline": st.session_state.get("placement_pipeline"),
            "target_date": str(st.session_state.get("target_placement_date")) if st.session_state.get("target_placement_date") else None,
        }

    return None


def hydrate_session_from_cloud(uid: str) -> bool:
    """
    Hydrate Streamlit session state from Cloud Firestore when a user signs in.
    Loads cached resume, GitHub audit, interview history, LeetCode data, and placement pipeline.
    """
    import streamlit as st

    if not uid:
        return False

    all_modules = load_all_user_data(uid)
    if not all_modules:
        st.session_state["cloud_sync_status"] = "synced_empty"
        logger.info("No cloud data found for user '%s'. Backing up active guest session.", uid)
        # Auto-backup any active session data from guest mode into the new account
        for mod in ["resume", "github", "interview", "leetcode", "placement"]:
            sync_module_to_cloud(mod)
        return True

    # 1. Resume Module
    if "resume" in all_modules and all_modules["resume"]:
        st.session_state["resume_results"] = all_modules["resume"]

    # 2. GitHub Module
    if "github" in all_modules and all_modules["github"]:
        gh_mod = all_modules["github"]
        audit = gh_mod.get("audit") or gh_mod
        data = gh_mod.get("data")
        username = gh_mod.get("username")
        st.session_state["github_audit"] = audit
        st.session_state["gh_audit"] = audit
        if data:
            st.session_state["gh_data"] = data
        if username:
            st.session_state["gh_user"] = username
            st.session_state["gh_target_user"] = username

    # 3. Mock Interview Module
    if "interview" in all_modules and all_modules["interview"]:
        int_mod = all_modules["interview"]
        session = int_mod.get("session") or int_mod
        st.session_state["interview_session"] = session
        if "evaluations" in int_mod and int_mod["evaluations"]:
            st.session_state["interview_evaluations"] = int_mod["evaluations"]
        if "role" in int_mod and int_mod["role"]:
            st.session_state["session_role"] = int_mod["role"]
        if "style" in int_mod and int_mod["style"]:
            st.session_state["session_style"] = int_mod["style"]

    # 4. LeetCode Module
    if "leetcode" in all_modules and all_modules["leetcode"]:
        lc_mod = all_modules["leetcode"]
        audit = lc_mod.get("audit") or lc_mod
        stats = lc_mod.get("stats")
        username = lc_mod.get("username")
        st.session_state["leetcode_audit"] = audit
        if stats:
            st.session_state["lc_stats"] = stats
        if username:
            st.session_state["lc_username"] = username
            st.session_state["lc_target_user"] = username

    # 5. Placement Dashboard Module
    if "placement" in all_modules and all_modules["placement"]:
        place_data = all_modules["placement"]
        if "readiness" in place_data and place_data["readiness"]:
            st.session_state["placement_readiness"] = place_data["readiness"]
        if "milestones" in place_data and place_data["milestones"]:
            st.session_state["placement_milestones"] = place_data["milestones"]
        if "pipeline" in place_data and place_data["pipeline"]:
            st.session_state["placement_pipeline"] = place_data["pipeline"]

    st.session_state["cloud_sync_status"] = "synced"
    logger.info("Streamlit session hydrated from Firestore for user '%s'.", uid)
    return True


def sync_module_to_cloud(module_name: str) -> bool:
    """
    Extract active state for a specific module from st.session_state and sync to Firestore.
    Safe no-op if user is not logged in or Firestore is not configured.
    """
    user = get_current_user()
    if not user or not user.get("uid"):
        return False

    uid = user["uid"]
    data_to_save = _extract_module_data_from_session(module_name)

    if data_to_save:
        success = save_module_data(uid, module_name, data_to_save)
        if success:
            try:
                import streamlit as st
                st.session_state["cloud_sync_status"] = "synced"
            except Exception:
                pass
            return True

    return False


def sync_module_to_cloud_async(module_name: str) -> None:
    """
    Trigger a background sync of module state to Firestore so the UI does not block.
    CRITICAL: Extracts the user profile and session data on the MAIN thread before spawning the worker,
    because child threads in Streamlit do not possess the ScriptRunContext and cannot access st.session_state.
    """
    user = get_current_user()
    if not user or not user.get("uid"):
        return

    uid = user["uid"]
    data_to_save = _extract_module_data_from_session(module_name)
    if not data_to_save:
        return

    def _background_worker(target_uid: str, target_mod: str, payload: Dict[str, Any]):
        try:
            save_module_data(target_uid, target_mod, payload)
        except Exception as e:
            logger.error("Background sync failed for module '%s': %s", target_mod, e)

    thread = threading.Thread(
        target=_background_worker,
        args=(uid, module_name, data_to_save),
        daemon=True,
    )
    thread.start()


def sync_all_modules_to_cloud(uid: Optional[str] = None) -> bool:
    """Sync all 5 modules from the active session to Firestore."""
    user = get_current_user()
    target_uid = uid or (user.get("uid") if user else None)
    if not target_uid:
        return False

    success_any = False
    for mod in ["resume", "github", "interview", "leetcode", "placement"]:
        data = _extract_module_data_from_session(mod)
        if data:
            if save_module_data(target_uid, mod, data):
                success_any = True
    return success_any
