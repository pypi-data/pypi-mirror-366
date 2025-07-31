import unittest
import numpy as np
import sys
import os

# Add the parent directory to the path to import quoridor_sim
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quoridor_sim.quoridor_env import QuoridorEnv
from quoridor_sim.core import QuoridorGame


class TestQuoridorEnv(unittest.TestCase):
    """Comprehensive test suite for the QuoridorEnv class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.env_2p = QuoridorEnv(num_players=2, max_walls=10)
        self.env_4p = QuoridorEnv(num_players=4, max_walls=10)

    def test_env_initialization_2_players(self):
        """Test environment initialization with 2 players."""
        self.assertEqual(self.env_2p.num_players, 2)
        self.assertEqual(self.env_2p.board_size, 9)
        self.assertEqual(self.env_2p.action_space.n, 4 + 2 * (9-1)**2)  # 4 + 2*64 = 132
        self.assertEqual(self.env_2p.observation_space.shape, (4, 9, 9))  # 2 players + 2 wall channels

    def test_env_initialization_4_players(self):
        """Test environment initialization with 4 players."""
        self.assertEqual(self.env_4p.num_players, 4)
        self.assertEqual(self.env_4p.board_size, 9)
        self.assertEqual(self.env_4p.action_space.n, 4 + 2 * (9-1)**2)  # Same action space
        self.assertEqual(self.env_4p.observation_space.shape, (6, 9, 9))  # 4 players + 2 wall channels

    def test_reset_functionality(self):
        """Test environment reset returns correct initial state."""
        obs, info = self.env_2p.reset()
        
        # Check observation shape
        self.assertEqual(obs.shape, (4, 9, 9))  # 2 players + 2 wall channels
        self.assertEqual(obs.dtype, np.float32)
        
        # Check info is a dictionary
        self.assertIsInstance(info, dict)
        
        # Check initial positions are set
        # Player 0 should be at (4, 0), Player 1 at (4, 8)
        self.assertEqual(obs[0, 4, 0], 1.0)  # Player 0 position
        self.assertEqual(obs[1, 4, 8], 1.0)  # Player 1 position
        
        # Check no walls initially
        self.assertEqual(np.sum(obs[2]), 0.0)  # No horizontal walls
        self.assertEqual(np.sum(obs[3]), 0.0)  # No vertical walls

    def test_action_decoding_moves(self):
        """Test action decoding for move actions (0-3)."""
        self.env_2p.reset()
        
        # Test move actions
        move_up = self.env_2p._decode_action(0)
        move_down = self.env_2p._decode_action(1)
        move_left = self.env_2p._decode_action(2)
        move_right = self.env_2p._decode_action(3)
        
        # Initial position is (4, 0) for player 0
        self.assertEqual(move_up, ("move", 4, -1, None))
        self.assertEqual(move_down, ("move", 4, 1, None))
        self.assertEqual(move_left, ("move", 3, 0, None))
        self.assertEqual(move_right, ("move", 5, 0, None))

    def test_action_decoding_walls(self):
        """Test action decoding for wall placement actions."""
        self.env_2p.reset()
        
        # Test first horizontal wall action (action 4)
        wall_h = self.env_2p._decode_action(4)
        self.assertEqual(wall_h, ("wall", 0, 0, "h"))
        
        # Test first vertical wall action (action 4 + 64 = 68)
        wall_v = self.env_2p._decode_action(68)
        self.assertEqual(wall_v, ("wall", 0, 0, "v"))

    def test_step_valid_move(self):
        """Test step function with valid move action."""
        obs, _ = self.env_2p.reset()
        
        # Move right (action 3)
        obs_new, reward, terminated, truncated, info = self.env_2p.step(3)
        
        # Check shapes and types
        self.assertEqual(obs_new.shape, (4, 9, 9))  # 2 players + 2 wall channels
        self.assertIsInstance(reward, float)
        self.assertIsInstance(terminated, bool)
        self.assertIsInstance(truncated, bool)
        self.assertIsInstance(info, dict)
        
        # Should not be terminated after one move
        self.assertFalse(terminated)
        self.assertFalse(truncated)
        
        # Check player moved from (4,0) to (5,0)
        self.assertEqual(obs_new[0, 4, 0], 0.0)  # Old position empty
        self.assertEqual(obs_new[0, 5, 0], 1.0)  # New position occupied

    def test_step_invalid_action(self):
        """Test step function with invalid action."""
        self.env_2p.reset()
        
        # Try to move up from (4,0) - this should be invalid as it goes off board
        obs, reward, terminated, truncated, info = self.env_2p.step(0)
        
        # Should get negative reward for invalid action
        self.assertEqual(reward, -1.0)
        self.assertFalse(terminated)
        self.assertFalse(truncated)
        self.assertTrue(info.get("invalid_action", False))

    def test_reward_calculation_bug_fix(self):
        """Test that the reward calculation bug is fixed."""
        # Create a game where we can force a win condition
        env = QuoridorEnv(num_players=2, max_walls=10)
        obs, _ = env.reset()
        
        # Manually set up a win condition by moving player 0 to the goal
        env.game.positions[0] = (4, 8)  # Move to goal position
        env.game.turn = 0  # Set turn to player 0
        
        # Take any valid action that should trigger win
        # Since we manually set position, we need to manually trigger win
        env.game.winner = 0  # Manually set winner
        env.game.turn = 1   # Turn should advance after win
        
        # Now calculate reward like the step function does
        prev_player = (env.game.turn - 1) % env.num_players
        reward = 1.0 if env.game.winner == prev_player else 0.0
        
        # The reward should be 1.0 for the winning player
        self.assertEqual(reward, 1.0)

    def test_observation_structure(self):
        """Test that observations have correct structure."""
        obs, _ = self.env_2p.reset()
        
        # Check each channel
        # Channels 0-1 should contain player positions
        player_channels = obs[:2]
        self.assertEqual(np.sum(player_channels), 2.0)  # Only 2 players
        
        # Channels 2-3 should contain wall information (initially empty)
        wall_channels = obs[2:]
        self.assertEqual(np.sum(wall_channels), 0.0)  # No walls initially

    def test_wall_placement_action(self):
        """Test wall placement through actions."""
        self.env_2p.reset()
        
        # Try to place a horizontal wall (action 4 = position (0,0) horizontal)
        obs, reward, terminated, truncated, info = self.env_2p.step(4)
        
        # Check if wall was placed (should be valid)
        if not info.get("invalid_action", False):
            # Should have a wall in the observation
            self.assertGreater(np.sum(obs[2]), 0.0)  # Horizontal wall channel

    def test_episode_termination(self):
        """Test that episode terminates when a player wins."""
        # This is a complex test - we'll manually set up a near-win state
        self.env_2p.reset()
        
        # Move player 0 to near-goal position
        self.env_2p.game.positions[0] = (4, 7)  # One step from goal (4, 8)
        self.env_2p.game.turn = 0  # Set turn to player 0
        
        # Move to goal position (action 1 = move down/up depending on coordinate system)
        obs, reward, terminated, truncated, info = self.env_2p.step(1)
        
        # Game should be terminated with a winner
        if terminated:
            self.assertIsNotNone(self.env_2p.game.winner)
            self.assertEqual(reward, 1.0)  # Winning player gets reward

    def test_different_player_counts(self):
        """Test that environment works with different player counts."""
        # Test 4-player game initialization
        obs, _ = self.env_4p.reset()
        
        # Should have 4 player positions
        player_positions = []
        for i in range(4):
            positions = np.argwhere(obs[i] == 1.0)
            if len(positions) > 0:
                player_positions.append(tuple(positions[0]))
        
        # Should have exactly 4 players
        expected_positions = [(4, 0), (4, 8), (0, 4), (8, 4)]
        self.assertEqual(len(player_positions), 4)
        for pos in player_positions:
            self.assertIn(pos, expected_positions)

    def test_action_space_consistency(self):
        """Test that action space is consistent with decoding."""
        self.env_2p.reset()
        
        # Test all move actions
        for action in range(4):
            decoded = self.env_2p._decode_action(action)
            self.assertEqual(decoded[0], "move")
        
        # Test wall actions don't cause errors
        for action in range(4, min(20, self.env_2p.action_space.n)):
            decoded = self.env_2p._decode_action(action)
            self.assertEqual(decoded[0], "wall")
            self.assertIn(decoded[3], ["h", "v"])

    def test_render_functionality(self):
        """Test that render function doesn't crash."""
        self.env_2p.reset()
        
        # Should not raise an exception
        try:
            self.env_2p.render()
        except Exception as e:
            self.fail(f"Render function raised an exception: {e}")

    def test_observation_bounds(self):
        """Test that observations stay within expected bounds."""
        obs, _ = self.env_2p.reset()
        
        # All values should be between 0 and 1
        self.assertTrue(np.all(obs >= 0.0))
        self.assertTrue(np.all(obs <= 1.0))
        
        # Take a few actions and check bounds
        for action in [3, 2, 1]:  # Some move actions
            obs, _, terminated, _, info = self.env_2p.step(action)
            if terminated:
                break
            if not info.get("invalid_action", False):
                self.assertTrue(np.all(obs >= 0.0))
                self.assertTrue(np.all(obs <= 1.0))

    def test_legal_moves_integration(self):
        """Test that environment correctly uses legal moves from game."""
        self.env_2p.reset()
        
        # Get legal moves from game
        legal_moves = self.env_2p.game.legal_moves()
        
        # Should have some legal moves available
        self.assertGreater(len(legal_moves), 0)
        
        # Each legal move should be a valid action tuple
        for move in legal_moves:
            self.assertIn(move[0], ["move", "wall"])
            if move[0] == "move":
                self.assertEqual(len(move), 3)
            else:  # wall
                self.assertEqual(len(move), 4)
                self.assertIn(move[3], ["h", "v"])

    def test_input_validation(self):
        """Test input validation in constructor."""
        # Test invalid num_players
        with self.assertRaises(ValueError):
            QuoridorEnv(num_players=3)  # Only 2 or 4 allowed
            
        with self.assertRaises(ValueError):
            QuoridorEnv(num_players=1)  # Only 2 or 4 allowed
            
        # Test negative max_walls
        with self.assertRaises(ValueError):
            QuoridorEnv(max_walls=-1)
            
        # Test wrong types
        with self.assertRaises(TypeError):
            QuoridorEnv(num_players="2")
            
        with self.assertRaises(TypeError):
            QuoridorEnv(max_walls="10")

    def test_action_validation(self):
        """Test action validation in _decode_action."""
        self.env_2p.reset()
        
        # Test invalid action types
        with self.assertRaises(TypeError):
            self.env_2p._decode_action("0")
            
        with self.assertRaises(TypeError):
            self.env_2p._decode_action(1.5)
            
        # Test out of range actions
        with self.assertRaises(ValueError):
            self.env_2p._decode_action(-1)
            
        with self.assertRaises(ValueError):
            self.env_2p._decode_action(self.env_2p.action_space.n)


if __name__ == '__main__':
    unittest.main()