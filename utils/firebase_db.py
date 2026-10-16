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
        return True

    # 1. Resume Module
    if "resume" in all_modules and all_modules["resume"]:
        st.session_state["resume_results"] = all_modules["resume"]

    # 2. GitHub Module
    if "github" in all_modules and all_modules["github"]:
        st.session_state["github_audit"] = all_modules["github"]

    # 3. Mock Interview Module
    if "interview" in all_modules and all_modules["interview"]:
        st.session_state["interview_session"] = all_modules["interview"]

    # 4. LeetCode Module
    if "leetcode" in all_modules and all_modules["leetcode"]:
        st.session_state["leetcode_audit"] = all_modules["leetcode"]

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
    import streamlit as st

    user = get_current_user()
    if not user or not user.get("uid"):
        return False

    uid = user["uid"]

    data_to_save: Optional[Dict[str, Any]] = None

    if module_name == "resume":
        data_to_save = st.session_state.get("resume_results")
    elif module_name == "github":
        data_to_save = st.session_state.get("github_audit")
    elif module_name == "interview":
        data_to_save = st.session_state.get("interview_session")
    elif module_name == "leetcode":
        data_to_save = st.session_state.get("leetcode_audit")
    elif module_name == "placement":
        data_to_save = {
            "readiness": st.session_state.get("placement_readiness"),
            "milestones": st.session_state.get("placement_milestones"),
            "pipeline": st.session_state.get("placement_pipeline"),
        }

    if data_to_save:
        success = save_module_data(uid, module_name, data_to_save)
        if success:
            st.session_state["cloud_sync_status"] = "synced"
            return True

    return False


def sync_module_to_cloud_async(module_name: str) -> None:
    """
    Trigger a background sync of module state to Firestore so the UI does not block.
    """
    thread = threading.Thread(target=sync_module_to_cloud, args=(module_name,), daemon=True)
    thread.start()
