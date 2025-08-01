"""
Comprehensive test suite for QuoridorGame core functionality.
"""
import pytest
from quoridor_sim.core import QuoridorGame


class TestQuoridorGameInitialization:
    """Test game initialization and reset functionality."""
    
    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        game = QuoridorGame()
        assert game.board_size == 9
        assert game.num_players == 2
        assert game.max_walls == 10
        assert game.turn == 0
        assert game.winner is None
        assert len(game.positions) == 2
        assert len(game.walls_remaining) == 2
        assert all(walls == 10 for walls in game.walls_remaining)
    
    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        game = QuoridorGame(num_players=4, max_walls=8)
        assert game.num_players == 4
        assert game.max_walls == 8
        assert len(game.positions) == 4
        assert len(game.walls_remaining) == 4
        assert all(walls == 8 for walls in game.walls_remaining)
    
    def test_init_invalid_board_size(self):
        """Test that invalid board size raises assertion error."""
        with pytest.raises(AssertionError):
            QuoridorGame(board_size=8)
    
    def test_init_invalid_num_players(self):
        """Test that invalid number of players raises assertion error."""
        with pytest.raises(AssertionError):
            QuoridorGame(num_players=3)
        with pytest.raises(AssertionError):
            QuoridorGame(num_players=1)
        with pytest.raises(AssertionError):
            QuoridorGame(num_players=5)
    
    def test_initial_positions_2_players(self):
        """Test initial positions for 2-player game."""
        game = QuoridorGame(num_players=2)
        expected = [(4, 0), (4, 8)]
        assert game.positions == expected
    
    def test_initial_positions_4_players(self):
        """Test initial positions for 4-player game."""
        game = QuoridorGame(num_players=4)
        expected = [(4, 0), (4, 8), (0, 4), (8, 4)]
        assert game.positions == expected
    
    def test_reset(self):
        """Test game reset functionality."""
        game = QuoridorGame()
        # Make some changes
        game.turn = 1
        game.winner = 0
        game.walls_remaining[0] = 5
        game.board.place_wall(0, 0, 'h')
        
        # Reset and verify
        game.reset()
        assert game.turn == 0
        assert game.winner is None
        assert all(walls == 10 for walls in game.walls_remaining)
        assert game.board.is_empty()


class TestPawnMovement:
    """Test pawn movement mechanics including jumping."""
    
    def test_basic_pawn_moves(self):
        """Test basic pawn movement in all directions."""
        game = QuoridorGame()
        game.positions[0] = (4, 4)  # Move to center
        
        moves = game._legal_pawn_moves(0)
        expected_moves = [
            ("move", 3, 4),  # left
            ("move", 5, 4),  # right
            ("move", 4, 3),  # down
            ("move", 4, 5),  # up
        ]
        
        assert len(moves) == 4
        for move in expected_moves:
            assert move in moves
    
    def test_pawn_moves_blocked_by_walls(self):
        """Test that walls block pawn movement."""
        game = QuoridorGame()
        game.positions[0] = (4, 4)
        
        # Place walls blocking movement
        game.board.place_wall(3, 4, 'v')  # Block left movement
        game.board.place_wall(4, 4, 'h')  # Block up movement
        
        moves = game._legal_pawn_moves(0)
        move_coords = [(x, y) for _, x, y in moves]
        
        # Should not be able to move left or up
        assert (3, 4) not in move_coords
        assert (4, 5) not in move_coords
        # Should still be able to move right and down
        assert (5, 4) in move_coords
        assert (4, 3) in move_coords
    
    def test_pawn_moves_at_board_edges(self):
        """Test pawn movement at board boundaries."""
        game = QuoridorGame()
        
        # Test corner position
        game.positions[0] = (0, 0)
        moves = game._legal_pawn_moves(0)
        move_coords = [(x, y) for _, x, y in moves]
        
        # Only right and up should be possible
        assert (1, 0) in move_coords
        assert (0, 1) in move_coords
        assert len(moves) == 2
    
    def test_straight_pawn_jump(self):
        """Test jumping straight over an adjacent pawn."""
        game = QuoridorGame()
        game.positions[0] = (4, 4)
        game.positions[1] = (4, 5)  # Player 1 adjacent to player 0
        
        moves = game._legal_pawn_moves(0)
        move_coords = [(x, y) for _, x, y in moves]
        
        # Should be able to jump over player 1
        assert (4, 6) in move_coords
        # Should not be able to move to occupied square
        assert (4, 5) not in move_coords
    
    def test_diagonal_pawn_jump_when_blocked(self):
        """Test diagonal jump when straight jump is blocked by wall."""
        game = QuoridorGame()
        game.positions[0] = (4, 4)
        game.positions[1] = (4, 5)  # Player 1 adjacent to player 0
        
        # Block straight jump with wall
        game.board.place_wall(4, 5, 'h')
        
        moves = game._legal_pawn_moves(0)
        move_coords = [(x, y) for _, x, y in moves]
        
        # Should not be able to jump straight (blocked by wall)
        assert (4, 6) not in move_coords
        # Should be able to make diagonal jumps
        assert (3, 5) in move_coords or (5, 5) in move_coords
    
    def test_no_jump_when_target_occupied(self):
        """Test that jump is not possible when target square is occupied."""
        game = QuoridorGame(num_players=4)
        game.positions[0] = (4, 4)
        game.positions[1] = (4, 5)  # Adjacent pawn
        game.positions[2] = (4, 6)  # Blocking jump target
        
        moves = game._legal_pawn_moves(0)
        move_coords = [(x, y) for _, x, y in moves]
        
        # Straight jump should not be possible
        assert (4, 6) not in move_coords
        # Should still be able to move to other directions
        assert (3, 4) in move_coords
        assert (5, 4) in move_coords


