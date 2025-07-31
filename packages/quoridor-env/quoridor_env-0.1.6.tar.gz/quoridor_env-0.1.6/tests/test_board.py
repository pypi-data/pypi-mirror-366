import unittest
import numpy as np
import sys
import os

# Add the parent directory to the path to import quoridor_sim
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quoridor_sim.board import Board


class TestBoard(unittest.TestCase):
    """Comprehensive test suite for the Board class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.board = Board(size=9)
        self.small_board = Board(size=3)

    def test_board_initialization(self):
        """Test board initialization with different sizes."""
        # Test default size
        board = Board()
        size = board.size
        self.assertEqual(board.size, 9)
        self.assertEqual(board.horiz_walls.shape, (size - 1, size))  # (8, 9)
        self.assertEqual(board.vert_walls.shape, (size, size - 1))   # (9, 8)

        # Test custom size
        board = Board(size=5)
        size = board.size
        self.assertEqual(board.size, 5)
        self.assertEqual(board.horiz_walls.shape, (size - 1, size))  # (4, 5)
        self.assertEqual(board.vert_walls.shape, (size, size - 1))   # (5, 4)

        # Test minimum size
        board = Board(size=3)
        size = board.size
        self.assertEqual(board.size, 3)
        self.assertEqual(board.horiz_walls.shape, (size - 1, size))  # (2, 3)
        self.assertEqual(board.vert_walls.shape, (size, size - 1))   # (3, 2)
        
    def test_board_initialization_invalid_size(self):
        """Test that invalid board sizes raise ValueError."""
        with self.assertRaises(ValueError):
            Board(size=2)
        with self.assertRaises(ValueError):
            Board(size=0)
        with self.assertRaises(ValueError):
            Board(size=-1)

    def test_reset(self):
        """Test board reset functionality."""
        # Place some walls
        self.board.place_wall(0, 0, 'h')
        self.board.place_wall(1, 1, 'v')
        
        # Reset board
        self.board.reset()
        
        # Check all walls are cleared
        self.assertFalse(np.any(self.board.horiz_walls))
        self.assertFalse(np.any(self.board.vert_walls))

    def test_valid_wall_placement_basic(self):
        """Test basic valid wall placements."""
        # Test valid horizontal wall
        self.assertTrue(self.board.is_valid_wall(0, 0, 'h'))
        self.assertTrue(self.board.is_valid_wall(3, 4, 'h'))
        self.assertTrue(self.board.is_valid_wall(7, 7, 'h'))
        
        # Test valid vertical wall
        self.assertTrue(self.board.is_valid_wall(0, 0, 'v'))
        self.assertTrue(self.board.is_valid_wall(3, 4, 'v'))
        self.assertTrue(self.board.is_valid_wall(7, 7, 'v'))

    def test_invalid_wall_placement_bounds(self):
        """Test boundary condition validation."""
        # Test horizontal walls at boundaries
        self.assertFalse(self.board.is_valid_wall(8, 0, 'h'))  # x at boundary
        self.assertFalse(self.board.is_valid_wall(0, 8, 'h'))  # y at boundary
        self.assertFalse(self.board.is_valid_wall(8, 8, 'h'))  # both at boundary
        
        # Test vertical walls at boundaries
        self.assertFalse(self.board.is_valid_wall(8, 0, 'v'))  # x at boundary
        self.assertFalse(self.board.is_valid_wall(0, 8, 'v'))  # y at boundary
        self.assertFalse(self.board.is_valid_wall(8, 8, 'v'))  # both at boundary

    def test_invalid_wall_placement_orientation(self):
        """Test invalid orientation validation."""
        self.assertFalse(self.board.is_valid_wall(0, 0, 'invalid'))
        self.assertFalse(self.board.is_valid_wall(0, 0, 'H'))
        self.assertFalse(self.board.is_valid_wall(0, 0, 'V'))
        self.assertFalse(self.board.is_valid_wall(0, 0, ''))
        self.assertFalse(self.board.is_valid_wall(0, 0, 'horizontal'))

    def test_wall_overlap_detection_horizontal(self):
        """Test horizontal wall overlap detection."""
        # Place initial horizontal wall
        self.board.place_wall(2, 2, 'h')
        
        # Test direct overlap
        self.assertFalse(self.board.is_valid_wall(2, 2, 'h'))
        
        # Test overlapping with adjacent positions (2-unit wall logic)
        self.assertFalse(self.board.is_valid_wall(2, 1, 'h'))  # Would overlap at y=2
        self.assertFalse(self.board.is_valid_wall(2, 3, 'h'))  # Would overlap at y=2
        
        # Test valid adjacent placements (should be allowed)
        self.assertTrue(self.board.is_valid_wall(1, 2, 'h'))  # Different x
        self.assertTrue(self.board.is_valid_wall(3, 2, 'h'))  # Different x
        self.assertTrue(self.board.is_valid_wall(2, 0, 'h'))  # Non-overlapping y
        if self.board.size > 4:
            self.assertTrue(self.board.is_valid_wall(2, 4, 'h'))  # Non-overlapping y

    def test_wall_overlap_detection_vertical(self):
        """Test vertical wall overlap detection."""
        # Place initial vertical wall
        self.board.place_wall(2, 2, 'v')
        
        # Test direct overlap
        self.assertFalse(self.board.is_valid_wall(2, 2, 'v'))
        
        # Test overlapping with adjacent positions (2-unit wall logic)
        self.assertFalse(self.board.is_valid_wall(1, 2, 'v'))  # Would overlap at x=2
        self.assertFalse(self.board.is_valid_wall(3, 2, 'v'))  # Would overlap at x=2
        
        # Test valid adjacent placements (should be allowed)
        self.assertTrue(self.board.is_valid_wall(2, 1, 'v'))  # Different y
        self.assertTrue(self.board.is_valid_wall(2, 3, 'v'))  # Different y
        self.assertTrue(self.board.is_valid_wall(0, 2, 'v'))  # Non-overlapping x
        if self.board.size > 4:
            self.assertTrue(self.board.is_valid_wall(4, 2, 'v'))  # Non-overlapping x

    def test_wall_placement_complex_scenarios(self):
        """Test complex wall placement scenarios."""
        # Test placement of multiple non-overlapping walls
        self.board.place_wall(0, 0, 'h')
        self.board.place_wall(0, 2, 'h')  # Should be valid (non-overlapping)
        self.board.place_wall(2, 0, 'v')
        self.board.place_wall(2, 2, 'v')  # Should be valid (non-overlapping)
        
        # Verify walls are placed
        self.assertTrue(self.board.horiz_walls[0, 0])
        self.assertTrue(self.board.horiz_walls[0, 2])
        self.assertTrue(self.board.vert_walls[2, 0])
        self.assertTrue(self.board.vert_walls[2, 2])

    def test_place_wall_input_validation(self):
        """Test input validation for place_wall method."""
        # Test invalid types
        with self.assertRaises(TypeError):
            self.board.place_wall("0", 0, 'h')
        with self.assertRaises(TypeError):
            self.board.place_wall(0, "0", 'h')
        with self.assertRaises(TypeError):
            self.board.place_wall(0, 0, 123)
        
        # Test out of bounds coordinates
        with self.assertRaises(ValueError):
            self.board.place_wall(-1, 0, 'h')
        with self.assertRaises(ValueError):
            self.board.place_wall(0, -1, 'h')
        with self.assertRaises(ValueError):
            self.board.place_wall(8, 0, 'h')  # x >= size-1
        with self.assertRaises(ValueError):
            self.board.place_wall(0, 8, 'h')  # y >= size-1
        
        # Test invalid orientation
        with self.assertRaises(ValueError):
            self.board.place_wall(0, 0, 'invalid')

    def test_place_wall_overlap_prevention(self):
        """Test that place_wall prevents overlapping walls."""
        # Place initial wall
        self.board.place_wall(2, 2, 'h')
        
        # Try to place overlapping walls
        with self.assertRaises(ValueError):
            self.board.place_wall(2, 2, 'h')  # Direct overlap
        with self.assertRaises(ValueError):
            self.board.place_wall(2, 1, 'h')  # Overlapping 2-unit wall
        with self.assertRaises(ValueError):
            self.board.place_wall(2, 3, 'h')  # Overlapping 2-unit wall

    def test_wall_blocks_movement(self):
        """Test wall blocking logic for all movement directions."""
        # Test horizontal wall blocking vertical movement
        self.board.place_wall(1, 1, 'h')
        
        # Should block movement across the wall
        self.assertTrue(self.board.wall_blocks((1, 1), (1, 2)))  # Moving up
        self.assertTrue(self.board.wall_blocks((1, 2), (1, 1)))  # Moving down
        
        # Should not block parallel movement
        self.assertFalse(self.board.wall_blocks((1, 1), (2, 1)))  # Moving right
        self.assertFalse(self.board.wall_blocks((1, 1), (0, 1)))  # Moving left
        
        # Test vertical wall blocking horizontal movement
        self.board.reset()
        self.board.place_wall(1, 1, 'v')
        
        # Should block movement across the wall
        self.assertTrue(self.board.wall_blocks((1, 1), (2, 1)))  # Moving right
        self.assertTrue(self.board.wall_blocks((2, 1), (1, 1)))  # Moving left
        
        # Should not block parallel movement
        self.assertFalse(self.board.wall_blocks((1, 1), (1, 2)))  # Moving up
        self.assertFalse(self.board.wall_blocks((1, 1), (1, 0)))  # Moving down

    def test_wall_blocks_boundary_conditions(self):
        """Test wall blocking at board boundaries."""
        board = self.board
        size = board.size

        # Test no wall blocks on valid boundary edges
        self.assertFalse(board.wall_blocks((0, 0), (0, 1)))  # top-left
        self.assertFalse(board.wall_blocks((size - 2, size - 1), (size - 2, size - 2)))  # bottom-right edge
        self.assertFalse(board.wall_blocks((size - 1, 0), (size - 2, 0)))  # bottom-left edge
        self.assertFalse(board.wall_blocks((0, size - 1), (1, size - 1)))  # top-right edge

        # Add wall at bottom-right vertical wall position and test again
        board.vert_walls[size - 2, size - 2] = True  # vert_walls[7, 7]
        self.assertTrue(board.wall_blocks((size - 1, size - 2), (size - 2, size - 2)))  # from (8, 7) to (7, 7)

    def test_wall_blocks_non_adjacent(self):
        """Test that wall_blocks returns False for non-adjacent moves."""
        # Test moves with Manhattan distance > 1
        self.assertFalse(self.board.wall_blocks((0, 0), (2, 0)))  # Distance 2
        self.assertFalse(self.board.wall_blocks((0, 0), (0, 2)))  # Distance 2
        self.assertFalse(self.board.wall_blocks((0, 0), (1, 1)))  # Diagonal
        self.assertFalse(self.board.wall_blocks((0, 0), (3, 4)))  # Far away

    def test_get_walls(self):
        """Test get_walls method returns proper copies."""
        # Place some walls
        self.board.place_wall(1, 1, 'h')
        self.board.place_wall(2, 2, 'v')
        
        # Get wall arrays
        horiz, vert = self.board.get_walls()
        
        # Verify they are copies (not references)
        self.assertIsNot(horiz, self.board.horiz_walls)
        self.assertIsNot(vert, self.board.vert_walls)
        
        # Verify content is correct
        np.testing.assert_array_equal(horiz, self.board.horiz_walls)
        np.testing.assert_array_equal(vert, self.board.vert_walls)
        
        # Verify modifying copy doesn't affect original
        horiz[0, 0] = True
        self.assertFalse(self.board.horiz_walls[0, 0])

    def test_clone_method(self):
        """Test board cloning functionality."""
        # Place some walls on original board
        self.board.place_wall(1, 1, 'h')
        self.board.place_wall(2, 2, 'v')
        self.board.place_wall(3, 3, 'h')
        
        # Clone the board
        cloned_board = self.board.clone()
        
        # Verify clone is separate instance
        self.assertIsNot(cloned_board, self.board)
        self.assertIsNot(cloned_board.horiz_walls, self.board.horiz_walls)
        self.assertIsNot(cloned_board.vert_walls, self.board.vert_walls)
        
        # Verify clone has same size
        self.assertEqual(cloned_board.size, self.board.size)
        
        # Verify clone has same wall configuration
        np.testing.assert_array_equal(cloned_board.horiz_walls, self.board.horiz_walls)
        np.testing.assert_array_equal(cloned_board.vert_walls, self.board.vert_walls)
        
        # Verify modifying clone doesn't affect original
        cloned_board.place_wall(0, 0, 'h')
        self.assertFalse(self.board.horiz_walls[0, 0])
        
        # Verify modifying original doesn't affect clone
        self.board.place_wall(4, 4, 'v')
        self.assertFalse(cloned_board.vert_walls[4, 4])

    def test_clone_with_different_sizes(self):
        """Test cloning boards of different sizes."""
        size = 3
        small_board = Board(size=size)
        self.assertEqual(small_board.horiz_walls.shape, (size - 1, size))  # (2, 3)
        self.assertEqual(small_board.vert_walls.shape, (size, size - 1))   # (3, 2)

        small_board.place_wall(0, 0, 'h')
        small_board.place_wall(1, 1, 'v')

        cloned_small = small_board.clone()

        self.assertEqual(cloned_small.size, size)
        self.assertEqual(cloned_small.horiz_walls.shape, (size - 1, size))  # (2, 3)
        self.assertEqual(cloned_small.vert_walls.shape, (size, size - 1))   # (3, 2)
        np.testing.assert_array_equal(cloned_small.horiz_walls, small_board.horiz_walls)
        np.testing.assert_array_equal(cloned_small.vert_walls, small_board.vert_walls)

    def test_small_board_edge_cases(self):
        """Test edge cases with minimum size board (3x3)."""
        # Test wall placement on small board
        self.small_board.place_wall(0, 0, 'h')
        self.small_board.place_wall(1, 1, 'v')
        
        # Test boundary conditions
        self.assertFalse(self.small_board.is_valid_wall(2, 0, 'h'))  # Out of bounds
        self.assertFalse(self.small_board.is_valid_wall(0, 2, 'v'))  # Out of bounds
        
        # Test overlap detection
        self.assertFalse(self.small_board.is_valid_wall(0, 1, 'h'))  # Would overlap
        self.assertFalse(self.small_board.is_valid_wall(0, 1, 'v'))  # Would overlap

    def test_count_walls(self):
        """Test count_walls method functionality."""
        # Test empty board
        h_count, v_count = self.board.count_walls()
        self.assertEqual(h_count, 0)
        self.assertEqual(v_count, 0)
        
        # Place some horizontal walls
        self.board.place_wall(0, 0, 'h')
        self.board.place_wall(1, 1, 'h')
        h_count, v_count = self.board.count_walls()
        self.assertEqual(h_count, 2)
        self.assertEqual(v_count, 0)
        
        # Add some vertical walls
        self.board.place_wall(2, 2, 'v')
        self.board.place_wall(3, 3, 'v')
        self.board.place_wall(4, 4, 'v')
        h_count, v_count = self.board.count_walls()
        self.assertEqual(h_count, 2)
        self.assertEqual(v_count, 3)
        
        # Test return type
        self.assertIsInstance(h_count, int)
        self.assertIsInstance(v_count, int)
        
        # Test with reset
        self.board.reset()
        h_count, v_count = self.board.count_walls()
        self.assertEqual(h_count, 0)
        self.assertEqual(v_count, 0)

    def test_count_walls_small_board(self):
        """Test count_walls method on small board."""
        # Place maximum walls on small board
        self.small_board.place_wall(0, 0, 'h')
        self.small_board.place_wall(1, 1, 'v')
        
        h_count, v_count = self.small_board.count_walls()
        self.assertEqual(h_count, 1)
        self.assertEqual(v_count, 1)

    def test_comprehensive_wall_scenario(self):
        """Test a comprehensive wall placement scenario."""
        # Create a complex wall configuration
        walls_to_place = [
            (0, 0, 'h'),
            (0, 2, 'h'),  # Non-overlapping horizontal walls
            (2, 0, 'v'),
            (2, 2, 'v'),  # Non-overlapping vertical walls
            (4, 1, 'h'),
            (5, 3, 'v'),
        ]
        
        # Place all walls
        for x, y, orientation in walls_to_place:
            self.assertTrue(self.board.is_valid_wall(x, y, orientation))
            self.board.place_wall(x, y, orientation)
        
        # Verify walls are placed correctly
        for x, y, orientation in walls_to_place:
            if orientation == 'h':
                self.assertTrue(self.board.horiz_walls[x, y])
            else:
                self.assertTrue(self.board.vert_walls[x, y])
        
        # Test wall count after complex placement
        h_count, v_count = self.board.count_walls()
        self.assertEqual(h_count, 3)  # 3 horizontal walls placed
        self.assertEqual(v_count, 3)  # 3 vertical walls placed
        
        # Test that overlapping walls are now invalid
        self.assertFalse(self.board.is_valid_wall(0, 1, 'h'))  # Would overlap with (0,0,'h')
        self.assertFalse(self.board.is_valid_wall(1, 0, 'v'))  # Would overlap with (2,0,'v')


if __name__ == '__main__':
    unittest.main()
