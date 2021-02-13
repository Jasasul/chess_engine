import numpy as np
import engine.lookup_tables as tb
import engine.helper as hp
from engine.chessboard import Chessboard
from engine.constants import Color, Piece, Rank
from engine.square import Square
from engine.move import Move

def get_pawn_attacks(i, color):
    # looks up pawn attack set in an attack table
    return tb.PAWN_ATTACKS[color][i]

def get_knight_attacks(i):
    # looks up knight attack set in an attack table
    return tb.KNIGHT_ATTACKS[i]

def get_king_attacks(i):
    # looks up king attacks set in an attack table
    return tb.KING_ATTACKS[i]

def get_bishop_attacks(i, occ):
    # calculates diagonal and antidiagonal moves
    attacks = np.uint64(0)

    diag = tb.mask_diag_attacks(i, occ)
    antidiag = tb.mask_antidiag_attacks(i, occ)

    attacks |= diag | antidiag

    return attacks

def get_rook_attacks(i, occ):
    # calculates file and rank moves
    attacks = np.uint64(0)

    rank = tb.mask_rank_attacks(i, occ)
    file = tb.mask_file_attacks(i, occ)

    attacks |= rank | file
    
    return attacks

def get_queen_attacks(i, occ):
    # combines bishop and rook attacks
    attacks = np.uint64(0)

    bishop = get_bishop_attacks(i, occ)
    rook = get_rook_attacks(i, occ)

    attacks |= rook | bishop

    return attacks

def is_attacked(position, i, color):
    # returns if a square is attacked by a color given
    if get_pawn_attacks(i, color) & position.pieces[color ^ 1][Piece.PAWN]:
        return True
    if get_knight_attacks(i) & position.pieces[color][Piece.KNIGHT]:
        return True
    if get_king_attacks(i) & position.pieces[color][Piece.KING]:
        return True
    if get_bishop_attacks(i, board.occupancy) & position.pieces[color][Piece.BISHOP]:
        return True
    if get_rook_attacks(i, board.occupancy) & position.pieces[color][Piece.ROOK]:
        return True
    if get_queen_attacks(i, board.occupancy) & position.pieces[color][Piece.QUEEN]:
        return True

    return False

def gen_single_push(position, src):
    # generates a single push for a src square
    if position.turn == Color.WHITE:
        single_push = (src << np.uint8(8)) & ~position.occupancy
    elif position.turn == Color.BLACK:
        single_push = (src >> np.uint8(8)) & ~position.occupancy
    
    if single_push:
        move = Move(src, single_push, Piece.PAWN)
    return move

def gen_double_push(position, src):
    # generates a double push from src square
    # original - 1st for W, 7th for B
    on_original_rank = src & tb.RANKS[(position.turn*5) + 1] 
    if position.turn == Color.WHITE:
        double_push = on_original_rank << np.uint8(16) & ~position.occupancy
    elif position.turn == Color.BLACK:
        double_push = on_original_rank >> np.uint8(16) & ~position.occupancy
    
    if double_push:
        move = Move(src, double_push, Piece.PAWN)
    
    return move

def gen_pawn_capture(position, src):
    # generates pawn captures from src square
    captures = []
    pawn_attacks = get_pawn_attacks(hp.lsb(src), position.turn)
    while pawn_attacks:
        dest = Square(hp.lsb(pawn_attacks))
        for piece in Piece:
            if dest.to_bitboard() & position.pieces[position.turn ^ 1][piece]:
                move = Move(src,
                            dest.to_bitboard(),
                            Piece.PAWN,
                            captured=piece)
                captures.append(move)
        pawn_attacks = hp.clear_bit(pawn_attacks, dest.index)
    
    return captures

def check_en_passant(position, src):
    # creates an en passant move if available
    pawn_attacks = get_pawn_attacks(hp.lsb(src), position.turn)
    en_passant = pawn_attacks & position.en_passant.to_bitboard()
    move = Move(src, en_passant, Piece.PAWN)
    return move

def gen_pawn_moves(position, pawn):
    # generates all pawn moves for the side to move
    moves = []
    enp = None
    single = gen_single_push(position, pawn)
    if single:
        moves.append(single)
        if Square(single.dest).to_bitboard() & tb.RANKS[7 - position.turn*7]:
            single.promo = Piece.QUEEN
        double = gen_double_push(position, pawn)
        if double:
            double.ep = single.dest # if double push, setting en passant for the next move
            moves.append(double)
    captures = gen_pawn_capture(position, pawn)
    for capture in captures:
        moves.append(capture)
    if position.en_passant: 
        enp = check_en_passant(position, pawn)
        moves.append(enp)

    return moves

def check_capture(position, move):
    # checks if a piece move destination is a capture
    for piece in Piece:
        if Square(move.dest).to_bitboard() & position.pieces[position.turn ^ 1][piece]:
            move.captured = piece

def gen_knight_moves(position, src):
    # generates all moves for a knigth
    moves = []
    attacks = get_knight_attacks(hp.lsb(src))
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if not attack & position.colors[position.turn]:
            move = Move(src, attack, Piece.KNIGHT)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attack))
    return moves

def generate_moves(position):
    # generates moves for all pieces on all squares for a side to move
    moves = []
    for piece in Piece:
        piece_bb = position.pieces[position.turn][piece]
        while piece_bb:
            moveset = []
            src = Square(hp.lsb(piece_bb))

            if piece == Piece.PAWN:
                moveset = gen_pawn_moves(position, src.to_bitboard())
            if piece == Piece.KNIGHT:
                moveset = gen_knight_moves(position, src.to_bitboard())

            for move in moveset:
                if move.is_valid():
                    moves.append(move)

            piece_bb = hp.clear_bit(piece_bb, src.index)
    
    return moves