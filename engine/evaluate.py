from enum import Enum, IntEnum
import numpy as np
from numpy.core.numeric import binary_repr

import engine.chessboard as cb
import engine.lookup_tables as tb
import engine.helper as hp
import engine.square_tables as sqtb
from engine.constants import Piece, Color
from engine.square import Square

class Score(IntEnum):
    # values of each piece in centipawns (1/100 of a pawn)
    PAWN = np.int32(100)
    KNIGHT = np.int32(320)
    BISHOP = np.int32(330)
    ROOK = np.int32(500)
    QUEEN = np.int32(900)
    KING = np.int32(20000)

def get_piece_diff(position):
    # gets a points for pieces on the board
    values = [100, 320, 330, 500, 900, 20000]
    score = 0
    for piece in Piece:
        score += hp.bit_count(position.pieces[Color.WHITE][piece]) * values[piece]
        score -= hp.bit_count(position.pieces[Color.BLACK][piece]) * values[piece]
    return score

def score_piece_placement(position, color, piece):
    # gets a bonus points for piece placement
    bb = position.pieces[color][piece]
    score = 0
    for i in range(64):
        if (bb >> np.uint8(i)) & np.uint8(1):
            rank = i // 8
            file = i % 8
            if color == Color.WHITE:
                square = rank*8 + file
                score += sqtb.BOARD_SCORE[piece][63-square]
            else:
                square = (7-rank)*8 + (file)
                score -= sqtb.BOARD_SCORE[piece][63-square]
    return score

def get_score(position):
    # scores a positon for side to move
    material = get_piece_diff(position)
    placement = 0
    for piece in Piece:
        placement += score_piece_placement(position, Color.WHITE, piece)
        placement += score_piece_placement(position, Color.BLACK, piece)
    return material + placement