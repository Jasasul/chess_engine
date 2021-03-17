import numpy as np
from enum import IntEnum

class Color(IntEnum):
    # 2 players - 2 side to move
    WHITE = 0
    BLACK = 1

class Piece(IntEnum):
    # 6 types of pieces
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

    def to_char(self):
        # for notation
        if self == Piece.PAWN:
            return 'p'
        elif self == Piece.KNIGHT:
            return 'n'
        elif self == Piece.BISHOP:
            return 'b'
        elif self == Piece.ROOK:
            return 'r'
        elif self == Piece.QUEEN:
            return 'q'
        elif self == Piece.KING:
            return 'k'

class Castle(IntEnum):
    # kingside/short and queenside/long
    OO = 0
    OOO = 1

class Rank(IntEnum):
    # 8 ranks - horizontally
    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7

class File(IntEnum):
    # 8 files - vertically
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7