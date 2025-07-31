"""Integration tests for the full Quoridor application stack."""

import json
import pytest
import requests
import subprocess
import time
import os
import signal
from contextlib import contextmanager
from multiprocessing import Process


# Test configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
STARTUP_TIMEOUT = 10  # seconds


@contextmanager
def backend_server():
    """Context manager to start and stop the backend server for testing."""
    # Start the backend server
    env = os.environ.copy()
    env.update({
        'HOST': BACKEND_HOST,
        'PORT': str(BACKEND_PORT),
        'SESSION_TIMEOUT_MINUTES': '5',
        'MAX_SESSIONS': '10',
        'ALLOWED_ORIGINS': '*'  # For testing only
    })
    
    process = subprocess.Popen(
        ['python', 'backend/main.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Create new process group
    )
    
    try:
        # Wait for server to start
        start_time = time.time()
        while time.time() - start_time < STARTUP_TIMEOUT:
            try:
                response = requests.get(f"{API_BASE_URL}/sessions", timeout=1)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError("Backend server failed to start within timeout")
        
        yield process
        
    finally:
        # Clean shutdown
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=5)
        except (subprocess.TimeoutExpired, ProcessLookupError):
            # Force kill if graceful shutdown fails
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass


class TestFullStackIntegration:
    """Integration tests for the complete application stack."""
    
    @pytest.fixture(scope="class")
    def backend(self):
        """Start backend server for integration tests."""
        with backend_server() as server:
            yield server
    
    def test_api_health_check(self, backend):
        """Test that the API is responsive and healthy."""
        response = requests.get(f"{API_BASE_URL}/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_sessions" in data
        assert "max_sessions" in data
        assert isinstance(data["active_sessions"], int)
        assert isinstance(data["max_sessions"], int)
    
    def test_session_lifecycle(self, backend):
        """Test creating, using, and cleaning up a game session."""
        # Create a new session
        create_response = requests.post(
            f"{API_BASE_URL}/sessions",
            json={"players": 2},
            headers={"Content-Type": "application/json"}
        )
        assert create_response.status_code == 200
        
        session_data = create_response.json()
        assert "session_id" in session_data
        session_id = session_data["session_id"]
        
        # Validate session_id format (should be UUID)
        import uuid
        uuid.UUID(session_id)  # Will raise if invalid
        
        # Get game state
        state_response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/state")
        assert state_response.status_code == 200
        
        state_data = state_response.json()
        assert "session_id" in state_data
        assert "observation" in state_data
        assert "done" in state_data
        assert "current_player" in state_data
        assert "board_size" in state_data
        assert state_data["session_id"] == session_id
        assert state_data["board_size"] == 9
        
        # Verify observation structure
        observation = state_data["observation"]
        if isinstance(observation, dict):
            # Object format
            assert "board" in observation or "players" in observation
        else:
            # Array format
            assert isinstance(observation, list)
        
        # Clean up session
        delete_response = requests.delete(f"{API_BASE_URL}/sessions/{session_id}")
        assert delete_response.status_code == 200
        
        # Verify session is gone
        state_response_after = requests.get(f"{API_BASE_URL}/sessions/{session_id}/state")
        assert state_response_after.status_code == 404
    
    def test_game_move_sequence(self, backend):
        """Test making moves in a game."""
        # Create session
        create_response = requests.post(
            f"{API_BASE_URL}/sessions",
            json={"players": 2}
        )
        session_id = create_response.json()["session_id"]
        
        # Get initial state
        initial_state = requests.get(f"{API_BASE_URL}/sessions/{session_id}/state")
        assert initial_state.status_code == 200
        
        initial_data = initial_state.json()
        initial_player = initial_data["current_player"]
        assert initial_data["done"] is False
        
        # Attempt to make a move
        move_response = requests.post(
            f"{API_BASE_URL}/move",
            json={
                "session_id": session_id,
                "player_id": initial_player,
                "action": 0  # Move action (up)
            }
        )
        
        # The move might be valid or invalid depending on board state
        # but the API should respond properly
        assert move_response.status_code in [200, 400]
        
        if move_response.status_code == 200:
            # Move was successful
            move_data = move_response.json()
            assert "observation" in move_data
            assert "done" in move_data
            assert "reward" in move_data
        else:
            # Move was invalid - check error format
            error_data = move_response.json()
            assert "detail" in error_data
            if isinstance(error_data["detail"], dict):
                assert "detail" in error_data["detail"]
                assert "error_type" in error_data["detail"]
        
        # Clean up
        requests.delete(f"{API_BASE_URL}/sessions/{session_id}")
    
    def test_session_limit_handling(self, backend):
        """Test that session limits are enforced properly."""
        created_sessions = []
        
        try:
            # Try to create more sessions than the limit (10 for test)
            for i in range(12):
                response = requests.post(
                    f"{API_BASE_URL}/sessions",
                    json={"players": 2}
                )
                
                if response.status_code == 200:
                    session_id = response.json()["session_id"]
                    created_sessions.append(session_id)
                elif response.status_code == 503:
                    # Session limit reached
                    break
                else:
                    pytest.fail(f"Unexpected status code: {response.status_code}")
            
            # Should have hit the limit before creating 12 sessions
            assert len(created_sessions) <= 10
            
        finally:
            # Clean up created sessions
            for session_id in created_sessions:
                try:
                    requests.delete(f"{API_BASE_URL}/sessions/{session_id}")
                except:
                    pass  # Ignore cleanup errors
    
    def test_rate_limiting(self, backend):
        """Test that rate limiting works properly."""
        # Make rapid requests to trigger rate limiting
        responses = []
        
        for i in range(110):  # More than the 100 req/min limit
            try:
                response = requests.get(f"{API_BASE_URL}/sessions", timeout=1)
                responses.append(response.status_code)
            except requests.RequestException:
                responses.append(None)
            
            # Small delay to avoid overwhelming the server
            if i % 10 == 0:
                time.sleep(0.01)
        
        # Should get some 429 (rate limited) responses
        rate_limited_count = responses.count(429)
        successful_count = responses.count(200)
        
        # Should have triggered rate limiting
        assert rate_limited_count > 0, f"Expected rate limiting, got responses: {set(responses)}"
        assert successful_count > 0, "Should have some successful requests"
    
    def test_error_handling_consistency(self, backend):
        """Test that all endpoints return consistent error formats."""
        # Test invalid session ID
        invalid_session_id = "invalid-uuid"
        
        response = requests.get(f"{API_BASE_URL}/sessions/{invalid_session_id}/state")
        assert response.status_code == 422  # Validation error
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Test non-existent session
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = requests.get(f"{API_BASE_URL}/sessions/{fake_uuid}/state")
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Test malformed move request
        response = requests.post(
            f"{API_BASE_URL}/move",
            json={"invalid": "data"}
        )
        assert response.status_code == 422
        
        error_data = response.json()
        assert "detail" in error_data
    
    def test_cors_headers(self, backend):
        """Test that CORS headers are properly set."""
        response = requests.options(f"{API_BASE_URL}/sessions")
        
        # Should have CORS headers for preflight
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        
        # Test actual request has CORS headers
        response = requests.get(f"{API_BASE_URL}/sessions")
        assert "Access-Control-Allow-Origin" in response.headers


class TestFrontendBackendIntegration:
    """Tests that simulate frontend-backend communication patterns."""
    
    @pytest.fixture(scope="class")
    def backend(self):
        """Start backend server for integration tests."""
        with backend_server() as server:
            yield server
    
    def test_frontend_session_workflow(self, backend):
        """Test the typical frontend session workflow."""
        # 1. Frontend checks for existing sessions
        sessions_response = requests.get(f"{API_BASE_URL}/sessions")
        assert sessions_response.status_code == 200
        
        # 2. Frontend creates a new session
        create_response = requests.post(
            f"{API_BASE_URL}/sessions",
            json={"players": 2}
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # 3. Frontend polls for game state (simulating real usage)
        poll_count = 0
        max_polls = 5
        
        while poll_count < max_polls:
            state_response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/state")
            assert state_response.status_code == 200
            
            state_data = state_response.json()
            assert "observation" in state_data
            assert "current_player" in state_data
            assert "board_size" in state_data
            
            # Simulate frontend processing delay
            time.sleep(0.1)
            poll_count += 1
        
        # 4. Frontend cleans up session when done
        delete_response = requests.delete(f"{API_BASE_URL}/sessions/{session_id}")
        assert delete_response.status_code == 200
    
    def test_concurrent_sessions(self, backend):
        """Test multiple concurrent sessions (simulating multiple users)."""
        session_ids = []
        
        try:
            # Create multiple sessions concurrently
            import concurrent.futures
            
            def create_session():
                response = requests.post(f"{API_BASE_URL}/sessions", json={"players": 2})
                return response.json()["session_id"] if response.status_code == 200 else None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(create_session) for _ in range(3)]
                session_ids = [f.result() for f in futures if f.result() is not None]
            
            assert len(session_ids) >= 2, "Should be able to create concurrent sessions"
            
            # Test concurrent access to different sessions
            def get_session_state(session_id):
                response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/state")
                return response.status_code == 200
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(get_session_state, sid) for sid in session_ids]
                results = [f.result() for f in futures]
            
            assert all(results), "All concurrent session accesses should succeed"
            
        finally:
            # Clean up
            for session_id in session_ids:
                try:
                    requests.delete(f"{API_BASE_URL}/sessions/{session_id}")
                except:
                    pass


if __name__ == "__main__":
    # Allow running integration tests directly
    pytest.main([__file__, "-v"])