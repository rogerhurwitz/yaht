from yaht.player import Player


class Game:
    def __init__(self, players: list[Player]):
        """Initialize game state."""

    def play_game(self) -> None:
        """Run the full game loop until completion."""

    def get_winner(self) -> list[Player]:
        """Returns which player(s) won at the end of the game."""

    def _play_turn(self, player: Player):
        """Internal method to run a full turn for the given player."""

    def _is_game_over(self) -> bool:
        """Internal: returns True if all players have completed all 13 turns."""

    def _next_player(self) -> Player:
        """Internal method returns the next player in the turn."""

    def _current_player(self) -> Player:
        """Internal method returns the current player in the turn."""
