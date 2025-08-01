#!/usr/bin/env python3
"""
Test script to verify NumPy serialization fixes work with complex game states.
This script tests the fixes in example_integration.py and episode_logger.py.
"""

import sys
import os
import json
import tempfile
import numpy as np

# Add the current directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(__file__))

try:
    from quoridor_sim.core import QuoridorGame
    from quoridor_sim.episode_logger import EpisodeLogger
    from example_integration import create_game_observation, play_random_game
    ALL_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    ALL_MODULES_AVAILABLE = False


def test_basic_numpy_serialization():
    """Test basic NumPy array and scalar serialization."""
    print("Testing basic NumPy serialization...")
    
    test_dir = tempfile.mkdtemp()
    logger = EpisodeLogger(log_dir=test_dir)
    
    # Test various NumPy types
    test_data = {
        "int_array": np.array([1, 2, 3, 4]),
        "float_array": np.array([1.1, 2.2, 3.3]),
        "2d_array": np.array([[1, 2], [3, 4]]),
        "bool_array": np.array([True, False, True]),
        "int_scalar": np.int32(42),
        "float_scalar": np.float64(3.14159),
        "bool_scalar": np.bool_(True),
    }
    
    try:
        serialized = logger._serialize_observation(test_data)
        
        # Verify all numpy arrays became lists
        assert isinstance(serialized["int_array"], list), "int_array should be list"
        assert isinstance(serialized["float_array"], list), "float_array should be list"
        assert isinstance(serialized["2d_array"], list), "2d_array should be list"
        assert isinstance(serialized["bool_array"], list), "bool_array should be list"
        
        # Verify numpy scalars became Python types
        assert isinstance(serialized["int_scalar"], int), "int_scalar should be int"
        assert isinstance(serialized["float_scalar"], float), "float_scalar should be float"
        assert isinstance(serialized["bool_scalar"], bool), "bool_scalar should be bool"
        
        # Test JSON serialization
        json_str = json.dumps(serialized)
        reloaded = json.loads(json_str)
        
        print("✓ Basic NumPy serialization works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Basic NumPy serialization failed: {e}")
        return False
    
    finally:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_game_observation_serialization():
    """Test that game observations serialize correctly."""
    if not ALL_MODULES_AVAILABLE:
        print("Skipping game observation test - modules not available")
        return True
    
    print("Testing game observation serialization...")
    
    try:
        # Create a game and get observation
        game = QuoridorGame(num_players=2)
        observation = create_game_observation(game)
        
        # Verify board_state is a list (the main fix)
        assert isinstance(observation["board_state"], list), "board_state should be list"
        
        # Test JSON serialization
        json_str = json.dumps(observation)
        reloaded = json.loads(json_str)
        
        # Verify structure is preserved
        assert "board_state" in reloaded, "board_state should be in reloaded data"
        assert "player_positions" in reloaded, "player_positions should be in reloaded data"
        assert "current_player" in reloaded, "current_player should be in reloaded data"
        assert "winner" in reloaded, "winner should be in reloaded data"
        
        print("✓ Game observation serialization works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Game observation serialization failed: {e}")
        return False


