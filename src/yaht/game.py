from dataclasses import dataclass

from yaht.dicetypes import DiceCup
from yaht.player import Player
from yaht.scorecard import ScorecardView


@dataclass
class PlayerGameState:
    dice_cup: DiceCup
    card: ScorecardView


class Game:
    def __init__(self, players: list[Player]):
        """Initialize game state."""
        raise NotImplementedError()

    def play_game(self) -> None:
        """Run the full game loop until completion."""
        raise NotImplementedError()

    def winning_players(self) -> list[Player]:
        """Returns which player(s) won at the end of the game."""
        raise NotImplementedError()

    def _play_turn(self, player: Player) -> None:
        """Internal method to run a full turn for the given player."""
        raise NotImplementedError()

    def _is_game_over(self) -> bool:
        """Internal: returns True if all players have completed all 13 turns."""
        raise NotImplementedError()

    def _next_player(self) -> Player:
        """Internal method returns the next player in the turn."""
        raise NotImplementedError()

    def _current_player(self) -> Player:
        """Internal method returns the current player in the turn."""
        raise NotImplementedError()