class TestWallPlacement:
    """Test wall placement mechanics and validation."""
    
    def test_legal_wall_placements(self):
        """Test basic wall placement generation."""
        game = QuoridorGame()
        walls = game._legal_wall_placements()
        
        # Should have many possible wall placements initially
        assert len(walls) > 0
        
        # Check format of wall actions
        for wall in walls[:5]:  # Check first few
            assert len(wall) == 4
            assert wall[0] == "wall"
            assert isinstance(wall[1], int)
            assert isinstance(wall[2], int)
            assert wall[3] in ['h', 'v']
    
    def test_no_walls_when_inventory_empty(self):
        """Test that no wall placements are returned when out of walls."""
        game = QuoridorGame()
        game.walls_remaining[0] = 0
        
        walls = game._legal_wall_placements()
        assert len(walls) == 0
    
    def test_wall_placement_pathfinding_validation(self):
        """Test that walls blocking all paths are not allowed."""
        game = QuoridorGame()
        
        # This test verifies that _would_block_all_paths is being called
        # The actual pathfinding logic is tested separately
        walls = game._legal_wall_placements()
        
        # All returned walls should be valid (not blocking all paths)
        for wall in walls:
            _, x, y, orientation = wall
            assert not game._would_block_all_paths((x, y), orientation)


class TestPathfinding:
    """Test pathfinding and goal reachability."""
    
    def test_can_reach_goal_initial_state(self):
        """Test that players can reach goals from initial positions."""
        game = QuoridorGame()
        
        # Both players should be able to reach their goals initially
        assert game._can_reach_goal(0)
        assert game._can_reach_goal(1)
    
    def test_can_reach_goal_4_players(self):
        """Test goal reachability for 4-player game."""
        game = QuoridorGame(num_players=4)
        
        # All players should be able to reach their goals initially
        for player in range(4):
            assert game._can_reach_goal(player)
    
    def test_blocked_path_detection(self):
        """Test detection of completely blocked paths."""
        game = QuoridorGame()
        
        # Create a scenario that might block a path
        # (This is a complex test that would need specific wall configurations)
        # For now, just verify the method works
        result = game._would_block_all_paths((4, 4), 'h')
        assert isinstance(result, bool)


class TestWinConditions:
    """Test win condition checking."""
    
    def test_check_win_position_2_players(self):
        """Test win position checking for 2-player game."""
        game = QuoridorGame()
        
        # Player 0 wins by reaching y=8
        assert game._check_win_position(0, (4, 8))
        assert not game._check_win_position(0, (4, 7))
        
        # Player 1 wins by reaching y=0
        assert game._check_win_position(1, (4, 0))
        assert not game._check_win_position(1, (4, 1))
    
    def test_check_win_position_4_players(self):
        """Test win position checking for 4-player game."""
        game = QuoridorGame(num_players=4)
        
        # Player 0 wins by reaching y=8
        assert game._check_win_position(0, (4, 8))
        
        # Player 1 wins by reaching y=0
        assert game._check_win_position(1, (4, 0))
        
        # Player 2 wins by reaching x=8
        assert game._check_win_position(2, (8, 4))
        
        # Player 3 wins by reaching x=0
        assert game._check_win_position(3, (0, 4))
    
    def test_check_win(self):
        """Test overall win checking."""
        game = QuoridorGame()
        
        # Initially no winner
        assert not game._check_win(0)
        assert not game._check_win(1)
        
        # Move player 0 to winning position
        game.positions[0] = (4, 8)
        assert game._check_win(0)
        assert not game._check_win(1)


