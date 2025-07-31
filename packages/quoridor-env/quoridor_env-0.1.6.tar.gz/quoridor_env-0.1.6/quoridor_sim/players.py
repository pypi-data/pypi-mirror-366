import random
from typing import Any, List


class BasePlayer:
    """
    Abstract base class for all player types.

    Attributes:
        player_id (int): Unique identifier for the player.
    """

    def __init__(self, player_id: int) -> None:
        """
        Initialize a BasePlayer instance.

        Args:
            player_id (int): Unique identifier for the player.

        Raises:
            ValueError: If player_id is not a non-negative integer.
        """
        if not isinstance(player_id, int) or player_id < 0:
            raise ValueError("player_id must be a non-negative integer")
        self.player_id = player_id

    def select_action(self, state: Any, legal_actions: List[Any]) -> Any:
        """
        Select an action from the list of legal actions.

        Args:
            state (Any): The current game state.
            legal_actions (List[Any]): List of legal actions.

        Returns:
            Any: The selected action.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError


class RandomPlayer(BasePlayer):
    """
    Player that selects actions uniformly at random from the legal actions.
    """

    def select_action(self, state: Any, legal_actions: List[Any]) -> Any:
        """
        Randomly select an action from the list of legal actions.

        Args:
            state (Any): The current game state.
            legal_actions (List[Any]): List of legal actions.

        Returns:
            Any: The randomly selected action.

        Raises:
            ValueError: If no legal actions are available.
        """
        if not legal_actions:
            raise ValueError("No legal actions available")
        return random.choice(legal_actions)


class HumanPlayer(BasePlayer):
    """
    Player that selects actions based on human input via the console.
    """

    def select_action(self, state: Any, legal_actions: List[Any]) -> Any:
        """
        Prompt the human player to select an action from the list of legal actions.

        Args:
            state (Any): The current game state.
            legal_actions (List[Any]): List of legal actions.

        Returns:
            Any: The action selected by the human player.

        Raises:
            ValueError: If no legal actions are available.
        """
        if not legal_actions:
            raise ValueError("No legal actions available")

        print("Available actions:")
        for idx, action in enumerate(legal_actions):
            print(f"{idx}: {action}")

        while True:
            try:
                choice = int(input(f"Player {self.player_id}, select an action index: "))
                if 0 <= choice < len(legal_actions):
                    return legal_actions[choice]
                else:
                    print("Invalid index. Try again.")
            except ValueError:
                print("Please enter a number.")


class ScriptedPlayer(BasePlayer):
    """
    Player that follows a predefined script of actions.

    Attributes:
        script (List[Any]): A list of predetermined actions.
        step_idx (int): Current step index in the script.
    """

    def __init__(self, player_id: int, script: List[Any]) -> None:
        """
        Initialize a ScriptedPlayer instance.

        Args:
            player_id (int): Unique identifier for the player.
            script (List[Any]): A list of predetermined actions.
        """
        super().__init__(player_id)
        self.script = script
        self.step_idx = 0

    def select_action(self, state: Any, legal_actions: List[Any]) -> Any:
        """
        Select the next scripted action if it is legal.

        Args:
            state (Any): The current game state.
            legal_actions (List[Any]): List of legal actions.

        Returns:
            Any: The selected action from the script.

        Raises:
            ValueError: If the scripted action is not legal.
            IndexError: If the script has been exhausted.
        """
        if self.step_idx >= len(self.script):
            raise IndexError("Script exhausted.")

        if not legal_actions:
            raise ValueError("No legal actions available")

        action = self.script[self.step_idx]
        self.step_idx += 1

        legal_actions_set = set(legal_actions)
        if action in legal_actions_set:
            return action
        else:
            raise ValueError("Scripted action not legal.")
