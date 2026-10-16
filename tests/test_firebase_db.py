"""
Unit tests for Firebase Firestore Database module (utils/firebase_db.py).
Tests document serialization, Firestore CRUD operations, session hydration, and cloud sync hooks.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from utils.firebase_db import (
    _sanitize_data_for_firestore,
    save_module_data,
    load_module_data,
    load_all_user_data,
    hydrate_session_from_cloud,
    sync_module_to_cloud,
)


class TestFirestoreSanitization:
    """Tests for sanitizing nested Python data structures for Firestore compatibility."""

    def test_sanitizes_sets_and_tuples_to_lists(self):
        data = {
            "tags": {"python", "fastapi"},
            "coordinates": (10, 20),
            "score": 95,
            "nested": {
                "skills": ["go", "c++"],
                "ids": {1, 2, 3},
            },
        }
        sanitized = _sanitize_data_for_firestore(data)
        assert isinstance(sanitized["tags"], list)
        assert sorted(sanitized["tags"]) == ["fastapi", "python"]
        assert isinstance(sanitized["coordinates"], list)
        assert sanitized["coordinates"] == [10, 20]
        assert isinstance(sanitized["nested"]["ids"], list)

    def test_preserves_primitives_and_datetimes(self):
        now = datetime.now(timezone.utc)
        data = {"num": 42, "flag": True, "text": "hello", "time": now, "empty": None}
        sanitized = _sanitize_data_for_firestore(data)
        assert sanitized["num"] == 42
        assert sanitized["flag"] is True
        assert sanitized["text"] == "hello"
        assert sanitized["time"] == now
        assert sanitized["empty"] is None


class TestFirestoreCrud:
    """Tests for Firestore CRUD operations with mocked clients."""

    @patch("utils.firebase_db.get_firestore_client")
    def test_save_module_data_success(self, mock_client_getter):
        mock_client = MagicMock()
        mock_doc = MagicMock()
        mock_client.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc
        mock_client_getter.return_value = mock_client

        ok = save_module_data("uid_123", "resume", {"score": 85})
        assert ok
        mock_doc.set.assert_called_once()
        args, kwargs = mock_doc.set.call_args
        assert args[0]["score"] == 85
        assert "updated_at" in args[0]
        assert kwargs.get("merge") is True

    @patch("utils.firebase_db.get_firestore_client")
    def test_save_module_data_offline_graceful(self, mock_client_getter):
        mock_client_getter.return_value = None
        ok = save_module_data("uid_123", "resume", {"score": 85})
        assert not ok

    @patch("utils.firebase_db.get_firestore_client")
    def test_load_module_data_existing(self, mock_client_getter):
        mock_client = MagicMock()
        mock_snapshot = MagicMock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = {"score": 90, "user": "candidate"}

        mock_client.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_snapshot
        mock_client_getter.return_value = mock_client

        data = load_module_data("uid_123", "resume")
        assert data is not None
        assert data["score"] == 90
        assert data["user"] == "candidate"

    @patch("utils.firebase_db.get_firestore_client")
    def test_load_module_data_missing(self, mock_client_getter):
        mock_client = MagicMock()
        mock_snapshot = MagicMock()
        mock_snapshot.exists = False

        mock_client.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = mock_snapshot
        mock_client_getter.return_value = mock_client

        data = load_module_data("uid_123", "resume")
        assert data is None


class TestSessionHydrationAndSync:
    """Tests for session state hydration and sync hooks."""

    @patch("utils.firebase_db.load_all_user_data")
    def test_hydrate_session_from_cloud(self, mock_load_all):
        import streamlit as st
        mock_load_all.return_value = {
            "resume": {"ats": {"total": 88}},
            "github": {"total_score": 82},
            "leetcode": {"total_score": 75},
            "placement": {
                "readiness": {"composite_score": 85},
                "milestones": [{"id": "m1", "completed": True}],
                "pipeline": [{"company": "Google", "stage": "Applied"}],
            },
        }

        ok = hydrate_session_from_cloud("uid_777")
        assert ok
        assert st.session_state["resume_results"]["ats"]["total"] == 88
        assert st.session_state["github_audit"]["total_score"] == 82
        assert st.session_state["leetcode_audit"]["total_score"] == 75
        assert st.session_state["placement_readiness"]["composite_score"] == 85
        assert len(st.session_state["placement_milestones"]) == 1
        assert len(st.session_state["placement_pipeline"]) == 1

    @patch("utils.firebase_db.get_current_user")
    @patch("utils.firebase_db.save_module_data")
    def test_sync_module_to_cloud_logged_in(self, mock_save, mock_user):
        import streamlit as st
        mock_user.return_value = {"uid": "user_sync_test"}
        mock_save.return_value = True

        st.session_state["resume_results"] = {"ats": {"total": 92}}
        synced = sync_module_to_cloud("resume")
        assert synced
        mock_save.assert_called_once_with("user_sync_test", "resume", {"ats": {"total": 92}})

    @patch("utils.firebase_db.get_current_user", return_value=None)
    def test_sync_module_to_cloud_guest_mode_noop(self, mock_user):
        synced = sync_module_to_cloud("resume")
        assert not synced
