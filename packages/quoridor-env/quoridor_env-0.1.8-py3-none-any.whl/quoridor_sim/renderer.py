import json


def export_state_to_json(state):
    """
    Convert internal game state to a JSON-serializable dict for 3D rendering.
    
    Args:
        state (dict): Game state dictionary containing required keys
        
    Returns:
        str: JSON string representation of the state
        
    Raises:
        TypeError: If state is not a dictionary
        KeyError: If required keys are missing from state
    """
    # Add input validation
    if not isinstance(state, dict):
        raise TypeError("State must be a dictionary")
    
    required_keys = ["positions", "horiz_walls", "vert_walls", "walls_remaining", "turn", "winner"]
    missing = [key for key in required_keys if key not in state]
    if missing:
        raise KeyError(f"Missing required state keys: {missing}")
    
    return json.dumps({
        "positions": [{"x": x, "y": y} for (x, y) in state["positions"]],
        "horiz_walls": [{"x": x, "y": y} for (x, y) in state["horiz_walls"]],
        "vert_walls": [{"x": x, "y": y} for (x, y) in state["vert_walls"]],
        "walls_remaining": state["walls_remaining"],
        "turn": state["turn"],
        "winner": state["winner"]
    }, indent=2)

def save_state_to_file(state, filename):
    """
    Save game state to a JSON file.
    
    Args:
        state (dict): Game state dictionary
        filename (str): Path to the output file
        
    Raises:
        IOError: If file cannot be written
        TypeError: If state is not a dictionary
        KeyError: If required keys are missing from state
    """
    try:
        with open(filename, "w") as f:
            f.write(export_state_to_json(state))
    except IOError as e:
        raise IOError(f"Failed to save state to {filename}: {e}")

def load_state_from_file(filename):
    """
    Load game state from a JSON file.
    
    Args:
        filename (str): Path to the input file
        
    Returns:
        dict: Game state dictionary
        
    Raises:
        IOError: If file cannot be read
        json.JSONDecodeError: If file contains invalid JSON
    """
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except IOError as e:
        raise IOError(f"Failed to load state from {filename}: {e}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {filename}: {e.msg}", e.doc, e.pos)
