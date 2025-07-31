import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any

from .core import QuoridorGame

# Constants
NUM_MOVE_ACTIONS = 4
WALL_CHANNELS = 2  # horizontal and vertical walls


class QuoridorEnv(gym.Env):
    """
    Gymnasium-compatible environment for the Quoridor board game.

    Observations:
        - Shape: (num_players + 2, board_size, board_size)
        - Channels:
            0 to num_players-1: Player positions (one per player)
            num_players: Horizontal wall placements
            num_players+1: Vertical wall placements

    Actions:
        - Discrete values:
            0-3: Move (up, down, left, right)
            4 to 4 + (board_size - 1)**2 - 1: Horizontal wall placements
            Remaining: Vertical wall placements
    """
    metadata = {"render_modes": ["human"], "render_fps": 5}

    def __init__(self, num_players: int = 2, max_walls: int = 10) -> None:
        """
        Initialize the Quoridor environment.

        Parameters
        ----------
        num_players : int
            Number of players (must be 2 or 4).
        max_walls : int
            Maximum number of walls per player.
            
        Raises
        ------
        ValueError
            If num_players is not 2 or 4, or if max_walls is negative.
        TypeError
            If parameters are not integers.
        """
        # Input validation
        if not isinstance(num_players, int):
            raise TypeError("num_players must be an integer")
        if not isinstance(max_walls, int):
            raise TypeError("max_walls must be an integer")
        if num_players not in [2, 4]:
            raise ValueError("num_players must be 2 or 4")
        if max_walls < 0:
            raise ValueError("max_walls must be non-negative")
            
        super().__init__()
        self.game = QuoridorGame(num_players=num_players, max_walls=max_walls)
        self.num_players = num_players
        self.board_size = self.game.board_size

        # Dynamic observation space based on number of players
        obs_channels = self.num_players + WALL_CHANNELS
        self.action_space = spaces.Discrete(NUM_MOVE_ACTIONS + 2 * (self.board_size - 1) ** 2)
        self.observation_space = spaces.Box(
            low=0, high=1,
            shape=(obs_channels, self.board_size, self.board_size),
            dtype=np.float32
        )
        
        # Pre-allocate observation array for performance
        self._obs_array = np.zeros(self.observation_space.shape, dtype=np.float32)

    def reset(
        self, 
        seed: Optional[int] = None, 
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to the initial state.

        Returns
        -------
        observation : np.ndarray
            The initial observation.
        info : dict
            Additional info (empty by default).
        """
        super().reset(seed=seed)
        self.game.reset()
        obs = self._get_obs()
        return obs, {}

    def step(
        self, 
        action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Apply an action to the environment.

        Parameters
        ----------
        action : int
            Discrete action index.

        Returns
        -------
        observation : np.ndarray
            New game state.
        reward : float
            Reward for this step.
        terminated : bool
            Whether the game has ended.
        truncated : bool
            Always False in this implementation.
        info : dict
            Additional info such as invalid action flag.
        """
        legal_actions = self.game.legal_moves()
        action_obj = self._decode_action(action)

        if action_obj not in legal_actions:
            reward = -1.0
            terminated = False
            truncated = False
            info = {"invalid_action": True}
            obs = self._get_obs()
            return obs, reward, terminated, truncated, info

        self.game.step(action_obj)

        obs = self._get_obs()
        # Fix: When a player wins, turn has already advanced, so we need the previous player
        prev_player = (self.game.turn - 1) % self.num_players
        reward = 1.0 if self.game.winner == prev_player else 0.0
        terminated = self.game.winner is not None
        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self) -> None:
        """
        Render the current state to the console.
        """
        print("Positions:", self.game.positions)
        print("Horizontal walls:", self.game.horiz_walls)
        print("Vertical walls:", self.game.vert_walls)

    def _get_obs(self) -> np.ndarray:
        """
        Convert internal game state to observation tensor.

        Returns
        -------
        obs : np.ndarray
            Observation tensor of shape (num_players + 2, board_size, board_size).
        """
        state = self.game.get_state()
        
        # Clear the pre-allocated array for efficiency
        self._obs_array.fill(0.0)

        # Set player positions
        for idx, (x, y) in enumerate(state["positions"]):
            if idx < self.num_players:  # Only set positions for actual players
                self._obs_array[idx, x, y] = 1.0

        # Set wall positions in the last two channels
        wall_channel_offset = self.num_players
        for x, y in state["horiz_walls"]:
            self._obs_array[wall_channel_offset, x, y] = 1.0

        for x, y in state["vert_walls"]:
            self._obs_array[wall_channel_offset + 1, x, y] = 1.0

        return self._obs_array.copy()

    def _decode_action(self, action: int) -> Tuple[str, int, int, Optional[str]]:
        """
        Map a discrete action index to a game action tuple.

        Parameters
        ----------
        action : int
            Discrete action index.

        Returns
        -------
        action_tuple : Tuple[str, int, int, Optional[str]]
            Game action in the form:
                - ("move", x, y, None) for move actions
                - ("wall", x, y, orientation) for wall actions
                
        Raises
        ------
        ValueError
            If action is out of valid range.
        TypeError
            If action is not an integer.
        """
        if not isinstance(action, int):
            raise TypeError("Action must be an integer")
        if not (0 <= action < self.action_space.n):
            raise ValueError(f"Action {action} is out of range [0, {self.action_space.n})")
            
        if action < NUM_MOVE_ACTIONS:
            # Move actions: up, down, left, right
            dx, dy = [(0, -1), (0, 1), (-1, 0), (1, 0)][action]
            x, y = self.game.positions[self.game.turn]
            new_x, new_y = x + dx, y + dy
            
            # Bounds checking for move actions (let the game handle invalid moves)
            return ("move", new_x, new_y, None)
        else:
            # Wall actions
            i = action - NUM_MOVE_ACTIONS
            wall_positions_per_orientation = (self.board_size - 1) ** 2
            
            if i < wall_positions_per_orientation:
                # Horizontal wall
                x, y = divmod(i, self.board_size - 1)
                orientation = "h"
            else:
                # Vertical wall
                i -= wall_positions_per_orientation
                x, y = divmod(i, self.board_size - 1) 
                orientation = "v"
                
            return ("wall", x, y, orientation)


# Register environments with Gymnasium
def register_environments():
    """Register QuoridorEnv environments with Gymnasium."""
    try:
        gym.register(
            id='Quoridor-v0',
            entry_point='quoridor_sim.quoridor_env:QuoridorEnv',
            kwargs={'num_players': 2, 'max_walls': 10},
            max_episode_steps=200,
            reward_threshold=1.0,
        )
        
        gym.register(
            id='Quoridor-4p-v0',
            entry_point='quoridor_sim.quoridor_env:QuoridorEnv',
            kwargs={'num_players': 4, 'max_walls': 10},
            max_episode_steps=400,
            reward_threshold=1.0,
        )
    except gym.error.Error:
        # Environments already registered
        pass


# Auto-register environments when module is imported
register_environments()
