import numpy as np
from engine.constants import Rank, File, Color
from engine.square import Square
import engine.helper as hp


def compute_diag_mask(i):
    # finds on which diagonal a square is
    diag = 8*(i & 7) - (i & 56)
    north = -diag & (diag >> 31)
    south = diag & (-diag >> 31)
    return (MAIN_DIAGONAL >> np.uint8(south)) << np.uint8(north)

def compute_antidiag_mask(i):
    # finds on which antidiagonal a square is
    diag = 56 - 8*(i & 7) - (i & 56)
    north = -diag & (diag >> 31)
    south = diag & (-diag >> 31)
    return (MAIN_ANTIDIAGONAL >> np.uint8(south)) << np.uint8(north)

def first_rank_attacks(sq, occ):
    # returns attack set for a given square and occupancy
    attacks = np.uint64(0)
    w = np.uint64(0)
    e = np.uint64(0)
    # right ray
    for i in range(sq, 8):
        w |= np.uint64(1) << np.uint64(i)
        if i == sq:
            w ^= (np.uint64(1) << sq)
        # if the ray is blocked
        if w & occ:
            break
    # left ray
    for i in range(sq, -1, -1):
        # if the ray is blocked
        e |= np.uint64(1) << np.uint64(i)
        if i == sq:
            e ^= (np.uint64(1) << sq)
        if e & occ:
            break
    
    attacks |= w | e
    
    return attacks ^ (np.uint64(1) << sq)
# constants required for calculations
A_FILE = np.uint64(0x0101010101010101)
FIRST_RANK = np.uint64(0x00000000000000FF)
MAIN_DIAGONAL = np.uint64(0x8040201008040201)
MAIN_ANTIDIAGONAL = np.uint64(0x0102040810204080)
# list of all ranks
RANKS = np.array(
            [FIRST_RANK << np.uint8(8*i) for i in range(8)],
            dtype=np.uint64)
# list of all files
FILES = np.array(
            [A_FILE << np.uint8(i) for i in range(8)],
            dtype=np.uint64)

