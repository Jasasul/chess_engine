import numpy as np
import engine.helper as hp
import engine.square_tables as sqtb
from engine.constants import Piece, Color

def get_piece_diff(position):
    # gets a points for pieces on the board
    values = [100, 320, 330, 500, 900, 20000] # P N B R Q K in centipawns
    score = 0
    for piece in Piece:
        # white has positive values
        score += hp.bit_count(position.pieces[Color.WHITE][piece]) * values[piece]
        # black negative
        score -= hp.bit_count(position.pieces[Color.BLACK][piece]) * values[piece]
    return score

def score_piece_placement(position, color, piece):
    # gets a bonus points for piece placement
    bb = position.pieces[color][piece]
    score = 0
    for i in range(64):
        if (bb >> np.uint8(i)) & np.uint8(1):
            # there is a piece
            rank = i // 8
            file = i % 8
            if color == Color.WHITE:
                # score for white
                square = rank*8 + file
                score += sqtb.BOARD_SCORE[piece][63-square]
            else:
                # mirrored for black
                square = (7-rank)*8 + (file)
                score -= sqtb.BOARD_SCORE[piece][63-square]
    return score

def get_score(position):
    # scores a positon for side to move
    material = get_piece_diff(position)
    placement = 0
    for piece in Piece:
        # white gets positive score
        placement += score_piece_placement(position, Color.WHITE, piece)
        # black negative
        placement += score_piece_placement(position, Color.BLACK, piece)
    return material + placement