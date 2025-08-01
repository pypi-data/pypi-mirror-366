"""
Quoridor Board Implementation

Coordinate System: 
- (0,0) at bottom-left corner of the board
- Positive x rightward, positive y upward  
- Wall arrays: horiz_walls[x,y] = wall on top edge of square (x,y)
              vert_walls[x,y] = wall on right edge of square (x,y)
"""
import numpy as np
from typing import Tuple, Union, List


class Board:
    """Board representation for Quoridor game with wall state management.
    
    The Board class manages wall placements using 2D numpy arrays for efficient
    operations. Walls are represented as boolean arrays where True indicates
    the presence of a wall segment.
    
    Attributes:
        size (int): Size of the square board (default 9 for standard Quoridor)
        horiz_walls (np.ndarray): Horizontal wall segments array
        vert_walls (np.ndarray): Vertical wall segments array
    """
    def __init__(self, size: int = 9) -> None:
        """Initialize a new Board instance.
        
        Args:
            size (int): Size of the square board. Must be >= 3 for valid gameplay.
                       Standard Quoridor uses 9.
        
        Raises:
            ValueError: If size is less than 3, which would not allow valid gameplay.
        """
        if size < 3:
            raise ValueError("Board size must be at least 3 for valid gameplay")
        self.size = size
        self.reset()

    def reset(self) -> None:
        """Reset the board to initial state with no walls placed.
        
        Initializes both horizontal and vertical wall arrays as (size-1, size-1)
        boolean arrays filled with False.
        """
        self.horiz_walls = np.zeros((self.size - 1, self.size), dtype=np.bool_)
        self.vert_walls = np.zeros((self.size, self.size - 1), dtype=np.bool_)

    def is_valid_wall(self, x: int, y: int, orientation: str) -> bool:
        """Check if a wall placement is valid at the given position.
        
        Args:
            x (int): X coordinate for wall placement
            y (int): Y coordinate for wall placement
            orientation (str): Wall orientation, either 'h' for horizontal or 'v' for vertical
        
        Returns:
            bool: True if the wall placement is valid, False otherwise
        
        Note:
            Implements proper Quoridor rules: prevents overlapping 2-unit walls,
            but allows adjacent walls that don't overlap.
        """
        # Validate orientation parameter
        if orientation not in ['h', 'v']:
            return False
            
        if orientation == 'h':
            # Check bounds for 2-unit horizontal wall
            if x >= self.size - 1 or y >= self.size - 1:
                return False
            # Check if this wall would overlap existing walls
            return not (self.horiz_walls[x, y] or 
                       (y > 0 and self.horiz_walls[x, y-1]) or
                       (y < self.size - 2 and self.horiz_walls[x, y+1]))
        elif orientation == 'v':
            # Check bounds for 2-unit vertical wall
            if x >= self.size - 1 or y >= self.size - 1:
                return False
            # Check if this wall would overlap existing walls
            return not (self.vert_walls[x, y] or
                       (x > 0 and self.vert_walls[x-1, y]) or
                       (x < self.size - 2 and self.vert_walls[x+1, y]))
        return False

    def place_wall(self, x: int, y: int, orientation: str) -> None:
        """Place a wall at the specified position and orientation.
        
        Args:
            x (int): X coordinate for wall placement
            y (int): Y coordinate for wall placement
            orientation (str): Wall orientation, either 'h' for horizontal or 'v' for vertical
        
        Raises:
            ValueError: If the wall placement is invalid according to is_valid_wall()
            TypeError: If coordinates are not integers
        """
        # Validate input types and ranges
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("Coordinates must be integers")
        if not isinstance(orientation, str):
            raise TypeError("Orientation must be a string")
        if x < 0 or y < 0 or x >= self.size - 1 or y >= self.size - 1:
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds for board size {self.size}")
        if orientation not in ['h', 'v']:
            raise ValueError("Orientation must be 'h' for horizontal or 'v' for vertical")
            
        if not self.is_valid_wall(x, y, orientation):
            raise ValueError("Invalid wall placement: would overlap existing walls")
            
        if orientation == 'h':
            self.horiz_walls[x, y] = True
        else:
            self.vert_walls[x, y] = True

    def wall_blocks(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        """
        Determine whether a wall blocks movement between two adjacent board positions.

        Args:
            a (Tuple[int, int]): Coordinates (x, y) of the first position.
            b (Tuple[int, int]): Coordinates (x, y) of the second position.

        Returns:
            bool: True if a wall blocks movement between positions a and b, False otherwise.

        Notes:
            - Positions must be orthogonal neighbors (differ by exactly one in either x or y).
            - Both positions must be within the board boundaries.
            - Checks the appropriate horizontal or vertical wall arrays depending on movement direction.
        """
        x1, y1 = a
        x2, y2 = b
        dx, dy = x2 - x1, y2 - y1

        # Ensure positions are orthogonal neighbors
        if abs(dx) + abs(dy) != 1:
            return False

        # Ensure both positions are on the board
        if not (0 <= x1 < self.size and 0 <= y1 < self.size and
                0 <= x2 < self.size and 0 <= y2 < self.size):
            return False

        # Vertical move: check horizontal walls
        if dy != 0:
            xi = x1
            yi = min(y1, y2)
            if 0 <= xi < self.size - 1 and 0 <= yi < self.size:
                return bool(self.horiz_walls[xi, yi])
            return False

        # Horizontal move: check vertical walls
        xi = min(x1, x2)
        yi = y1
        if 0 <= xi < self.size and 0 <= yi < self.size - 1:
            return bool(self.vert_walls[xi, yi])

        return False

    def get_walls(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get copies of the current wall state arrays.
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing copies of
                (horizontal_walls, vertical_walls) arrays
        """
        return self.horiz_walls.copy(), self.vert_walls.copy()

    def count_walls(self) -> Tuple[int, int]:
        """Return count of placed walls (horizontal, vertical).
        
        Returns:
            Tuple[int, int]: A tuple containing the count of placed walls
                as (horizontal_count, vertical_count)
        
        Note:
            Useful for game state analysis, checking wall limits,
            and strategic planning.
        """
        return int(np.sum(self.horiz_walls)), int(np.sum(self.vert_walls))

    def clone(self) -> 'Board':
        """Create a deep copy of the current board state.
        
        Returns:
            Board: A new Board instance with identical wall configurations
        
        Note:
            Useful for game tree search or simulation where you need to
            test moves without modifying the original board state.
        """
        new_board = Board(size=self.size)
        new_board.horiz_walls = self.horiz_walls.copy()
        new_board.vert_walls = self.vert_walls.copy()
        return new_board

    def is_empty(self) -> bool:
        """Check if board has no walls placed.
        
        Returns:
            bool: True if no walls are placed on the board, False otherwise
        
        Note:
            Efficiently checks both horizontal and vertical wall arrays using numpy operations.
        """
        return not (np.any(self.horiz_walls) or np.any(self.vert_walls))

    def get_wall_positions(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """Get positions of all placed walls.
        
        Returns:
            Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]: A tuple containing
                (horizontal_positions, vertical_positions) where each position list
                contains (x, y) coordinate tuples of placed wall segments
        
        Note:
            Uses numpy.argwhere() for efficient position extraction. Coordinates
            follow the same convention as the wall arrays: (x, y) where a wall
            segment at position (x, y) affects the boundary of square (x, y).
        """
        h_positions = [(x, y) for x, y in np.argwhere(self.horiz_walls)]
        v_positions = [(x, y) for x, y in np.argwhere(self.vert_walls)]
        return h_positions, v_positions