RANK_MASKS = np.fromiter(
    # gets rank for each square
        (RANKS[i//8] for i in range(64)),
        dtype=np.uint64,
        count=64)

FILE_MASKS = np.fromiter(
    # gets file for each square
        (FILES[i%8] for i in range(64)),
        dtype=np.uint64,
        count=64)

DIAG_MASKS = np.fromiter(
    # gets diagonal for each square
        (compute_diag_mask(i) for i in range(64)),
        dtype=np.uint64,
        count=64)

ANTIDIAG_MASKS = np.fromiter(
    # gets antidiagonal for each square
        (compute_antidiag_mask(i) for i in range(64)),
        dtype=np.uint64,
        count=64)

MASK_64 = int('1'*64, 2)


def kindergarten_multipication(x, y):
    # 128 bit is too large, need to mask it back down to 64 bit
    return np.uint64((int(x) * int(y)) & MASK_64)


def mask_pawn_attacks(color, i):
    # gets attacks set for a pawn of a given color on a given square
    attacks = np.uint64(0)
    sq = Square(i)

    pawn = sq.to_bitboard()

    if color == Color.WHITE:
        # black is up
        ne = (pawn & ~FILES[File.H]) << np.uint(9)
        nw = (pawn & ~FILES[File.A]) << np.uint(7)
        attacks |= ne | nw
    else:
        # white is down
        sw = (pawn & ~FILES[File.A]) >> np.uint(9)
        se = (pawn & ~FILES[File.H]) >> np.uint(7)
        attacks |= se | sw
    
    return attacks

def mask_knight_attacks(i):
    # knights don't need separate colors
    attacks = np.uint64(0)
    sq = Square(i)

    knight = sq.to_bitboard()

    nnw = (knight & ~FILES[File.A]) << np.uint64(15)
    nne = (knight & ~FILES[File.H]) << np.uint64(17)
    nww = (knight & ~(FILES[File.A] | FILES[File.B])) << np.uint64(6)
    nee = (knight & ~(FILES[File.G] | FILES[File.H])) << np.uint64(10)

    ssw = (knight & ~FILES[File.A]) >> np.uint64(17)
    sse = (knight & ~FILES[File.H]) >> np.uint64(15)
    sww = (knight & ~(FILES[File.A] | FILES[File.B])) >> np.uint64(10)
    see = (knight & ~(FILES[File.G] | FILES[File.H])) >> np.uint64(6)

    attacks |= nnw | nne | nww | nee | ssw | sse | sww | see

    return attacks

def mask_king_attacks(i):
    # pseudo-legal, needs to be checked for check
    attacks = np.uint64(0)
    sq = Square(i)

    king = sq.to_bitboard()

    n = king << np.uint64(8)
    s = king >> np.uint64(8)
    w = (king & ~FILES[File.A]) >> np.uint64(1)
    e = (king & ~FILES[File.H]) << np.uint64(1)

    nw = (king & ~FILES[File.A]) << np.uint(7)
    ne = (king & ~FILES[File.H]) << np.uint(9)
    sw = (king & ~FILES[File.A]) >> np.uint(9)
    se = (king & ~FILES[File.H]) >> np.uint(7)

    attacks |= n | s | w | e | nw | ne | sw | se

    return attacks

def mask_file_attacks(i, occ):
    # gets a file attack mask for a square and occ
    sq = Square(i)
    file_index = sq.index % 8
    file = FILE_MASKS[sq.index]
    # masking to file where the square is
    blockers = file & occ
    # shifting to A file
    a_mask = blockers >> np.uint64(file_index)
    # first rank mask is mirrored
    first_rank_index = (i ^ np.uint8(56)) >> np.uint8(3)
    # mapping A file occupancy to the first rank
    first_rank_occ = kindergarten_multipication(a_mask, MAIN_DIAGONAL) >> np.uint64(56)
    # looking up attacks in the attacks table for a first rank
    attacks = FIRST_RANK_ATTACKS[first_rank_index][first_rank_occ]
    # mapping back to H file
    h_mask = kindergarten_multipication(attacks, MAIN_DIAGONAL) & FILES[File.H]
    # shifting to file where the square
    return h_mask >> np.uint8(7-file_index)

def mask_rank_attacks(sq, occ):
    # gets a rank attack mask for a square and occ
    rank_index = sq // 8
    file_index = sq % 8
    rank = RANK_MASKS[sq]
    # rank mask
    blockers = rank & occ
    # simple shift to the first rank
    first_rank_occ = blockers >> np.uint8(rank_index*8)
    # looking up attacks in the attacks table for a first rank
    attacks = FIRST_RANK_ATTACKS[file_index][first_rank_occ]
    # shifting back to the original rank
    return attacks << np.uint64(rank_index*8)

def mask_diag_attacks(sq, occ):
    # gets a diagonal mask for a given square and occ
    file_index = sq % 8
    diag = DIAG_MASKS[sq]
    # masking to a diagonal
    blockers = diag & occ
    # mapping to a first rank
    first_rank_occ = kindergarten_multipication(blockers, FILES[File.A]) >> np.uint8(56)
    # looking up attacks in the attacks table for a first rank
    attacks = FIRST_RANK_ATTACKS[file_index][first_rank_occ]
    # mapping back to diagonal
    return (attacks * FILES[File.A]) & DIAG_MASKS[sq]

def mask_antidiag_attacks(sq, occ):
    # gets an antidiagonal mask for a given square and occ
    file_index = sq % 8
    antidiag = ANTIDIAG_MASKS[sq]
    # masking to an antidiagonal
    blockers = antidiag & occ
    # mapping to a first rank
    first_rank_occ = kindergarten_multipication(blockers, FILES[File.A]) >> np.uint8(56)
    # looking up attacks in the attacks table for a first rank
    attacks = FIRST_RANK_ATTACKS[file_index][first_rank_occ]
    # mapping back to antidiagonal
    return (attacks * FILES[File.A]) & ANTIDIAG_MASKS[sq]

FIRST_RANK_ATTACKS = np.fromiter(
        (first_rank_attacks(np.uint64(i), np.uint64(occ))
            for i in range(8) # 8 squares in a rank 
            for occ in range(256)), # 2^8 = 256 possible occupancies of a rank
        dtype=np.uint8,
        count=8*256)
FIRST_RANK_ATTACKS.shape = (8,256)

PAWN_ATTACKS = np.zeros((2, 64), dtype=np.uint64)
# pawn attacks table
for color in Color:
    for i in range(64):
        # 2 colors (white, black), 64 squares
        PAWN_ATTACKS[color][i] = mask_pawn_attacks(color, i)

KNIGHT_ATTACKS = np.zeros(64, dtype=np.uint64)
# knight attacks table
for i in range(64):
    # only 64 squares, moves for both colors are the same
    KNIGHT_ATTACKS[i] = mask_knight_attacks(i)

KING_ATTACKS = np.zeros(64, dtype=np.uint64)
# king attacks table
for i in range(64):
    # like knight, need to be checked for checks
    KING_ATTACKS[i] = mask_king_attacks(i)