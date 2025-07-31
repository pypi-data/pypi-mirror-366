import unittest
import json
import os
import sys
import numpy as np
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from quoridor_sim.episode_logger import EpisodeLogger
    from example_integration import create_game_observation, QuoridorGame
    SERIALIZATION_MODULES_AVAILABLE = True
except ImportError:
    SERIALIZATION_MODULES_AVAILABLE = False


@unittest.skipUnless(SERIALIZATION_MODULES_AVAILABLE, "Serialization test dependencies not available")
class TestNumpySerializationFixes(unittest.TestCase):
    """Test suite for NumPy serialization fixes."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.logger = EpisodeLogger(log_dir=self.test_dir)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_numpy_array_serialization(self):
        """Test that NumPy arrays are properly serialized to lists."""
        # Create various NumPy arrays
        test_arrays = {
            "1d_array": np.array([1, 2, 3, 4]),
            "2d_array": np.array([[1, 2], [3, 4]]),
            "3d_array": np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]]),
            "float_array": np.array([1.1, 2.2, 3.3]),
            "bool_array": np.array([True, False, True]),
            "int8_array": np.array([1, 2, 3], dtype=np.int8),
            "int64_array": np.array([1000000, 2000000], dtype=np.int64),
        }
        
        for array_name, array in test_arrays.items():
            with self.subTest(array_name=array_name):
                serialized = self.logger._serialize_observation(array)
                
                # Should be a list, not numpy array
                self.assertIsInstance(serialized, list)
                
                # Should be JSON serializable
                try:
                    json.dumps(serialized)
                except (TypeError, ValueError):
                    self.fail(f"Serialized {array_name} is not JSON serializable")
                
                # Content should match original array
                self.assertEqual(serialized, array.tolist())

    def test_numpy_scalar_serialization(self):
        """Test that NumPy scalars are properly serialized."""
        test_scalars = {
            "np_int32": np.int32(42),
            "np_int64": np.int64(1000000),
            "np_float32": np.float32(3.14),
            "np_float64": np.float64(2.71828),
            "np_bool": np.bool_(True),
            "np_uint8": np.uint8(255),
        }
        
        for scalar_name, scalar in test_scalars.items():
            with self.subTest(scalar_name=scalar_name):
                serialized = self.logger._serialize_observation(scalar)
                
                # Should be a Python native type, not numpy type
                self.assertNotIsInstance(serialized, (np.integer, np.floating, np.bool_))
                
                # Should be JSON serializable
                try:
                    json.dumps(serialized)
                except (TypeError, ValueError):
                    self.fail(f"Serialized {scalar_name} is not JSON serializable")
                
                # Value should match original scalar
                self.assertEqual(serialized, scalar.item())

    def test_mixed_data_structure_serialization(self):
        """Test serialization of complex data structures containing NumPy arrays."""
        complex_observation = {
            "board_state": np.array([[1, 0, 2], [0, 1, 0], [2, 0, 1]]),
            "player_positions": [(0, 1), (2, 1)],
            "metadata": {
                "turn": np.int32(5),
                "walls_remaining": [np.int8(3), np.int8(7)],
                "scores": np.array([100, 85], dtype=np.float32),
            },
            "game_stats": {
                "moves_count": np.int64(25),
                "time_elapsed": np.float64(120.5),
                "game_over": np.bool_(False),
            },
            "history": [
                {"action": np.int32(1), "reward": np.float32(0.1)},
                {"action": np.int32(2), "reward": np.float32(-0.05)},
            ]
        }
        
        serialized = self.logger._serialize_observation(complex_observation)
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(serialized)
            # Test that we can load it back
            loaded = json.loads(json_str)
        except (TypeError, ValueError) as e:
            self.fail(f"Complex observation serialization failed: {e}")
        
        # Check structure is preserved
        self.assertIsInstance(serialized["board_state"], list)
        self.assertEqual(len(serialized["board_state"]), 3)
        self.assertEqual(len(serialized["board_state"][0]), 3)
        
        # Check scalar conversions
        self.assertIsInstance(serialized["metadata"]["turn"], int)
        self.assertIsInstance(serialized["game_stats"]["moves_count"], int)
        self.assertIsInstance(serialized["game_stats"]["time_elapsed"], float)
        self.assertIsInstance(serialized["game_stats"]["game_over"], bool)
        
        # Check nested array conversions
        self.assertIsInstance(serialized["metadata"]["scores"], list)
        self.assertEqual(len(serialized["metadata"]["scores"]), 2)

    def test_episode_logger_integration(self):
        """Test that episode logger properly handles NumPy arrays in observations."""
        # Create observations with NumPy arrays
        observation_1 = {
            "board": np.array([[1, 0], [0, 1]]),
            "player": np.int32(0),
            "score": np.float64(15.5),
        }
        
        next_observation = {
            "board": np.array([[1, 1], [0, 1]]),
            "player": np.int32(1),
            "score": np.float64(20.0),
        }
        
        # Log a step
        self.logger.log_step(
            observation=observation_1,
            action=5,
            reward=1.0,
            next_observation=next_observation,
            done=False
        )
        
        # Save the episode
        filepath = self.logger.save(tag="numpy_test", include_metadata=True)
        
        # Verify file was created and is valid JSON
        self.assertTrue(os.path.exists(filepath))
        
        with open(filepath, 'r') as f:
            loaded_data = json.load(f)
        
        # Check structure
        self.assertIn("metadata", loaded_data)
        self.assertIn("steps", loaded_data)
        self.assertEqual(len(loaded_data["steps"]), 1)
        
        step = loaded_data["steps"][0]
        
        # Check that NumPy arrays were converted to lists
        self.assertIsInstance(step["observation"]["board"], list)
        self.assertIsInstance(step["next_observation"]["board"], list)
        
        # Check that NumPy scalars were converted to Python types
        self.assertIsInstance(step["observation"]["player"], int)
        self.assertIsInstance(step["observation"]["score"], float)

    def test_example_integration_board_state_fix(self):
        """Test that example_integration.py correctly converts board_state to list."""
        try:
            # Create a game instance
            game = QuoridorGame(num_players=2)
            
            # Create observation using the fixed function
            observation = create_game_observation(game)
            
            # Check that board_state is a list, not numpy array
            self.assertIsInstance(observation["board_state"], list)
            
            # Should be JSON serializable
            try:
                json.dumps(observation)
            except (TypeError, ValueError):
                self.fail("Observation from create_game_observation is not JSON serializable")
            
            # Check structure
            self.assertIsInstance(observation["player_positions"], list)
            self.assertIsInstance(observation["current_player"], int)
            
        except ImportError:
            self.skipTest("QuoridorGame not available for testing")

    def test_recursive_serialization_edge_cases(self):
        """Test edge cases in recursive serialization."""
        edge_cases = [
            # Empty structures
            {"empty_list": [], "empty_dict": {}},
            
            # Nested empty structures
            {"nested": {"empty": [], "also_empty": {}}},
            
            # Mixed types
            {"mixed": [1, "string", np.int32(42), [np.float32(3.14)]]},
            
            # Deeply nested
            {"level1": {"level2": {"level3": {"array": np.array([1, 2, 3])}}}},
            
            # None values
            {"none_value": None, "array_with_none": [None, np.int32(1)]},
        ]
        
        for i, case in enumerate(edge_cases):
            with self.subTest(case_num=i):
                serialized = self.logger._serialize_observation(case)
                
                # Should be JSON serializable
                try:
                    json.dumps(serialized)
                except (TypeError, ValueError):
                    self.fail(f"Edge case {i} is not JSON serializable")

    def test_large_array_serialization_performance(self):
        """Test serialization of large NumPy arrays."""
        # Create a reasonably large array
        large_array = np.random.rand(100, 100)
        
        # Time the serialization (should complete in reasonable time)
        import time
        start_time = time.time()
        
        serialized = self.logger._serialize_observation(large_array)
        
        end_time = time.time()
        serialization_time = end_time - start_time
        
        # Should complete in under 1 second for this size
        self.assertLess(serialization_time, 1.0)
        
        # Should be a list
        self.assertIsInstance(serialized, list)
        self.assertEqual(len(serialized), 100)
        self.assertEqual(len(serialized[0]), 100)

    def test_episode_logger_streaming_with_numpy(self):
        """Test that streaming mode properly handles NumPy arrays."""
        # Create logger with small memory limit to trigger streaming
        streaming_logger = EpisodeLogger(
            log_dir=self.test_dir,
            streaming=True,
            max_memory_steps=5
        )
        
        # Log multiple steps with NumPy arrays
        for i in range(10):
            observation = {
                "step": i,
                "board": np.random.rand(3, 3),
                "player": np.int32(i % 2),
            }
            
            streaming_logger.log_step(
                observation=observation,
                action=i,
                reward=float(i),
                next_observation=observation,
                done=(i == 9)
            )
        
        # Save and verify
        filepath = streaming_logger.save(tag="streaming_numpy_test")
        
        # Should be valid JSON
        with open(filepath, 'r') as f:
            loaded_data = json.load(f)
        
        # Check all steps were saved
        steps = loaded_data.get("steps", loaded_data)
        self.assertEqual(len(steps), 10)
        
        # Check NumPy arrays were properly serialized in all steps
        for step in steps:
            self.assertIsInstance(step["observation"]["board"], list)
            self.assertIsInstance(step["observation"]["player"], int)

    def test_backwards_compatibility(self):
        """Test that the serialization fixes maintain backwards compatibility."""
        # Test with regular Python objects (should work as before)
        regular_observation = {
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "int": 42,
            "float": 3.14,
            "bool": True,
            "string": "test",
            "none": None,
        }
        
        serialized = self.logger._serialize_observation(regular_observation)
        
        # Should be identical to input for regular Python objects
        self.assertEqual(serialized, regular_observation)
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(serialized)
            reloaded = json.loads(json_str)
            self.assertEqual(reloaded, regular_observation)
        except (TypeError, ValueError):
            self.fail("Regular Python objects should remain JSON serializable")


if __name__ == '__main__':
    unittest.main()