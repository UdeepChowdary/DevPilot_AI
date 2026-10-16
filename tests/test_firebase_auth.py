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
