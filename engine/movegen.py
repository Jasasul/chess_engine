import numpy as np
import lookup_tables as tb
import helper as hp
from chessboard import Chessboard
from constants import Color
import time

def get_pawn_attacks(color, i):
    return tb.PAWN_ATTACKS[color][i]

def get_knight_attacks(i):
    return tb.KNIGHT_ATTACKS[i]

def get_king_attacks(i):
    return tb.KING_ATTACKS[i]

def get_bishop_attacks(i, occ):
    attacks = np.uint64(0)

    diag = tb.mask_diag_attacks(i, occ)
    antidiag = tb.mask_antidiag_attacks(i, occ)

    attacks |= diag | antidiag

    return attacks

def get_rook_attacks(i, occ):
    attacks = np.uint64(0)

    rank = tb.mask_rank_attacks(i, occ)
    file = tb.mask_file_attacks(i, occ)

    attacks |= rank | file
    
    return attacks

def get_queen_attacks(i, occ):
    attacks = np.uint64(0)

    bishop = get_bishop_attacks(i, occ)
    rook = get_rook_attacks(i, occ)

    attacks |= rook | bishop

    return attacks

board = Chessboard()