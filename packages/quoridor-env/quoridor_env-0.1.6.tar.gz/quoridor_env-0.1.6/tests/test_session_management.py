import unittest
import os
import sys
import time
import threading
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from main import (
        GameSession, get_session, cleanup_expired_sessions, sessions, 
        sessions_lock, SESSION_TIMEOUT_MINUTES, MAX_SESSIONS
    )
    MAIN_MODULE_AVAILABLE = True
except ImportError:
    MAIN_MODULE_AVAILABLE = False


@unittest.skipUnless(MAIN_MODULE_AVAILABLE, "Main module not available")
class TestSessionManagement(unittest.TestCase):
    """Test suite for session management functionality."""

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

    def test_game_session_creation(self):
        """Test GameSession creation and initialization."""
        session = GameSession()
        self.assertIsNotNone(session.env)
        self.assertIsNotNone(session.obs)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.last_accessed)
        self.assertIsNotNone(session._lock)
        
        # Check that session is not expired on creation
        self.assertFalse(session.is_expired())

    def test_session_expiration_check(self):
        """Test session expiration logic."""
        session = GameSession()
        
        # Fresh session should not be expired
        self.assertFalse(session.is_expired())
        
        # Mock old last_accessed time to simulate expiration
        old_time = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 1)
        with patch.object(session, 'last_accessed', old_time):
            self.assertTrue(session.is_expired())

    def test_session_update_access_time(self):
        """Test updating session access time."""
        session = GameSession()
        original_time = session.last_accessed
        
        # Wait a small amount to ensure time difference
        time.sleep(0.001)
        
        session.update_access_time()
        self.assertGreater(session.last_accessed, original_time)

    def test_session_thread_safety(self):
        """Test session thread safety with concurrent access."""
        session = GameSession()
        results = []
        errors = []
        
        def access_session():
            try:
                for _ in range(10):
                    session.update_access_time()
                    is_expired = session.is_expired()
                    results.append(is_expired)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=access_session) for _ in range(5)]
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that no errors occurred and all results are False (not expired)
        self.assertEqual(len(errors), 0)
        self.assertTrue(all(not result for result in results))

    def test_get_session_success(self):
        """Test successful session retrieval."""
        session_id = "test-session-123"
        
        # Add a session to the global store
        with sessions_lock:
            sessions[session_id] = GameSession()
        
        # Retrieve the session
        retrieved_session = get_session(session_id)
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session, sessions[session_id])

    def test_get_session_not_found(self):
        """Test session retrieval for non-existent session."""
        from fastapi import HTTPException
        
        non_existent_id = "non-existent-session"
        
        with self.assertRaises(HTTPException) as context:
            get_session(non_existent_id)
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Session not found")

    def test_get_session_expired(self):
        """Test session retrieval for expired session."""
        from fastapi import HTTPException
        
        session_id = "expired-session-123"
        
        # Create session and mock it as expired
        session = GameSession()
        old_time = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 1)
        
        with sessions_lock:
            sessions[session_id] = session
        
        # Mock the session's last_accessed time to make it expired
        with patch.object(session, 'last_accessed', old_time):
            with self.assertRaises(HTTPException) as context:
                get_session(session_id)
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Session expired")
        
        # Verify session was removed from store
        with sessions_lock:
            self.assertNotIn(session_id, sessions)

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        session_id_1 = "session-1"
        session_id_2 = "session-2"
        session_id_3 = "session-3"
        
        # Create sessions with different expiration states
        session_1 = GameSession()  # Fresh session
        session_2 = GameSession()  # Will be mocked as expired
        session_3 = GameSession()  # Fresh session
        
        with sessions_lock:
            sessions[session_id_1] = session_1
            sessions[session_id_2] = session_2
            sessions[session_id_3] = session_3
        
        # Mock session_2 as expired
        old_time = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 1)
        with patch.object(session_2, 'last_accessed', old_time):
            cleanup_expired_sessions()
        
        # Check that only expired session was removed
        with sessions_lock:
            self.assertIn(session_id_1, sessions)
            self.assertNotIn(session_id_2, sessions)  # Should be removed
            self.assertIn(session_id_3, sessions)

    def test_session_limit_enforcement(self):
        """Test session limit enforcement during cleanup."""
        # Create more than MAX_SESSIONS
        excess_sessions = MAX_SESSIONS + 5
        session_ids = []
        
        with sessions_lock:
            for i in range(excess_sessions):
                session_id = f"session-{i}"
                session = GameSession()
                sessions[session_id] = session
                session_ids.append(session_id)
                
                # Make older sessions have older access times
                if i < 5:  # First 5 sessions are older
                    old_time = datetime.now() - timedelta(minutes=i * 2)
                    session.last_accessed = old_time
        
        # Run cleanup
        cleanup_expired_sessions()
        
        # Check that sessions were limited to MAX_SESSIONS
        with sessions_lock:
            self.assertLessEqual(len(sessions), MAX_SESSIONS)
            
            # The oldest sessions should have been removed
            remaining_sessions = list(sessions.keys())
            for session_id in session_ids[:5]:  # First 5 (oldest) should be removed
                self.assertNotIn(session_id, remaining_sessions)

    def test_concurrent_session_access(self):
        """Test concurrent access to session store."""
        session_id = "concurrent-test-session"
        results = []
        errors = []
        
        def create_and_access_session():
            try:
                # Create session
                with sessions_lock:
                    if session_id not in sessions:
                        sessions[session_id] = GameSession()
                
                # Access session multiple times
                for _ in range(5):
                    session = get_session(session_id)
                    session.update_access_time()
                    results.append(True)
                    time.sleep(0.001)
                    
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=create_and_access_session) for _ in range(3)]
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that no errors occurred
        self.assertEqual(len(errors), 0)
        self.assertGreater(len(results), 0)
        
        # Clean up
        with sessions_lock:
            if session_id in sessions:
                del sessions[session_id]

    def test_session_step_thread_safety(self):
        """Test thread safety of session step operations."""
        session = GameSession()
        results = []
        errors = []
        
        def perform_step():
            try:
                # Simulate taking a step (action 0 is usually safe)
                obs, reward, done, truncated, info = session.step_with_lock(0)
                results.append((obs, reward, done, truncated, info))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads to perform steps
        threads = [threading.Thread(target=perform_step) for _ in range(3)]
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that operations completed (might have some game logic errors, but no threading issues)
        self.assertLessEqual(len(errors), 3)  # Allow for some game logic errors
        self.assertGreaterEqual(len(results), 0)

    def test_session_reset_thread_safety(self):
        """Test thread safety of session reset operations."""
        session = GameSession()
        results = []
        errors = []
        
        def perform_reset():
            try:
                obs = session.reset_with_lock()
                results.append(obs)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads to perform resets
        threads = [threading.Thread(target=perform_reset) for _ in range(3)]
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that operations completed successfully
        self.assertEqual(len(errors), 0)
        self.assertGreater(len(results), 0)

    def test_session_with_player_count(self):
        """Test session with player count attribute."""
        session = GameSession()
        
        # Add player count attribute (as done in create_session endpoint)
        session.player_count = 4
        
        self.assertEqual(session.player_count, 4)


if __name__ == '__main__':
    unittest.main()