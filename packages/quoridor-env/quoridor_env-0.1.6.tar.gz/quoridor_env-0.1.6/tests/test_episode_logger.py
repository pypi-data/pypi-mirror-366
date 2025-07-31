import unittest
import json
import os
import tempfile
import shutil
import numpy as np
import sys
from unittest.mock import patch, mock_open

# Add the parent directory to the path to import quoridor_sim
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quoridor_sim.episode_logger import EpisodeLogger


class TestEpisodeLogger(unittest.TestCase):
    """Comprehensive test suite for the EpisodeLogger class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test logs
        self.test_dir = tempfile.mkdtemp()
        self.logger = EpisodeLogger(log_dir=self.test_dir)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_logger_initialization(self):
        """Test logger initialization with different directories."""
        # Test default directory with unique name to avoid conflicts
        unique_default_dir = tempfile.mkdtemp(prefix="test_logs_")
        default_logger = EpisodeLogger(log_dir=unique_default_dir)
        self.assertEqual(default_logger.log_dir, unique_default_dir)
        self.assertTrue(os.path.exists(unique_default_dir))
        
        # Test custom directory
        custom_logger = EpisodeLogger(log_dir=self.test_dir)
        self.assertEqual(custom_logger.log_dir, self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
        
        # Test that episode starts empty
        self.assertEqual(len(custom_logger.episode), 0)
        
        # Clean up unique default logs directory
        if os.path.exists(unique_default_dir):
            shutil.rmtree(unique_default_dir)

    def test_serialize_observation_numpy_array(self):
        """Test observation serialization with numpy arrays."""
        obs = np.array([1, 2, 3, 4])
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, [1, 2, 3, 4])
        self.assertIsInstance(result, list)

    def test_serialize_observation_list(self):
        """Test observation serialization with lists."""
        obs = [1, 2, 3, 4]
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, [1, 2, 3, 4])
        self.assertIsInstance(result, list)

    def test_serialize_observation_tuple(self):
        """Test observation serialization with tuples."""
        obs = (1, 2, 3, 4)
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, [1, 2, 3, 4])
        self.assertIsInstance(result, list)

    def test_serialize_observation_scalar(self):
        """Test observation serialization with scalar values."""
        obs = 42
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, 42)
        
        obs = 3.14
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, 3.14)
        
        obs = "test"
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, "test")

    def test_serialize_observation_custom_object(self):
        """Test observation serialization with objects that don't have tolist."""
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        obs = CustomObject(42)
        result = self.logger._serialize_observation(obs)
        self.assertEqual(result, obs)  # Should return object as-is

    def test_log_step_basic(self):
        """Test basic step logging functionality."""
        observation = [1, 2, 3]
        action = 0
        reward = 1.0
        next_observation = [4, 5, 6]
        done = False
        
        self.logger.log_step(observation, action, reward, next_observation, done)
        
        self.assertEqual(len(self.logger.episode), 1)
        step = self.logger.episode[0]
        
        self.assertEqual(step["observation"], [1, 2, 3])
        self.assertEqual(step["action"], 0)
        self.assertEqual(step["reward"], 1.0)
        self.assertEqual(step["next_observation"], [4, 5, 6])
        self.assertEqual(step["done"], False)

    def test_log_step_multiple_steps(self):
        """Test logging multiple steps."""
        for i in range(5):
            observation = [i]
            action = i
            reward = float(i)
            next_observation = [i + 1]
            done = (i == 4)
            
            self.logger.log_step(observation, action, reward, next_observation, done)
        
        self.assertEqual(len(self.logger.episode), 5)
        
        # Check last step
        last_step = self.logger.episode[-1]
        self.assertEqual(last_step["observation"], [4])
        self.assertEqual(last_step["action"], 4)
        self.assertEqual(last_step["reward"], 4.0)
        self.assertEqual(last_step["next_observation"], [5])
        self.assertEqual(last_step["done"], True)

    def test_log_step_numpy_observations(self):
        """Test logging steps with numpy array observations."""
        observation = np.array([[1, 2], [3, 4]])
        action = "up"
        reward = -0.1
        next_observation = np.array([[5, 6], [7, 8]])
        done = True
        
        self.logger.log_step(observation, action, reward, next_observation, done)
        
        step = self.logger.episode[0]
        self.assertEqual(step["observation"], [[1, 2], [3, 4]])
        self.assertEqual(step["action"], "up")
        self.assertEqual(step["reward"], -0.1)
        self.assertEqual(step["next_observation"], [[5, 6], [7, 8]])
        self.assertEqual(step["done"], True)

    def test_save_without_tag(self):
        """Test saving episode without tag."""
        # Log some steps
        self.logger.log_step([1], 0, 1.0, [2], False)
        self.logger.log_step([2], 1, 2.0, [3], True)
        
        # Save episode
        filepath = self.logger.save()
        
        # Verify file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Verify filename format
        filename = os.path.basename(filepath)
        self.assertTrue(filename.startswith("episode_"))
        self.assertTrue(filename.endswith(".json"))
        
        # Verify episode was cleared
        self.assertEqual(len(self.logger.episode), 0)
        
        # Verify file content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["observation"], [1])
        self.assertEqual(data[1]["done"], True)

    def test_save_with_tag(self):
        """Test saving episode with tag."""
        # Log a step
        self.logger.log_step([1], 0, 1.0, [2], False)
        
        # Save with tag
        filepath = self.logger.save(tag="test_episode")
        
        # Verify filename includes tag
        filename = os.path.basename(filepath)
        self.assertTrue("test_episode" in filename)
        self.assertTrue(filename.startswith("episode_test_episode_"))

    def test_save_tag_sanitization(self):
        """Test that tags are properly sanitized."""
        # Log a step
        self.logger.log_step([1], 0, 1.0, [2], False)
        
        # Save with problematic tag
        filepath = self.logger.save(tag="test/episode..with*special?chars")
        
        # Verify filename is sanitized
        filename = os.path.basename(filepath)
        self.assertNotIn("/", filename)
        self.assertNotIn("*", filename)
        self.assertNotIn("?", filename)
        self.assertTrue("testepisodewithspecialchars" in filename)

    def test_save_empty_tag(self):
        """Test saving with empty tag."""
        # Log a step
        self.logger.log_step([1], 0, 1.0, [2], False)
        
        # Save with empty tag
        filepath = self.logger.save(tag="")
        
        # Verify filename doesn't include tag
        filename = os.path.basename(filepath)
        self.assertTrue(filename.startswith("episode_"))
        # Should not have double underscore
        self.assertNotIn("episode__", filename)

    def test_save_file_write_error(self):
        """Test save method handles file write errors."""
        # Log a step
        self.logger.log_step([1], 0, 1.0, [2], False)
        
        # Mock file operations to raise IOError
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Disk full")
            
            with self.assertRaises(RuntimeError) as context:
                self.logger.save()
            
            self.assertIn("Failed to save episode", str(context.exception))
            self.assertIn("Disk full", str(context.exception))

    def test_save_permission_error(self):
        """Test save method handles permission errors."""
        # Log a step
        self.logger.log_step([1], 0, 1.0, [2], False)
        
        # Mock file operations to raise PermissionError
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Access denied")
            
            with self.assertRaises(RuntimeError) as context:
                self.logger.save()
            
            self.assertIn("Failed to save episode", str(context.exception))
            self.assertIn("Access denied", str(context.exception))

    def test_load_valid_file(self):
        """Test loading a valid episode file."""
        # Create test data
        test_data = [
            {"observation": [1], "action": 0, "reward": 1.0, "next_observation": [2], "done": False},
            {"observation": [2], "action": 1, "reward": 2.0, "next_observation": [3], "done": True}
        ]
        
        # Write test file
        test_file = os.path.join(self.test_dir, "test_episode.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load and verify
        loaded_data = self.logger.load(test_file)
        self.assertEqual(loaded_data, test_data)
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["action"], 0)
        self.assertEqual(loaded_data[1]["done"], True)

    def test_load_file_not_found(self):
        """Test load method handles missing files."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.json")
        
        with self.assertRaises(RuntimeError) as context:
            self.logger.load(nonexistent_file)
        
        self.assertIn("Failed to load episode", str(context.exception))

    def test_load_invalid_json(self):
        """Test load method handles invalid JSON."""
        # Create invalid JSON file
        invalid_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        with self.assertRaises(ValueError) as context:
            self.logger.load(invalid_file)
        
        self.assertIn("Invalid JSON", str(context.exception))

    def test_load_io_error(self):
        """Test load method handles I/O errors."""
        # Mock file operations to raise IOError
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Read error")
            
            with self.assertRaises(RuntimeError) as context:
                self.logger.load("test.json")
            
            self.assertIn("Failed to load episode", str(context.exception))
            self.assertIn("Read error", str(context.exception))

    def test_save_load_round_trip(self):
        """Test save and load round trip."""
        # Create test episode
        test_steps = [
            ([1, 2], 0, 1.0, [3, 4], False),
            ([3, 4], 1, -1.0, [5, 6], True)
        ]
        
        for obs, action, reward, next_obs, done in test_steps:
            self.logger.log_step(obs, action, reward, next_obs, done)
        
        # Save episode
        filepath = self.logger.save(tag="round_trip_test")
        
        # Load episode
        loaded_data = self.logger.load(filepath)
        
        # Verify data matches
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["observation"], [1, 2])
        self.assertEqual(loaded_data[0]["action"], 0)
        self.assertEqual(loaded_data[1]["reward"], -1.0)
        self.assertEqual(loaded_data[1]["done"], True)

    def test_episode_cleared_after_save(self):
        """Test that episode data is cleared after saving."""
        # Log multiple steps
        for i in range(3):
            self.logger.log_step([i], i, float(i), [i+1], False)
        
        self.assertEqual(len(self.logger.episode), 3)
        
        # Save episode
        self.logger.save()
        
        # Verify episode is cleared
        self.assertEqual(len(self.logger.episode), 0)

    def test_multiple_episodes(self):
        """Test logging and saving multiple episodes."""
        # First episode
        self.logger.log_step([1], 0, 1.0, [2], True)
        filepath1 = self.logger.save(tag="episode1")
        
        # Second episode
        self.logger.log_step([10], 5, 5.0, [20], True)
        filepath2 = self.logger.save(tag="episode2")
        
        # Verify both files exist and contain correct data
        self.assertTrue(os.path.exists(filepath1))
        self.assertTrue(os.path.exists(filepath2))
        
        data1 = self.logger.load(filepath1)
        data2 = self.logger.load(filepath2)
        
        self.assertEqual(data1["steps"][0]["observation"], [1])
        self.assertEqual(data2["steps"][0]["observation"], [10])

    def test_complex_action_types(self):
        """Test logging with complex action types."""
        # Test different action types
        actions = [
            0,                          # int
            3.14,                      # float
            [1, 2, 3],                 # list
            {"move": "up", "force": 1}, # dict
            "jump"                     # string
        ]
        
        for i, action in enumerate(actions):
            self.logger.log_step([i], action, 1.0, [i+1], False)
        
        # Save and load
        filepath = self.logger.save()
        loaded_data = self.logger.load(filepath)
        
        # Verify action types are preserved
        for i, expected_action in enumerate(actions):
            self.assertEqual(loaded_data["steps"][i]["action"], expected_action)

    def test_large_episode_performance(self):
        """Test performance with large episodes."""
        # Log many steps (simulate long episode)
        num_steps = 1000
        
        for i in range(num_steps):
            obs = np.random.rand(10)  # Random 10-element observation
            action = i % 4  # Cycle through 4 actions
            reward = np.random.rand()
            next_obs = np.random.rand(10)
            done = (i == num_steps - 1)
            
            self.logger.log_step(obs, action, reward, next_obs, done)
        
        # Verify all steps logged
        self.assertEqual(len(self.logger.episode), num_steps)
        
        # Save (this tests performance of serialization)
        filepath = self.logger.save(tag="large_episode")
        
        # Verify file size is reasonable (should be > 0)
        file_size = os.path.getsize(filepath)
        self.assertGreater(file_size, 0)
        
        # Load and verify (tests deserialization performance)
        loaded_data = self.logger.load(filepath)
        self.assertEqual(len(loaded_data["steps"]), num_steps)
        self.assertEqual(loaded_data["metadata"]["step_count"], num_steps)

    def test_get_episode_stats(self):
        """Test episode statistics functionality."""
        # Test empty episode
        stats = self.logger.get_episode_stats()
        self.assertEqual(stats["step_count"], 0)
        self.assertEqual(stats["total_reward"], 0.0)
        self.assertFalse(stats["is_complete"])
        
        # Log some steps
        self.logger.log_step([1], 0, 2.5, [2], False)
        self.logger.log_step([2], 1, -1.0, [3], False)
        self.logger.log_step([3], 2, 0.5, [4], True)
        
        stats = self.logger.get_episode_stats()
        self.assertEqual(stats["step_count"], 3)
        self.assertEqual(stats["total_reward"], 2.0)  # 2.5 + (-1.0) + 0.5
        self.assertTrue(stats["is_complete"])
        self.assertIn("duration_seconds", stats)
        self.assertGreater(stats["duration_seconds"], 0)
    
    def test_save_without_metadata(self):
        """Test saving episode without metadata."""
        # Log some steps
        self.logger.log_step([1], 0, 1.0, [2], False)
        self.logger.log_step([2], 1, 2.0, [3], True)
        
        # Save without metadata
        filepath = self.logger.save(include_metadata=False)
        
        # Verify file content (should be just the steps array)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["observation"], [1])
        self.assertEqual(data[1]["done"], True)
    
    def test_performance_warning(self):
        """Test performance warning for large episodes."""
        # Create logger with low max_memory_steps for testing
        small_logger = EpisodeLogger(log_dir=self.test_dir, max_memory_steps=5)
        
        # Log enough steps to trigger warning
        with patch.object(small_logger.logger, 'warning') as mock_warning:
            for i in range(6):
                small_logger.log_step([i], i, 1.0, [i+1], False)
            
            # Verify warning was called
            mock_warning.assert_called_once()
            self.assertIn("performance may be impacted", mock_warning.call_args[0][0])
    
    def test_load_new_format_file(self):
        """Test loading files with new metadata format."""
        # Create test data with metadata
        test_data = {
            "metadata": {
                "step_count": 2,
                "timestamp": "20240101_120000",
                "duration_seconds": 5.5
            },
            "steps": [
                {"observation": [1], "action": 0, "reward": 1.0, "next_observation": [2], "done": False},
                {"observation": [2], "action": 1, "reward": 2.0, "next_observation": [3], "done": True}
            ]
        }
        
        # Write test file
        test_file = os.path.join(self.test_dir, "test_metadata_episode.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load and verify
        loaded_data = self.logger.load(test_file)
        self.assertIn("metadata", loaded_data)
        self.assertIn("steps", loaded_data)
        self.assertEqual(loaded_data["metadata"]["step_count"], 2)
        self.assertEqual(loaded_data["metadata"]["duration_seconds"], 5.5)
        self.assertEqual(len(loaded_data["steps"]), 2)


if __name__ == '__main__':
    unittest.main()