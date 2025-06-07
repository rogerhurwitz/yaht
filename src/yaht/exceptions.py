class GameError(Exception):
    """Base class for all game-related exceptions."""

    pass


class DiceCountError(GameError):
    """Raised when a player attempts to score with more or less than 5 dice."""

    pass


class DieValueError(GameError):
    """Raised when one of the dice in a combination is not between 1 and 6."""

    pass


class CategoryAlreadyScored(GameError):
    """Raised when a player attempts to score a category more than once."""

    pass


class InvalidCategoryError(GameError):
    """Raised when an unknown or unsupported category is specified."""

    pass


class DiceRollCountError(GameError):
    """Raised when player attempts to roll more than 3 times per turn."""

    pass


class DiceRollIndexError(GameError):
    """Raised when player incorrectly specifies dice to reroll during turn."""

    pass