def test_episode_logger_with_game():
    """Test episode logger with actual game data."""
    if not ALL_MODULES_AVAILABLE:
        print("Skipping episode logger game test - modules not available")
        return True
    
    print("Testing episode logger with game data...")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        logger = EpisodeLogger(log_dir=test_dir)
        
        # Play a short game and log it
        game = QuoridorGame(num_players=2)
        
        for i in range(5):  # Short game
            # Get current observation
            current_obs = create_game_observation(game)
            
            # Get legal actions and choose first one
            legal_actions = game.legal_moves()
            if not legal_actions:
                break
                
            action = legal_actions[0]
            
            # Take action
            game.step(action)
            
            # Get next observation
            next_obs = create_game_observation(game)
            
            # Log the step
            logger.log_step(
                observation=current_obs,
                action=action,
                reward=0.1,
                next_observation=next_obs,
                done=game.winner is not None
            )
            
            if game.winner is not None:
                break
        
        # Save episode
        filepath = logger.save(tag="serialization_test", include_metadata=True)
        
        # Verify file was created and is valid JSON
        assert os.path.exists(filepath), "Episode file should exist"
        
        with open(filepath, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify structure
        assert "metadata" in loaded_data, "Metadata should be present"
        assert "steps" in loaded_data, "Steps should be present"
        assert len(loaded_data["steps"]) > 0, "Should have at least one step"
        
        # Verify each step has properly serialized observations
        for step in loaded_data["steps"]:
            assert isinstance(step["observation"]["board_state"], list), "board_state should be list"
            assert isinstance(step["next_observation"]["board_state"], list), "next_observation board_state should be list"
        
        print("✓ Episode logger with game data works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Episode logger with game data failed: {e}")
        return False
    
    finally:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_complex_nested_structures():
    """Test serialization of complex nested structures with NumPy arrays."""
    print("Testing complex nested structure serialization...")
    
    test_dir = tempfile.mkdtemp()
    logger = EpisodeLogger(log_dir=test_dir)
    
    # Create a complex observation similar to what a real RL environment might produce
    complex_obs = {
        "board": {
            "state": np.array([[1, 0, 2], [0, 1, 0], [2, 0, 1]]),
            "walls": {
                "horizontal": np.array([[True, False], [False, True]]),
                "vertical": np.array([[False, True], [True, False]]),
            }
        },
        "players": [
            {
                "id": np.int32(0),
                "position": np.array([0, 1]),
                "walls_remaining": np.int8(10),
                "score": np.float32(150.5),
            },
            {
                "id": np.int32(1),
                "position": np.array([2, 1]),
                "walls_remaining": np.int8(8),
                "score": np.float32(130.2),
            }
        ],
        "metadata": {
            "turn": np.int64(25),
            "time_elapsed": np.float64(125.5),
            "game_over": np.bool_(False),
            "history": [
                {"action": np.int32(1), "reward": np.float32(0.1)},
                {"action": np.int32(2), "reward": np.float32(-0.05)},
            ]
        }
    }
    
    try:
        serialized = logger._serialize_observation(complex_obs)
        
        # Test JSON serialization
        json_str = json.dumps(serialized)
        reloaded = json.loads(json_str)
        
        # Verify numpy arrays became lists
        assert isinstance(reloaded["board"]["state"], list), "board state should be list"
        assert isinstance(reloaded["board"]["walls"]["horizontal"], list), "horizontal walls should be list"
        assert isinstance(reloaded["board"]["walls"]["vertical"], list), "vertical walls should be list"
        
        # Verify numpy scalars became Python types
        assert isinstance(reloaded["players"][0]["id"], int), "player id should be int"
        assert isinstance(reloaded["players"][0]["score"], float), "player score should be float"
        assert isinstance(reloaded["metadata"]["turn"], int), "turn should be int"
        assert isinstance(reloaded["metadata"]["game_over"], bool), "game_over should be bool"
        
        # Verify structure is preserved
        assert len(reloaded["players"]) == 2, "Should have 2 players"
        assert len(reloaded["metadata"]["history"]) == 2, "Should have 2 history items"
        
        print("✓ Complex nested structure serialization works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Complex nested structure serialization failed: {e}")
        return False
    
    finally:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_integration_example():
    """Test the example_integration.py script functionality."""
    if not ALL_MODULES_AVAILABLE:
        print("Skipping integration example test - modules not available")
        return True
    
    print("Testing integration example functionality...")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        logger = EpisodeLogger(log_dir=test_dir, max_memory_steps=50)
        
        # Play a very short random game
        stats = play_random_game(logger, num_players=2, max_moves=10)
        
        # Verify stats were returned
        assert isinstance(stats, dict), "Stats should be dictionary"
        
        # Save the episode
        filepath = logger.save(tag="integration_test", include_metadata=True)
        
        # Verify file was created and is valid JSON
        assert os.path.exists(filepath), "Episode file should exist"
        
        with open(filepath, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify the data structure
        assert "metadata" in loaded_data, "Metadata should be present"
        assert "steps" in loaded_data, "Steps should be present"
        
        print("✓ Integration example functionality works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Integration example functionality failed: {e}")
        return False
    
    finally:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def main():
    """Run all tests to verify NumPy serialization fixes."""
    print("=" * 60)
    print("Testing NumPy Serialization Fixes")
    print("=" * 60)
    
    tests = [
        test_basic_numpy_serialization,
        test_game_observation_serialization,
        test_episode_logger_with_game,
        test_complex_nested_structures,
        test_integration_example,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All NumPy serialization fixes are working correctly!")
        return True
    else:
        print("❌ Some tests failed. Please check the fixes.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)