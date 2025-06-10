# src/yaht/player.py
import random
from typing import Protocol

from yaht.category import Category
from yaht.dicetypes import Dice
from yaht.scorecard import ScorecardView


class Player(Protocol):
    def take_turn(self, dice: Dice, view: ScorecardView) -> Category:
        """
        Given a Dice object and a read-only view of the scorecard, decide on a
        scoring category. The GameManager will handle actual scoring and rule
        enforcement.
        """


class TestPlayer:
    def take_turn(self, dice: Dice, view: ScorecardView) -> Category:
        unscored = view.get_unscored_categories()
        return random.choice(unscored)
