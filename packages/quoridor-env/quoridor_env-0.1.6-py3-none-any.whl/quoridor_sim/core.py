import numpy as np
from collections import deque
from .board import Board


class QuoridorGame:
    def __init__(self, board_size=9, num_players=2, max_walls=10):
        assert board_size == 9, "Only 9x9 board supported in Quoridor rules."
        assert num_players in [2, 4], "Only 2 or 4 players supported."
        self.board_size = board_size
        self.num_players = num_players
        self.max_walls = max_walls
        self.board = Board(size=board_size)

        self.reset()

    def reset(self):
        self.positions = self._initial_positions()
        self.walls_remaining = [self.max_walls] * self.num_players
        self.board.reset()
        self.turn = 0
        self.winner = None
        
    @property
    def horiz_walls(self):
        """Get horizontal walls as a set for backward compatibility."""
        h_positions, _ = self.board.get_wall_positions()
        return set(h_positions)
        
    @property
    def vert_walls(self):
        """Get vertical walls as a set for backward compatibility."""
        _, v_positions = self.board.get_wall_positions()
        return set(v_positions)

    def _initial_positions(self):
        if self.num_players == 2:
            return [(4, 0), (4, 8)]
        else:
            return [(4, 0), (4, 8), (0, 4), (8, 4)]

    def legal_moves(self):
        # Returns list of legal actions for current player
        move_actions = self._legal_pawn_moves(self.turn)
        wall_actions = self._legal_wall_placements()
        return move_actions + wall_actions

    def _legal_pawn_moves(self, player):
        # Placeholder: returns adjacent unblocked positions
        x, y = self.positions[player]
        moves = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if not self._is_wall_between((x, y), (nx, ny)):
                    moves.append(("move", nx, ny))
        return moves

    def _legal_wall_placements(self):
        # Placeholder: returns all empty positions for wall placement
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

    def _is_wall_between(self, a, b):
        """Check if there's a wall blocking movement between two adjacent positions."""
        return self.board.wall_blocks(a, b)

    def _would_block_all_paths(self, position, orientation):
        """Check if placing a wall would block all paths to goals for any player."""
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
        
    def _can_reach_goal(self, player, board=None):
        """Check if a player can reach their goal using BFS pathfinding."""
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
        
    def _check_win_position(self, player, position):
        """Check if a position satisfies the win condition for a player."""
        x, y = position
        if self.num_players == 2:
            return (player == 0 and y == self.board_size - 1) or (player == 1 and y == 0)
        else:
            goals = [(None, self.board_size - 1), (None, 0), (self.board_size - 1, None), (0, None)]
            gx, gy = goals[player]
            return (gx is None or x == gx) and (gy is None or y == gy)

    def step(self, action):
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

    def _check_win(self, player):
        x, y = self.positions[player]
        if self.num_players == 2:
            return (player == 0 and y == self.board_size - 1) or (player == 1 and y == 0)
        else:
            goals = [(None, self.board_size - 1), (None, 0), (self.board_size - 1, None), (0, None)]
            gx, gy = goals[player]
            return (gx is None or x == gx) and (gy is None or y == gy)

    def get_state(self):
        return {
            "positions": self.positions,
            "horiz_walls": list(self.horiz_walls),
            "vert_walls": list(self.vert_walls),
            "walls_remaining": self.walls_remaining,
            "turn": self.turn,
            "winner": self.winner
        }
