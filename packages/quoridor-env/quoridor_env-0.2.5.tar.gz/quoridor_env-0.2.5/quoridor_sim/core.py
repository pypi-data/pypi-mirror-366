import numpy as np
from collections import deque
from typing import List, Tuple, Dict, Optional, Union
from .board import Board


class QuoridorGame:
    """Quoridor game engine with support for 2-4 players.
    
    Implements core game mechanics including pawn movement, wall placement,
    win condition checking, and turn management. Supports both 2-player
    and 4-player variants.
    
    Attributes:
        board_size (int): Size of the square board (always 9 for Quoridor)
        num_players (int): Number of players (2 or 4)
        max_walls (int): Maximum walls per player (default 10)
        board (Board): Board instance for wall management
        positions (List[Tuple[int, int]]): Current player positions
        walls_remaining (List[int]): Walls remaining for each player
        turn (int): Current player's turn (0-indexed)
        winner (Optional[int]): Winner player index, None if game ongoing
    """
    
    def __init__(self, board_size: int = 9, num_players: int = 2, max_walls: int = 10) -> None:
        """Initialize a new Quoridor game.
        
        Args:
            board_size (int): Size of the square board (must be 9)
            num_players (int): Number of players (must be 2 or 4)
            max_walls (int): Maximum walls per player (default 10)
            
        Raises:
            AssertionError: If board_size is not 9 or num_players not in [2, 4]
        """
        assert board_size == 9, "Only 9x9 board supported in Quoridor rules."
        assert num_players in [2, 4], "Only 2 or 4 players supported."
        self.board_size = board_size
        self.num_players = num_players
        self.max_walls = max_walls
        self.board = Board(size=board_size)

        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state.
        
        Resets player positions, wall counts, board state, turn counter,
        and winner status to start a new game.
        """
        self.positions = self._initial_positions()
        self.walls_remaining = [self.max_walls] * self.num_players
        self.board.reset()
        self.turn = 0
        self.winner = None
        
    @property
    def horiz_walls(self) -> set:
        """Get horizontal walls as a set for backward compatibility.
        
        Returns:
            set: Set of (x, y) tuples representing horizontal wall positions
        """
        """Get horizontal walls as a set for backward compatibility."""
        h_positions, _ = self.board.get_wall_positions()
        return set(h_positions)
        
    @property
    def vert_walls(self) -> set:
        """Get vertical walls as a set for backward compatibility.
        
        Returns:
            set: Set of (x, y) tuples representing vertical wall positions
        """
        """Get vertical walls as a set for backward compatibility."""
        _, v_positions = self.board.get_wall_positions()
        return set(v_positions)

    def _initial_positions(self) -> List[Tuple[int, int]]:
        """Get initial player positions based on number of players.
        
        Returns:
            List[Tuple[int, int]]: List of (x, y) starting positions for each player
        """
        if self.num_players == 2:
            return [(4, 0), (4, 8)]
        else:
            return [(4, 0), (4, 8), (0, 4), (8, 4)]

    def legal_moves(self) -> List[Tuple[str, ...]]:
        """Get all legal actions for the current player.
        
        Returns:
            List[Tuple[str, ...]]: List of legal actions where each action is a tuple:
                - ("move", x, y) for pawn moves
                - ("wall", x, y, orientation) for wall placements
        """
        move_actions = self._legal_pawn_moves(self.turn)
        wall_actions = self._legal_wall_placements()
        return move_actions + wall_actions

    def _legal_pawn_moves(self, player: int) -> List[Tuple[str, int, int]]:
        """Get all legal pawn moves for a specific player.
        
        Implements full Quoridor pawn movement rules including:
        - Basic orthogonal movement to adjacent squares
        - Jumping over adjacent pawns
        - Diagonal jumps when blocked by walls
        
        Args:
            player (int): Player index (0-indexed)
            
        Returns:
            List[Tuple[str, int, int]]: List of ("move", x, y) tuples for legal moves
        """
        x, y = self.positions[player]
        moves = []
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            
            # Check basic bounds
            if not (0 <= nx < self.board_size and 0 <= ny < self.board_size):
                continue
                
            # Check if wall blocks this movement
            if self._is_wall_between((x, y), (nx, ny)):
                continue
            
            # Check if there's a pawn at the target position
            if (nx, ny) in self.positions:
                # There's a pawn - check for jump possibilities
                jump_x, jump_y = nx + dx, ny + dy
                
                # Try straight jump first
                if (0 <= jump_x < self.board_size and 0 <= jump_y < self.board_size and
                    (jump_x, jump_y) not in self.positions and
                    not self._is_wall_between((nx, ny), (jump_x, jump_y))):
                    moves.append(("move", jump_x, jump_y))
                else:
                    # Straight jump blocked - try diagonal jumps
                    for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        # Skip the direction we came from and the blocked direction
                        if (ddx, ddy) == (-dx, -dy) or (ddx, ddy) == (dx, dy):
                            continue
                            
                        diag_x, diag_y = nx + ddx, ny + ddy
                        if (0 <= diag_x < self.board_size and 0 <= diag_y < self.board_size and
                            (diag_x, diag_y) not in self.positions and
                            not self._is_wall_between((nx, ny), (diag_x, diag_y))):
                            moves.append(("move", diag_x, diag_y))
            else:
                # No pawn at target - normal move
                moves.append(("move", nx, ny))
                
        return moves

    def _legal_wall_placements(self) -> List[Tuple[str, int, int, str]]:
        """Get all legal wall placements for the current player.
        
        Checks wall inventory, board validity, and pathfinding constraints.
        
        Returns:
            List[Tuple[str, int, int, str]]: List of ("wall", x, y, orientation) tuples
        """
        actions = []
        if self.walls_remaining[self.turn] <= 0:
            return actions
        for x in range(self.board_size - 1):
            for y in range(self.board_size - 1):
                if ((x, y) not in self.horiz_walls and
                    not self._would_block_all_paths((x, y), orientation="h")):
                    actions.append(("wall", x, y, "h"))
                if ((x, y) not in self.vert_walls and
                    not self._would_block_all_paths((x, y), orientation="v")):
                    actions.append(("wall", x, y, "v"))
        return actions

    def _is_wall_between(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        """Check if there's a wall blocking movement between two adjacent positions.
        
        Args:
            a (Tuple[int, int]): First position (x, y)
            b (Tuple[int, int]): Second position (x, y)
            
        Returns:
            bool: True if a wall blocks movement between the positions
        """
        return self.board.wall_blocks(a, b)

    def _would_block_all_paths(self, position: Tuple[int, int], orientation: str) -> bool:
        """Check if placing a wall would block all paths to goals for any player.
        
        Args:
            position (Tuple[int, int]): Wall position (x, y)
            orientation (str): Wall orientation ('h' or 'v')
            
        Returns:
            bool: True if the wall would block all paths for any player
        """
        x, y = position
        
        # Temporarily place the wall to test
        if not self.board.is_valid_wall(x, y, orientation):
            return True  # Invalid placement is considered blocking
            
        # Create a temporary board with the proposed wall
        temp_board = self.board.clone()
        try:
            temp_board.place_wall(x, y, orientation)
        except ValueError:
            return True  # Invalid wall placement
            
        # Check if all players can still reach their goals
        for player in range(self.num_players):
            if not self._can_reach_goal(player, temp_board):
                return True
                
        return False
        
    def _can_reach_goal(self, player: int, board: Optional['Board'] = None) -> bool:
        """Check if a player can reach their goal using BFS pathfinding.
        
        Args:
            player (int): Player index (0-indexed)
            board (Optional[Board]): Board instance to check, uses current board if None
            
        Returns:
            bool: True if player can reach their goal from current position
        """
        if board is None:
            board = self.board
            
        start = self.positions[player]
        queue = deque([start])
        visited = {start}
        
        while queue:
            x, y = queue.popleft()
            
            # Check if current position satisfies win condition
            if self._check_win_position(player, (x, y)):
                return True
                
            # Explore all adjacent positions
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if not (0 <= nx < self.board_size and 0 <= ny < self.board_size):
                    continue
                    
                # Check if already visited
                if (nx, ny) in visited:
                    continue
                    
                # Check for wall blocking
                if board.wall_blocks((x, y), (nx, ny)):
                    continue
                    
                # Check if position is occupied (simple check)
                if (nx, ny) in self.positions:
                    continue
                    
                visited.add((nx, ny))
                queue.append((nx, ny))
                
        return False
        
    def _check_win_position(self, player: int, position: Tuple[int, int]) -> bool:
        """Check if a position satisfies the win condition for a player.
        
        Args:
            player (int): Player index (0-indexed)
            position (Tuple[int, int]): Position to check (x, y)
            
        Returns:
            bool: True if the position is a winning position for the player
        """
        x, y = position
        if self.num_players == 2:
            return (player == 0 and y == self.board_size - 1) or (player == 1 and y == 0)
        else:
            goals = [(None, self.board_size - 1), (None, 0), (self.board_size - 1, None), (0, None)]
            gx, gy = goals[player]
            return (gx is None or x == gx) and (gy is None or y == gy)

    def step(self, action: Tuple[str, ...]) -> None:
        """Execute an action for the current player.
        
        Args:
            action (Tuple[str, ...]): Action tuple, either ("move", x, y) or ("wall", x, y, orientation)
            
        Raises:
            ValueError: If the action is not legal for the current player
        """
        # Validate action is legal
        legal_actions = self.legal_moves()
        if action not in legal_actions:
            raise ValueError(f"Illegal action {action} for player {self.turn}. Legal actions: {legal_actions}")
        
        if action[0] == "move":
            _, x, y = action
            self.positions[self.turn] = (x, y)
            if self._check_win(self.turn):
                self.winner = self.turn
        elif action[0] == "wall":
            _, x, y, o = action
            self.board.place_wall(x, y, o)
            self.walls_remaining[self.turn] -= 1

        self.turn = (self.turn + 1) % self.num_players

    def _check_win(self, player: int) -> bool:
        """Check if a player has won the game.
        
        Args:
            player (int): Player index (0-indexed)
            
        Returns:
            bool: True if the player has reached their goal
        """
        x, y = self.positions[player]
        if self.num_players == 2:
            return (player == 0 and y == self.board_size - 1) or (player == 1 and y == 0)
        else:
            goals = [(None, self.board_size - 1), (None, 0), (self.board_size - 1, None), (0, None)]
            gx, gy = goals[player]
            return (gx is None or x == gx) and (gy is None or y == gy)

    def get_state(self) -> Dict[str, Union[List, int, Optional[int]]]:
        """Get the current game state.
        
        Returns:
            Dict[str, Union[List, int, Optional[int]]]: Dictionary containing:
                - positions: List of player positions
                - horiz_walls: List of horizontal wall positions
                - vert_walls: List of vertical wall positions
                - walls_remaining: List of walls remaining per player
                - turn: Current player's turn
                - winner: Winner index or None
        """
        return {
            "positions": self.positions,
            "horiz_walls": list(self.horiz_walls),
            "vert_walls": list(self.vert_walls),
            "walls_remaining": self.walls_remaining,
            "turn": self.turn,
            "winner": self.winner
        }
