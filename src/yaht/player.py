# src/yaht/player.py
from typing import Protocol

from yaht.category import Category
from yaht.game import PlayerGameState


class Player(Protocol):
    def take_turn(self, state: PlayerGameState) -> Category:
        """Roll dice then choose category to score against."""
        raise NotImplementedError()
