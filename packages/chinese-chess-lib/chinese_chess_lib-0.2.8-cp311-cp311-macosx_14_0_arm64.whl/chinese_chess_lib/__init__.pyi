"""
Chinese Chess Library
-----------------------

.. currentmodule:: chinese_chess_lib

.. autosummary::
    :toctree: _generate

    get_legal_moves
    warn
    dead
"""

def get_legal_moves(board, chess, flag_ : bool = False):
    """
    Get all legal moves for a piece on the board
    """

def warn(chesses, color : str  = "") -> list[str]:
    """
    Get warnings for the current board state
    """

def dead(chesses, color : str = ""):
    """
    Check if the game is over (dead)
    """

class Chess:
    """
    A chess
    """

    x: int
    y: int
    color: str
    name: str