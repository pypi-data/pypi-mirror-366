import pytest
from unittest.mock import patch
from quoridor_sim.players import BasePlayer, RandomPlayer, HumanPlayer, ScriptedPlayer


def test_base_player_select_action_not_implemented():
    player = BasePlayer(player_id=0)
    with pytest.raises(NotImplementedError):
        player.select_action(state=None, legal_actions=[])


def test_base_player_invalid_id():
    with pytest.raises(ValueError):
        BasePlayer(player_id=-1)
    with pytest.raises(ValueError):
        BasePlayer(player_id="not_an_int")


def test_random_player_empty_actions():
    player = RandomPlayer(player_id=1)
    with pytest.raises(ValueError, match="No legal actions available"):
        player.select_action(state=None, legal_actions=[])


def test_random_player_valid_action():
    player = RandomPlayer(player_id=1)
    legal_actions = ["move", "wall"]
    action = player.select_action(state=None, legal_actions=legal_actions)
    assert action in legal_actions


def test_human_player_empty_actions():
    player = HumanPlayer(player_id=2)
    with pytest.raises(ValueError, match="No legal actions available"):
        player.select_action(state=None, legal_actions=[])


def test_human_player_valid_input():
    player = HumanPlayer(player_id=2)
    legal_actions = ["move", "wall"]
    with patch("builtins.input", return_value="1"):
        action = player.select_action(state=None, legal_actions=legal_actions)
    assert action == "wall"


def test_human_player_invalid_input_then_valid():
    player = HumanPlayer(player_id=2)
    legal_actions = ["move", "wall"]
    with patch("builtins.input", side_effect=["invalid", "99", "0"]):
        action = player.select_action(state=None, legal_actions=legal_actions)
    assert action == "move"


def test_scripted_player_valid_scripted_action():
    script = ["move", "wall"]
    player = ScriptedPlayer(player_id=3, script=script)
    action = player.select_action(state=None, legal_actions=["move", "wall"])
    assert action == "move"
    action = player.select_action(state=None, legal_actions=["wall"])
    assert action == "wall"


def test_scripted_player_exhausted_script():
    player = ScriptedPlayer(player_id=3, script=["move"])
    player.select_action(state=None, legal_actions=["move"])
    with pytest.raises(IndexError, match="Script exhausted"):
        player.select_action(state=None, legal_actions=["move"])


def test_scripted_player_illegal_action():
    player = ScriptedPlayer(player_id=3, script=["illegal"])
    with pytest.raises(ValueError, match="Scripted action not legal"):
        player.select_action(state=None, legal_actions=["move", "wall"])


def test_scripted_player_empty_legal_actions():
    player = ScriptedPlayer(player_id=3, script=["move"])
    with pytest.raises(ValueError, match="No legal actions available"):
        player.select_action(state=None, legal_actions=[])
