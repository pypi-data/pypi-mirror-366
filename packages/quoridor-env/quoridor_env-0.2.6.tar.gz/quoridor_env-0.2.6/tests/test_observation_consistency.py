import unittest
import os
import sys
import numpy as np
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from main import GameSession, sessions, sessions_lock
    MAIN_MODULE_AVAILABLE = True
except ImportError:
    MAIN_MODULE_AVAILABLE = False


@unittest.skipUnless(MAIN_MODULE_AVAILABLE, "Main module not available")
class TestObservationConsistency(unittest.TestCase):
    """Test suite for observation structure consistency after PR fix."""

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

    def test_session_obs_type_after_init(self):
        """Test that session.obs is always np.ndarray after initialization."""
        session = GameSession()
        
        # Should be np.ndarray, not tuple
        self.assertIsInstance(session.obs, np.ndarray)
        self.assertEqual(session.obs.dtype, np.float32)
        # Should have shape (num_players + 2, board_size, board_size)
        self.assertEqual(len(session.obs.shape), 3)

    def test_session_obs_type_after_reset(self):
        """Test that session.obs remains np.ndarray after reset."""
        session = GameSession()
        
        # Reset the session
        reset_result = session.reset_with_lock()
        
        # reset_with_lock should return tuple (obs, info)
        self.assertIsInstance(reset_result, tuple)
        self.assertEqual(len(reset_result), 2)
        self.assertIsInstance(reset_result[0], np.ndarray)
        self.assertIsInstance(reset_result[1], dict)
        
        # But session.obs should be normalized to just the observation array
        self.assertIsInstance(session.obs, np.ndarray)
        self.assertEqual(session.obs.dtype, np.float32)
        
        # Should be same as the observation part of reset result
        np.testing.assert_array_equal(session.obs, reset_result[0])

    def test_session_obs_type_after_step(self):
        """Test that session.obs remains np.ndarray after step."""
        session = GameSession()
        
        # Take a step (action 0 should be safe for most environments)
        try:
            step_result = session.step_with_lock(0)
            
            # step_with_lock should return tuple (obs, reward, done, truncated, info)
            self.assertIsInstance(step_result, tuple)
            self.assertEqual(len(step_result), 5)
            self.assertIsInstance(step_result[0], np.ndarray)  # obs
            self.assertIsInstance(step_result[1], (int, float))  # reward
            self.assertIsInstance(step_result[2], bool)  # done
            self.assertIsInstance(step_result[3], bool)  # truncated
            self.assertIsInstance(step_result[4], dict)  # info
            
            # But session.obs should be normalized to just the observation array
            self.assertIsInstance(session.obs, np.ndarray)
            self.assertEqual(session.obs.dtype, np.float32)
            
            # Should be same as the observation part of step result
            np.testing.assert_array_equal(session.obs, step_result[0])
            
        except Exception as e:
            # If step fails due to invalid action, that's okay for this test
            # We just want to make sure if it succeeds, the observation is consistent
            if "invalid" not in str(e).lower():
                raise

    def test_observation_consistency_across_reset_step_cycle(self):
        """Test observation consistency across reset-step-reset cycles."""
        session = GameSession()
        
        # Initial state - should be np.ndarray
        self.assertIsInstance(session.obs, np.ndarray)
        initial_obs = session.obs.copy()
        
        # Reset - should remain np.ndarray  
        reset_result = session.reset_with_lock()
        self.assertIsInstance(session.obs, np.ndarray)
        reset_obs = session.obs.copy()
        
        # Step (try a few different actions to find a valid one)
        step_success = False
        for action in [0, 1, 2, 4, 8]:  # Try some common valid actions
            try:
                step_result = session.step_with_lock(action)
                step_success = True
                break
            except:
                continue
        
        if step_success:
            # After step - should remain np.ndarray
            self.assertIsInstance(session.obs, np.ndarray)
            step_obs = session.obs.copy()
            
            # Reset again - should remain np.ndarray
            reset_result_2 = session.reset_with_lock()
            self.assertIsInstance(session.obs, np.ndarray)
            
            # All observations should have consistent shape and type
            self.assertEqual(initial_obs.shape, reset_obs.shape)
            self.assertEqual(reset_obs.shape, step_obs.shape)
            self.assertEqual(step_obs.shape, session.obs.shape)
            
            self.assertEqual(initial_obs.dtype, reset_obs.dtype)
            self.assertEqual(reset_obs.dtype, step_obs.dtype)
            self.assertEqual(step_obs.dtype, session.obs.dtype)
        else:
            self.skipTest("Could not find valid action for step test")

    def test_observation_shape_consistency(self):
        """Test that observation always has expected shape."""
        session = GameSession()
        
        # Should have shape (num_players + 2, board_size, board_size)
        expected_channels = 4  # 2 players + 2 wall channels for default 2-player game
        expected_board_size = 9  # Default Quoridor board size
        
        self.assertEqual(session.obs.shape, (expected_channels, expected_board_size, expected_board_size))
        
        # After reset
        session.reset_with_lock()
        self.assertEqual(session.obs.shape, (expected_channels, expected_board_size, expected_board_size))

    def test_no_tuple_access_needed(self):
        """Test that session.obs can be used directly without tuple indexing."""
        session = GameSession()
        
        # Should be able to call .tolist() directly (this was failing before the fix)
        try:
            obs_list = session.obs.tolist()
            self.assertIsInstance(obs_list, list)
        except AttributeError:
            self.fail("session.obs should support .tolist() directly (no tuple indexing needed)")
        
        # Should be able to access shape directly
        try:
            shape = session.obs.shape
            self.assertIsInstance(shape, tuple)
        except AttributeError:
            self.fail("session.obs should support .shape directly (no tuple indexing needed)")
        
        # Should be able to access dtype directly
        try:
            dtype = session.obs.dtype
            self.assertEqual(dtype, np.float32)
        except AttributeError:
            self.fail("session.obs should support .dtype directly (no tuple indexing needed)")

    def test_concurrent_observation_access(self):
        """Test thread-safe observation access after normalization."""
        import threading
        import time
        
        session = GameSession()
        results = []
        errors = []
        
        def access_obs():
            try:
                for _ in range(10):
                    # Access observation properties
                    shape = session.obs.shape
                    dtype = session.obs.dtype
                    obs_list = session.obs.tolist()
                    
                    results.append((shape, dtype, type(obs_list)))
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=access_obs) for _ in range(3)]
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that no errors occurred
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertGreater(len(results), 0)
        
        # All results should be consistent
        first_result = results[0]
        for result in results:
            self.assertEqual(result[0], first_result[0])  # shape
            self.assertEqual(result[1], first_result[1])  # dtype
            self.assertEqual(result[2], first_result[2])  # list type

    def test_mock_env_returns_tuple_but_session_normalizes(self):
        """Test that even if env returns tuples, session normalizes them."""
        session = GameSession()
        
        # Mock the env to return tuple for reset
        mock_obs = np.zeros((4, 9, 9), dtype=np.float32)
        mock_info = {"test": True}
        
        with patch.object(session.env, 'reset', return_value=(mock_obs, mock_info)):
            reset_result = session.reset_with_lock()
            
            # reset_with_lock should return the tuple
            self.assertEqual(reset_result, (mock_obs, mock_info))
            
            # But session.obs should be normalized to just the observation
            self.assertIsInstance(session.obs, np.ndarray)
            np.testing.assert_array_equal(session.obs, mock_obs)
        
        # Mock the env to return tuple for step
        mock_reward = 1.0
        mock_done = False
        mock_truncated = False
        mock_step_info = {"step": True}
        
        with patch.object(session.env, 'step', return_value=(mock_obs, mock_reward, mock_done, mock_truncated, mock_step_info)):
            step_result = session.step_with_lock(0)
            
            # step_with_lock should return the tuple
            self.assertEqual(step_result, (mock_obs, mock_reward, mock_done, mock_truncated, mock_step_info))
            
            # But session.obs should be normalized to just the observation
            self.assertIsInstance(session.obs, np.ndarray)
            np.testing.assert_array_equal(session.obs, mock_obs)


if __name__ == '__main__':
    unittest.main()