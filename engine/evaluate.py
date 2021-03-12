from enum import Enum
import numpy as np
from numpy.core.numeric import binary_repr

import engine.chessboard as cb
import engine.lookup_tables as tb
import engine.helper as hp
import engine.square_tables as sqtb
from engine.constants import Piece, Color

class Score(Enum):
    PAWN = np.int32(100)
    KNIGHT = np.int32(320)
    BISHOP = np.int32(330)
    ROOK = np.int32(500)
    QUEEN = np.int32(900)
    KING = np.int32(20000)

def get_piece_diff(position):
    # gets a points for pieces on the board
    score = 0
    for piece in Piece:
        white = hp.bit_count(position.pieces[Color.WHITE][piece])
        black = hp.bit_count(position.pieces[Color.BLACK][piece])
        score += white - black
    return score

def score_piece_placement(position, color, piece):
    # gets a bonus points for piece placement
    bb = position.pieces[color][piece]
    score = 0
    for i in range(64):
        if bb >> np.uint8(i) & np.uint8(1):
            if color == Color.WHITE:
                score += sqtb.BOARD_SCORE[piece][63-i]
            if color == Color.BLACK:
                score += sqtb.BOARD_SCORE[piece][i]
    return score

def get_score(position):
    # scores a positon for side to move
    material = get_piece_diff(position)
    placement = 0
    for piece in Piece:
        white_placement = score_piece_placement(position, Color.WHITE, piece)
        black_placement = score_piece_placement(position, Color.BLACK, piece)
        placement += white_placement - black_placement
    return material + placement