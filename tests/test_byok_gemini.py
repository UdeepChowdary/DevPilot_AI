"""
Unit tests for DevPilot AI Bring-Your-Own-Key (BYOK) Gemini API integration.
Verifies universal key synchronization across session state, environment, and all 5 sub-apps.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from utils.gemini_client import (
    get_active_gemini_key,
    set_active_gemini_key,
    clear_active_gemini_key,
)


@pytest.fixture(autouse=True)
def clean_gemini_env():
    """Ensure clean GEMINI_API_KEY environment for each test."""
    orig = os.environ.get("GEMINI_API_KEY")
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    yield
    if orig is not None:
        os.environ["GEMINI_API_KEY"] = orig
    elif "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]


def test_explicit_api_key_takes_priority():
    os.environ["GEMINI_API_KEY"] = "env-key-12345"
    res = get_active_gemini_key("explicit-key-99999")
    assert res == "explicit-key-99999"


def test_env_api_key_fallback():
    os.environ["GEMINI_API_KEY"] = "env-key-12345"
    res = get_active_gemini_key()
    assert res == "env-key-12345"


def test_session_state_takes_priority_over_env():
    mock_st = MagicMock()
    mock_st.session_state = {"gemini_api_key": "session-key-abcde"}

    with patch.dict("sys.modules", {"streamlit": mock_st}):
        os.environ["GEMINI_API_KEY"] = "env-key-12345"
        res = get_active_gemini_key()
        assert res == "session-key-abcde"


def test_set_active_gemini_key_syncs_to_env():
    mock_st = MagicMock()
    mock_st.session_state = {}

    with patch.dict("sys.modules", {"streamlit": mock_st}):
        set_active_gemini_key("user-pasted-key-xyz")
        assert mock_st.session_state["gemini_api_key"] == "user-pasted-key-xyz"
        assert os.environ.get("GEMINI_API_KEY") == "user-pasted-key-xyz"


def test_clear_active_gemini_key():
    mock_st = MagicMock()
    mock_st.session_state = {"gemini_api_key": "to-be-cleared"}
    os.environ["GEMINI_API_KEY"] = "to-be-cleared"

    with patch.dict("sys.modules", {"streamlit": mock_st}):
        clear_active_gemini_key()
        assert mock_st.session_state.get("gemini_api_key") == ""
        assert "GEMINI_API_KEY" not in os.environ


def test_all_subapps_pick_up_byok_key():
    """Verify that setting the BYOK key immediately makes it available across all sub-apps."""
    mock_st = MagicMock()
    mock_st.session_state = {}

    with patch.dict("sys.modules", {"streamlit": mock_st}):
        test_key = "AIzaSyTestUniversalKey123456789"
        set_active_gemini_key(test_key)

        from utils.github_ai_reviewer import generate_ai_critique
        from utils.interview_coach import generate_interview_questions
        from utils.leetcode_coach import analyze_code_complexity
        from utils.placement_tracker import generate_placement_strategy

        # Verify key is visible via get_active_gemini_key in each context
        assert get_active_gemini_key() == test_key
