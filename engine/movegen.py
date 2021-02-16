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
    # calculates diagonal and antidiagonal attacks
    attacks = np.uint64(0)

    diag = tb.mask_diag_attacks(i, occ)
    antidiag = tb.mask_antidiag_attacks(i, occ)

    attacks |= diag | antidiag

    return attacks

def get_rook_attacks(i, occ):
    # calculates file and rank attacks
    attacks = np.uint64(0)

    rank = tb.mask_rank_attacks(i, occ)
    file = tb.mask_file_attacks(i, occ)

    attacks |= rank | file
    attacks ^= Square(i).to_bitboard()
    
    return attacks

def get_queen_attacks(i, occ):
    # combines bishop and rook attacks
    attacks = np.uint64(0)

    bishop = get_bishop_attacks(i, occ)
    rook = get_rook_attacks(i, occ)

    attacks |= rook | bishop

    return attacks

def gen_single_push(position, src):
    # creates a single pudh move if available
    move = Move()
    if position.turn == Color.WHITE:
        single_push = src << np.uint64(8)
    elif position.turn == Color.BLACK:
        single_push = src >> np.uint64(8)
    
    if single_push & ~position.occupancy:
        move.src = src
        move.dest = single_push
        move.piece = Piece.PAWN
    
    return move

def gen_double_push(position, src):
    # creates a double push move if available
    move = Move()
    if position.turn == Color.WHITE:
        double_push = src << np.uint64(16)
    elif position.turn == Color.BLACK:
        double_push = src >> np.uint64(16)
    
    if not src & tb.RANKS[(position.turn*5) + 1]:
        double_push = np.uint64(0)
    
    if double_push & ~position.occupancy:
        move.src = src
        move.dest = double_push
        move.piece = Piece.PAWN
    
    return move

def gen_pawn_moves(position, src):
    # generates all pawn moves
    moves = []
    single = gen_single_push(position, src)
    if single.is_valid():
        moves.append(single)
        double = gen_double_push(position, src)
        moves.append(double)
        special = gen_en_passant(position)
        moves += special
    return moves

def gen_en_passant(position):
    # if there is an en passant target generate ep moves
    moves = []
    if position.en_passant != None:
        possible_squares = get_pawn_attacks(
            hp.lsb(position.en_passant),
            position.turn ^ 1)
        attacks = possible_squares & position.pieces[position.turn][Piece.PAWN]
        while attacks:
            attack = Square(hp.lsb(attacks)).to_bitboard()
            move = Move(attack, position.en_passant, Piece.PAWN, ep=True)
            moves.append(move)
            attacks = hp.clear_bit(attacks, hp.lsb(attack))
    
    return moves

def gen_knight_moves(position, src):
    # generates all knight moves
    moves = []
    attacks = get_knight_attacks(hp.lsb(src))
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if attack & ~position.colors[position.turn]:
            move = Move(src, attack, Piece.KNIGHT)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attack))
    
    return moves

def gen_bishop_moves(position, src):
    # generates all bishop moves
    moves = []
    attacks = get_bishop_attacks(hp.lsb(src), position.occupancy)
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if attack & ~position.colors[position.turn]:
            move = Move(src, attack, Piece.BISHOP)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attacks))
    
    return moves

def gen_rook_moves(position, src):
    # generates all rook moves
    moves = []
    attacks = get_rook_attacks(hp.lsb(src), position.occupancy)
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if attack & ~position.colors[position.turn]:
            move = Move(src, attack, Piece.ROOK)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attacks))
    
    return moves

def gen_queen_moves(position, src):
    # generates all queen moves
    moves = []
    attacks = get_queen_attacks(hp.lsb(src), position.occupancy)
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if attack & ~position.colors[position.turn]:
            move = Move(src, attack, Piece.QUEEN)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attacks))
    
    return moves

def check_capture(position, move):
    # checks if a move is a capture
   for piece in Piece:
       if move.dest & position.pieces[position.turn ^ 1][piece]:
           move.captured = piece

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

def generate_moves(position):
    # generates moves for all pieces on all squares for a side to move
    moves = []
    for piece in Piece:
        piece_bb = position.pieces[position.turn][piece]
        while piece_bb:
            moveset = []
            src = Square(hp.lsb(piece_bb)).to_bitboard()

            if piece == Piece.PAWN:
                moveset = gen_pawn_moves(position, src)
            if piece == Piece.KNIGHT:
                moveset = gen_knight_moves(position, src)
            if piece == Piece.BISHOP:
                moveset = gen_bishop_moves(position, src)
            if piece == Piece.ROOK:
                moveset = gen_rook_moves(position, src) 
            if piece == Piece.QUEEN:
                moveset = gen_queen_moves(position, src)

            for move in moveset:
                if move.is_valid():
                    moves.append(move)

            piece_bb = hp.clear_bit(piece_bb, hp.lsb(src))
    
    return moves