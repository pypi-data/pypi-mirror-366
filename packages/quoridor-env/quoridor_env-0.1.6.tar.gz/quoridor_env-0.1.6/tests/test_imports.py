"""
Test basic package imports to ensure all modules can be imported correctly.
"""
import pytest


def test_import_main_package():
    """Test that the main quoridor_sim package can be imported."""
    import quoridor_sim
    assert quoridor_sim is not None


def test_import_all_modules():
    """Test that all modules listed in __all__ can be imported."""
    from quoridor_sim import board, core, players, quoridor_env, episode_logger, renderer
    
    # Verify all modules are importable
    assert board is not None
    assert core is not None
    assert players is not None
    assert quoridor_env is not None
    assert episode_logger is not None
    assert renderer is not None


def test_import_individual_modules():
    """Test importing each module individually."""
    # Test board module
    from quoridor_sim import board
    assert hasattr(board, 'Board')
    
    # Test core module
    from quoridor_sim import core
    assert hasattr(core, 'QuoridorGame')
    
    # Test players module
    from quoridor_sim import players
    assert players is not None
    
    # Test quoridor_env module
    from quoridor_sim import quoridor_env
    assert quoridor_env is not None
    
    # Test episode_logger module
    from quoridor_sim import episode_logger
    assert episode_logger is not None
    
    # Test renderer module (the one we just added)
    from quoridor_sim import renderer
    assert hasattr(renderer, 'export_state_to_json')
    assert hasattr(renderer, 'save_state_to_file')
    assert hasattr(renderer, 'load_state_from_file')


def test_renderer_functions():
    """Test that renderer module functions work correctly."""
    from quoridor_sim import renderer
    
    # Test with a sample state
    sample_state = {
        "positions": [(0, 1), (8, 7)],
        "horiz_walls": [(2, 3), (4, 5)],
        "vert_walls": [(1, 2), (6, 7)],
        "walls_remaining": [8, 9],
        "turn": 0,
        "winner": None
    }
    
    # Test export_state_to_json
    json_output = renderer.export_state_to_json(sample_state)
    assert isinstance(json_output, str)
    assert "positions" in json_output
    assert "horiz_walls" in json_output
    assert "vert_walls" in json_output
    
    # Test JSON is valid
    import json
    parsed = json.loads(json_output)
    assert parsed["positions"] == [{"x": 0, "y": 1}, {"x": 8, "y": 7}]
    assert parsed["turn"] == 0
    assert parsed["winner"] is None


def test_renderer_input_validation():
    """Test that renderer functions properly validate input."""
    from quoridor_sim import renderer
    
    # Test export_state_to_json with invalid input
    with pytest.raises(TypeError, match="State must be a dictionary"):
        renderer.export_state_to_json("not a dict")
    
    with pytest.raises(TypeError, match="State must be a dictionary"):
        renderer.export_state_to_json(None)
    
    with pytest.raises(TypeError, match="State must be a dictionary"):
        renderer.export_state_to_json(42)
    
    # Test export_state_to_json with missing keys
    incomplete_state = {
        "positions": [(0, 1)],
        "horiz_walls": [],
        "vert_walls": []
        # Missing: walls_remaining, turn, winner
    }
    
    with pytest.raises(KeyError, match="Missing required state keys"):
        renderer.export_state_to_json(incomplete_state)
    
    # Test with empty dict
    with pytest.raises(KeyError, match="Missing required state keys"):
        renderer.export_state_to_json({})


def test_renderer_file_io():
    """Test file I/O functions work correctly."""
    from quoridor_sim import renderer
    import tempfile
    import os
    import json
    
    # Valid test state
    sample_state = {
        "positions": [(0, 1), (8, 7)],
        "horiz_walls": [(2, 3), (4, 5)],
        "vert_walls": [(1, 2), (6, 7)],
        "walls_remaining": [8, 9],
        "turn": 0,
        "winner": None
    }
    
    # Test save_state_to_file and load_state_from_file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
        tmp_filename = tmp_file.name
    
    try:
        # Test successful save and load
        renderer.save_state_to_file(sample_state, tmp_filename)
        assert os.path.exists(tmp_filename)
        
        loaded_state = renderer.load_state_from_file(tmp_filename)
        assert loaded_state is not None
        assert loaded_state["positions"] == [{"x": 0, "y": 1}, {"x": 8, "y": 7}]
        assert loaded_state["turn"] == 0
        assert loaded_state["winner"] is None
        
    finally:
        # Clean up
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)


def test_renderer_file_io_error_handling():
    """Test file I/O error handling."""
    from quoridor_sim import renderer
    import json
    
    # Test save_state_to_file with invalid state
    with pytest.raises(TypeError, match="State must be a dictionary"):
        renderer.save_state_to_file("invalid", "/tmp/test.json")
    
    # Test save_state_to_file with invalid path (directory that doesn't exist)
    sample_state = {
        "positions": [(0, 1)],
        "horiz_walls": [],
        "vert_walls": [],
        "walls_remaining": [10],
        "turn": 0,
        "winner": None
    }
    
    with pytest.raises(IOError, match="Failed to save state to"):
        renderer.save_state_to_file(sample_state, "/nonexistent/directory/file.json")
    
    # Test load_state_from_file with nonexistent file
    with pytest.raises(IOError, match="Failed to load state from"):
        renderer.load_state_from_file("/nonexistent/file.json")
    
    # Test load_state_from_file with invalid JSON
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
        tmp_file.write("invalid json content {")
        tmp_filename = tmp_file.name
    
    try:
        with pytest.raises(json.JSONDecodeError, match="Invalid JSON in file"):
            renderer.load_state_from_file(tmp_filename)
    finally:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)