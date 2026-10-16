"""
🔥 Firebase Client Initialization & Config Manager — DevPilot AI
Initializes firebase-admin and manages Firebase configuration across
environment variables, Streamlit secrets, and local service account keys.
Provides graceful fallbacks for 100% offline guest mode when Firebase is not configured.
"""

import os
import json
import logging
import threading
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_FIREBASE_APP_LOCK = threading.Lock()
_FIREBASE_INITIALIZED = False
_FIRESTORE_CLIENT: Optional[Any] = None


def get_config_val(key: str, default: str = "") -> str:
    """
    Retrieve a configuration value by priority:
    1. Streamlit secrets (st.secrets)
    2. Environment variables (os.environ)
    3. Provided default value
    """
    val = ""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
    except Exception:
        pass

    if not val:
        val = os.getenv(key, "").strip()

    return val or default


def get_firebase_web_api_key() -> str:
    """Return the Firebase Web API Key for Authentication REST endpoints."""
    return get_config_val("FIREBASE_WEB_API_KEY")


def get_firebase_project_id() -> str:
    """Return the Firebase Project ID."""
    return get_config_val("FIREBASE_PROJECT_ID")


def is_firebase_auth_configured() -> bool:
    """Returns True if the Firebase Web API Key is present."""
    return bool(get_firebase_web_api_key())


def is_firestore_configured() -> bool:
    """
    Returns True if either a valid service account file path or
    inline service account credentials are provided.
    """
    sa_path = get_config_val("FIREBASE_SERVICE_ACCOUNT_PATH")
    if sa_path and os.path.isfile(sa_path):
        return True

    client_email = get_config_val("FIREBASE_CLIENT_EMAIL")
    private_key = get_config_val("FIREBASE_PRIVATE_KEY")
    if client_email and private_key:
        return True

    return False


def get_firestore_client():
    """
    Thread-safe lazy initialization of the Firestore client via firebase-admin.
    Returns the google.cloud.firestore.Client instance, or None if not configured.
    """
    global _FIREBASE_INITIALIZED, _FIRESTORE_CLIENT

    if _FIRESTORE_CLIENT is not None:
        return _FIRESTORE_CLIENT

    with _FIREBASE_APP_LOCK:
        if _FIRESTORE_CLIENT is not None:
            return _FIRESTORE_CLIENT

        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            # Check if an app is already initialized
            if not firebase_admin._apps:
                cred = None
                sa_path = get_config_val("FIREBASE_SERVICE_ACCOUNT_PATH")
                if sa_path and os.path.isfile(sa_path):
                    cred = credentials.Certificate(sa_path)
                else:
                    client_email = get_config_val("FIREBASE_CLIENT_EMAIL")
                    private_key = get_config_val("FIREBASE_PRIVATE_KEY")
                    project_id = get_firebase_project_id()

                    if client_email and private_key:
                        # Normalize escaped newlines in private key
                        norm_private_key = private_key.replace("\\n", "\n")
                        cert_dict = {
                            "type": "service_account",
                            "project_id": project_id,
                            "client_email": client_email,
                            "private_key": norm_private_key,
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                        cred = credentials.Certificate(cert_dict)

                if cred:
                    project_id = get_firebase_project_id()
                    options = {"projectId": project_id} if project_id else None
                    firebase_admin.initialize_app(cred, options)
                    _FIREBASE_INITIALIZED = True
                    logger.info("Firebase Admin initialized successfully.")
                else:
                    logger.debug("Firebase service account credentials not found; Firestore offline.")
                    return None

            _FIRESTORE_CLIENT = firestore.client()
            return _FIRESTORE_CLIENT

        except Exception as e:
            logger.warning("Could not initialize Firestore client: %s", e)
            return None
