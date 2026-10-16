"""
Unit tests for Firebase Authentication module (utils/firebase_auth.py).
Tests REST API interactions, error translation, input validation, and session state management.
"""

import pytest
from unittest.mock import patch, MagicMock
from utils.firebase_auth import (
    sign_up,
    sign_in,
    send_password_reset,
    get_current_user,
    set_current_user,
    logout_user,
    _parse_error,
)


class TestFirebaseAuthValidation:
    """Tests for input validation prior to network requests."""

    def test_signup_missing_fields(self):
        ok, msg, data = sign_up("", "password123")
        assert not ok
        assert "email" in msg.lower()
        assert data is None

        ok, msg, data = sign_up("test@example.com", "")
        assert not ok
        assert "password" in msg.lower()
        assert data is None

    def test_signup_short_password(self):
        ok, msg, data = sign_up("test@example.com", "123")
        assert not ok
        assert "6 characters" in msg
        assert data is None

    def test_signin_missing_fields(self):
        ok, msg, data = sign_in("", "")
        assert not ok
        assert "both" in msg.lower()
        assert data is None

    def test_reset_empty_email(self):
        ok, msg = send_password_reset("")
        assert not ok
        assert "email" in msg.lower()


class TestFirebaseAuthRestEndpoints:
    """Tests for REST API requests with mocked HTTP responses."""

    @patch("utils.firebase_auth.get_firebase_web_api_key", return_value="fake_api_key")
    @patch("requests.post")
    def test_signup_success(self, mock_post, mock_key):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "localId": "user_123",
            "email": "dev@example.com",
            "idToken": "token_abc",
            "refreshToken": "refresh_xyz",
            "expiresIn": "3600",
        }
        mock_post.return_value = mock_response

        ok, msg, udata = sign_up("dev@example.com", "securePassword123")
        assert ok
        assert "success" in msg.lower()
        assert udata is not None
        assert udata["uid"] == "user_123"
        assert udata["email"] == "dev@example.com"
        assert udata["id_token"] == "token_abc"

    @patch("utils.firebase_auth.get_firebase_web_api_key", return_value="fake_api_key")
    @patch("requests.post")
    def test_signup_email_exists_error(self, mock_post, mock_key):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "EMAIL_EXISTS"}
        }
        mock_post.return_value = mock_response

        ok, msg, udata = sign_up("existing@example.com", "password123")
        assert not ok
        assert "already exists" in msg.lower()
        assert udata is None

    @patch("utils.firebase_auth.get_firebase_web_api_key", return_value="fake_api_key")
    @patch("requests.post")
    def test_signin_success(self, mock_post, mock_key):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "localId": "user_456",
            "email": "alex@example.com",
            "displayName": "Alex",
            "idToken": "token_456",
            "refreshToken": "ref_456",
            "expiresIn": "3600",
        }
        mock_post.return_value = mock_response

        ok, msg, udata = sign_in("alex@example.com", "pass1234")
        assert ok
        assert udata is not None
        assert udata["uid"] == "user_456"
        assert udata["display_name"] == "Alex"

    @patch("utils.firebase_auth.get_firebase_web_api_key", return_value="fake_api_key")
    @patch("requests.post")
    def test_signin_invalid_credentials(self, mock_post, mock_key):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "INVALID_LOGIN_CREDENTIALS"}
        }
        mock_post.return_value = mock_response

        ok, msg, udata = sign_in("alex@example.com", "wrongpass")
        assert not ok
        assert "invalid" in msg.lower()
        assert udata is None

    @patch("utils.firebase_auth.get_firebase_web_api_key", return_value="fake_api_key")
    @patch("requests.post")
    def test_password_reset_success(self, mock_post, mock_key):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "user@example.com"}
        mock_post.return_value = mock_response

        ok, msg = send_password_reset("user@example.com")
        assert ok
        assert "email sent" in msg.lower()


class TestSessionStateManagement:
    """Tests for current user session state caching."""

    @pytest.fixture(autouse=True)
    def isolate_session_cache(self, tmp_path):
        test_cache = str(tmp_path / ".test_session.json")
        with patch("utils.firebase_auth.get_session_cache_files", return_value=(test_cache,)):
            yield

    def test_session_user_roundtrip(self):
        user_payload = {"uid": "u999", "email": "test@devpilot.ai", "id_token": "tok"}
        set_current_user(user_payload)
        retrieved = get_current_user()
        assert retrieved == user_payload

        logout_user()
        assert get_current_user() is None

    def test_error_parser_fallbacks(self):
        custom_err = {"error": {"message": "CUSTOM_ERROR_CODE"}}
        parsed = _parse_error(custom_err)
        assert parsed == "CUSTOM_ERROR_CODE"

    def test_session_token_generation_and_verification(self):
        from utils.firebase_auth import generate_session_token, verify_session_token
        token = generate_session_token("uid_persistent_1", "persistent@devpilot.ai")
        assert token is not None
        assert len(token) > 50

        verified = verify_session_token(token)
        assert verified is not None
        assert verified["uid"] == "uid_persistent_1"
        assert verified["email"] == "persistent@devpilot.ai"

    def test_tampered_session_token_rejected(self):
        from utils.firebase_auth import generate_session_token, verify_session_token
        token = generate_session_token("uid_legit", "legit@devpilot.ai")
        tampered = token[:-4] + "zzzz"
        assert verify_session_token(tampered) is None

    @patch("utils.firebase_db.hydrate_session_from_cloud")
    def test_init_auth_recovers_user_from_query_params_after_f5(self, mock_hydrate, tmp_path):
        import streamlit as st
        from utils.firebase_auth import (
            generate_session_token,
            init_auth,
            logout_user,
            clear_persisted_session,
            SESSION_QUERY_PARAM,
        )

        test_cache = str(tmp_path / ".test_session.json")
        with patch("utils.firebase_auth.get_session_cache_files", return_value=(test_cache,)):
            # Simulate F5 reload where session_state was cleared but query_params persisted
            logout_user()
            clear_persisted_session()
            st.session_state["auth_user"] = None
            token = generate_session_token("f5_user", "f5@devpilot.ai")
            st.query_params[SESSION_QUERY_PARAM] = token

            recovered = init_auth()
            assert recovered is not None
            assert recovered["uid"] == "f5_user"
            assert recovered["email"] == "f5@devpilot.ai"
            mock_hydrate.assert_called_once_with("f5_user")
            logout_user()
            clear_persisted_session()

    @patch("utils.firebase_db.hydrate_session_from_cloud")
    def test_init_auth_recovers_user_from_file_cache(self, mock_hydrate, tmp_path):
        import streamlit as st
        from utils.firebase_auth import (
            persist_user_session,
            init_auth,
            logout_user,
            clear_persisted_session,
            SESSION_QUERY_PARAM,
        )

        test_cache = str(tmp_path / ".test_session.json")
        with patch("utils.firebase_auth.get_session_cache_files", return_value=(test_cache,)):
            logout_user()
            clear_persisted_session()

            # Persist a user to file cache
            persist_user_session({"uid": "file_cache_user", "email": "cached@devpilot.ai"})
            # Remove query param so it must fall back to file cache
            if SESSION_QUERY_PARAM in st.query_params:
                del st.query_params[SESSION_QUERY_PARAM]
            st.session_state["auth_user"] = None

            recovered = init_auth()
            assert recovered is not None
            assert recovered["uid"] == "file_cache_user"
            assert recovered["email"] == "cached@devpilot.ai"
            mock_hydrate.assert_called_with("file_cache_user")

            logout_user()
