class GameError(Exception):
    """Base class for all game-related exceptions."""


class CategoryAlreadyScored(GameError):
    """Raised when a player attempts to score a category more than once."""


class DiceCountError(GameError):
    """Raised when a player attempts to score with more or less than 5 dice."""


class DiceRollCountError(GameError):
    """Raised when player attempts to roll more than 3 times per turn."""


class DiceRollIndexError(GameError):
    """Raised when player incorrectly specifies dice to reroll during turn."""


class DieValueError(GameError):
    """Raised when one of the dice in a combination is not between 1 and 6."""


class GameNotOverError(GameError):
    """Raised when action requires current game to be over to be performed."""


class InvalidCategoryError(GameError):
    """Raised when an unknown or unsupported category is specified."""
