# src/yaht/validate.py
from yaht.scorecard import Scorecard
from yaht.utils import Category, Combo


def is_playable(category: Category, combo: Combo, card: Scorecard) -> bool:
    """True if combo is playable for the specified category/card else False"""