class TestGameFlow:
    """Test complete game flow and step execution."""
    
    def test_legal_moves_format(self):
        """Test that legal_moves returns properly formatted actions."""
        game = QuoridorGame()
        moves = game.legal_moves()
        
        assert len(moves) > 0
        
        for move in moves:
            assert isinstance(move, tuple)
            assert move[0] in ['move', 'wall']
            if move[0] == 'move':
                assert len(move) == 3
                assert isinstance(move[1], int)
                assert isinstance(move[2], int)
            elif move[0] == 'wall':
                assert len(move) == 4
                assert isinstance(move[1], int)
                assert isinstance(move[2], int)
                assert move[3] in ['h', 'v']
    
    def test_step_valid_move_action(self):
        """Test executing a valid move action."""
        game = QuoridorGame()
        initial_pos = game.positions[0]
        
        # Get a legal move
        moves = game.legal_moves()
        move_actions = [m for m in moves if m[0] == 'move']
        assert len(move_actions) > 0
        
        action = move_actions[0]
        initial_turn = game.turn
        
        game.step(action)
        
        # Position should be updated
        assert game.positions[initial_turn] != initial_pos
        assert game.positions[initial_turn] == (action[1], action[2])
        
        # Turn should advance
        assert game.turn == (initial_turn + 1) % game.num_players
    
    def test_step_valid_wall_action(self):
        """Test executing a valid wall action."""
        game = QuoridorGame()
        
        # Get a legal wall placement
        moves = game.legal_moves()
        wall_actions = [m for m in moves if m[0] == 'wall']
        assert len(wall_actions) > 0
        
        action = wall_actions[0]
        initial_walls = game.walls_remaining[0]
        initial_turn = game.turn
        
        game.step(action)
        
        # Wall should be placed
        x, y, orientation = action[1], action[2], action[3]
        if orientation == 'h':
            h_walls, _ = game.board.get_wall_positions()
            assert (x, y) in h_walls
        else:
            _, v_walls = game.board.get_wall_positions()
            assert (x, y) in v_walls
        
        # Wall count should decrease
        assert game.walls_remaining[initial_turn] == initial_walls - 1
        
        # Turn should advance
        assert game.turn == (initial_turn + 1) % game.num_players
    
    def test_step_invalid_action(self):
        """Test that invalid actions raise ValueError."""
        game = QuoridorGame()
        
        # Try an invalid move (out of bounds)
        with pytest.raises(ValueError):
            game.step(("move", -1, 0))
        
        # Try an invalid wall placement
        with pytest.raises(ValueError):
            game.step(("wall", 10, 10, 'h'))
    
    def test_step_winning_move(self):
        """Test that winning move sets winner."""
        game = QuoridorGame()
        
        # Move player 0 close to winning position
        game.positions[0] = (4, 7)
        
        # Make winning move
        game.step(("move", 4, 8))
        
        assert game.winner == 0
    
    def test_get_state(self):
        """Test game state retrieval."""
        game = QuoridorGame()
        
        state = game.get_state()
        
        assert isinstance(state, dict)
        assert 'positions' in state
        assert 'horiz_walls' in state
        assert 'vert_walls' in state
        assert 'walls_remaining' in state
        assert 'turn' in state
        assert 'winner' in state
        
        assert state['positions'] == game.positions
        assert state['walls_remaining'] == game.walls_remaining
        assert state['turn'] == game.turn
        assert state['winner'] == game.winner


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_multiple_pawns_blocking_jumps(self):
        """Test complex pawn configurations."""
        game = QuoridorGame(num_players=4)
        
        # Create a crowded scenario
        game.positions[0] = (4, 4)
        game.positions[1] = (4, 5)  # North
        game.positions[2] = (5, 4)  # East
        game.positions[3] = (3, 4)  # West
        
        moves = game._legal_pawn_moves(0)
        move_coords = [(x, y) for _, x, y in moves]
        
        # Should still have some legal moves (potentially jumps or south)
        assert len(moves) > 0
        assert (4, 3) in move_coords  # South should be free
    
    def test_wall_properties_compatibility(self):
        """Test that wall properties work correctly."""
        game = QuoridorGame()
        
        # Initially no walls
        assert len(game.horiz_walls) == 0
        assert len(game.vert_walls) == 0
        
        # Place some walls
        game.board.place_wall(0, 0, 'h')
        game.board.place_wall(1, 1, 'v')
        
        assert len(game.horiz_walls) == 1
        assert len(game.vert_walls) == 1
        assert (0, 0) in game.horiz_walls
        assert (1, 1) in game.vert_walls


if __name__ == "__main__":
    pytest.main([__file__])