import unittest
import json
import os
import sys
import uuid
from unittest.mock import patch, MagicMock
import threading
import time

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from fastapi.testclient import TestClient
    from main import app, sessions, sessions_lock, cleanup_expired_sessions
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI test dependencies not available")
class TestFastAPIEndpoints(unittest.TestCase):
    """Comprehensive test suite for FastAPI endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear sessions before each test
        with sessions_lock:
            sessions.clear()

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Clear sessions after each test
        with sessions_lock:
            sessions.clear()

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("version", data)
        self.assertIn("api_version", data)

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Quoridor Backend API")
        self.assertIn("version", data)
        self.assertIn("api_version", data)
        self.assertIn("docs_url", data)

    def test_create_session_success(self):
        """Test successful session creation."""
        response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("session_id", data)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Session created successfully")
        
        # Verify session was created
        with sessions_lock:
            self.assertIn(data["session_id"], sessions)

    def test_create_session_invalid_players(self):
        """Test session creation with invalid player count."""
        response = self.client.post(
            "/api/v1/sessions",
            json={"players": 5}  # Invalid - more than 4 players
        )
        self.assertEqual(response.status_code, 422)  # Pydantic validation error

    def test_create_session_missing_data(self):
        """Test session creation with missing data."""
        response = self.client.post("/api/v1/sessions", json={})
        self.assertEqual(response.status_code, 200)  # Should use default players=2

    def test_list_sessions(self):
        """Test listing sessions."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # List sessions
        response = self.client.get("/api/v1/sessions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["active_sessions"], 1)
        self.assertIn("max_sessions", data)
        self.assertEqual(len(data["sessions"]), 1)
        self.assertEqual(data["sessions"][0]["session_id"], session_id)

    def test_get_session_state(self):
        """Test getting session state."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Get session state
        response = self.client.get(f"/api/v1/sessions/{session_id}/state")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], session_id)
        self.assertIn("observation", data)
        self.assertIn("done", data)
        self.assertIn("current_player", data)

    def test_get_session_state_not_found(self):
        """Test getting state for non-existent session."""
        fake_session_id = str(uuid.uuid4())
        response = self.client.get(f"/api/v1/sessions/{fake_session_id}/state")
        self.assertEqual(response.status_code, 404)

    def test_reset_game(self):
        """Test resetting a game session."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Reset the session
        response = self.client.post(f"/api/v1/sessions/{session_id}/reset")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], session_id)
        self.assertIn("observation", data)
        self.assertFalse(data["done"])

    def test_make_move_valid(self):
        """Test making a valid move."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Make a move
        response = self.client.post(
            "/api/v1/move",
            json={
                "session_id": session_id,
                "player_id": 0,
                "action": 0
            }
        )
        # Note: This might fail if action 0 is invalid in the game logic
        # but it should at least pass validation
        self.assertIn(response.status_code, [200, 400])  # 400 if invalid move in game logic

    def test_make_move_invalid_session(self):
        """Test making a move with invalid session."""
        fake_session_id = str(uuid.uuid4())
        response = self.client.post(
            "/api/v1/move",
            json={
                "session_id": fake_session_id,
                "player_id": 0,
                "action": 0
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_make_move_invalid_action(self):
        """Test making a move with invalid action."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Try negative action
        response = self.client.post(
            "/api/v1/move",
            json={
                "session_id": session_id,
                "player_id": 0,
                "action": -1
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_make_move_action_too_large(self):
        """Test making a move with action that's too large."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Try action that exceeds bounds
        response = self.client.post(
            "/api/v1/move",
            json={
                "session_id": session_id,
                "player_id": 0,
                "action": 2000000  # Way too large
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_get_session_log(self):
        """Test getting session log."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Get session log
        response = self.client.get(f"/api/v1/sessions/{session_id}/log")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], session_id)
        self.assertIn("log", data)
        self.assertIn("log_size", data)

    def test_delete_session(self):
        """Test deleting a session."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Delete the session
        response = self.client.delete(f"/api/v1/sessions/{session_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["session_id"], session_id)
        
        # Verify session was deleted
        with sessions_lock:
            self.assertNotIn(session_id, sessions)

    def test_delete_session_not_found(self):
        """Test deleting non-existent session."""
        fake_session_id = str(uuid.uuid4())
        response = self.client.delete(f"/api/v1/sessions/{fake_session_id}")
        self.assertEqual(response.status_code, 404)

    def test_invalid_session_id_format(self):
        """Test endpoints with invalid session ID format."""
        invalid_session_id = "not-a-uuid"
        
        # Test various endpoints with invalid UUID
        endpoints = [
            ("GET", f"/api/v1/sessions/{invalid_session_id}/state"),
            ("POST", f"/api/v1/sessions/{invalid_session_id}/reset"),
            ("GET", f"/api/v1/sessions/{invalid_session_id}/log"),
            ("DELETE", f"/api/v1/sessions/{invalid_session_id}"),
        ]
        
        for method, url in endpoints:
            response = getattr(self.client, method.lower())(url)
            # Should return 422 for validation error or 404 for not found
            self.assertIn(response.status_code, [404, 422])

    def test_move_request_validation(self):
        """Test move request validation."""
        # Create a session first
        create_response = self.client.post(
            "/api/v1/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Test invalid session ID format in move request
        response = self.client.post(
            "/api/v1/move",
            json={
                "session_id": "invalid-uuid",
                "player_id": 0,
                "action": 0
            }
        )
        self.assertEqual(response.status_code, 422)  # Pydantic validation error
        
        # Test invalid player ID
        response = self.client.post(
            "/api/v1/move",
            json={
                "session_id": session_id,
                "player_id": 5,  # Invalid - only 0-3 allowed
                "action": 0
            }
        )
        self.assertEqual(response.status_code, 422)  # Pydantic validation error


if __name__ == '__main__':
    unittest.main()