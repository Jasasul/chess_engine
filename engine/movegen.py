import copy
import numpy as np
import engine.lookup_tables as tb
import engine.helper as hp
import engine.move_ordering as mord
from engine.constants import Color, Piece, Castle
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
    # checking if blocked
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
    # checking if blocked
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
        # generating under promo moves if the move is a promo; underpromo - promo to N B R
        moves.append(single)
        # checking double push
        double = gen_double_push(position, src)
        double.new_ep = single.dest
        moves.append(double)
        # checking en passant moves
        special = gen_en_passant(position)
        moves += special
    # generating attacks
    attacks = get_pawn_attacks(hp.lsb(src), position.turn)
    attacks &= position.colors[position.turn ^ 1]
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if attack & ~position.colors[position.turn]:
            move = Move(src, attack, Piece.PAWN)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attack))
    return moves

def gen_en_passant(position):
    # if there is an en passant target generate ep captures
    moves = []
    if position.ep_square != None:
        possible_squares = get_pawn_attacks(
            hp.lsb(position.ep_square),
            position.turn ^ 1)
        attacks = possible_squares & position.pieces[position.turn][Piece.PAWN]
        i = 0
        while attacks:
            attack = Square(hp.lsb(attacks)).to_bitboard()
            move = Move(attack, position.ep_square, Piece.PAWN, is_ep=True)
            moves.append(move)
            attacks = hp.clear_bit(attacks, hp.lsb(attack))
    position.ep_square = None
    
    return moves

def gen_knight_moves(position, src):
    # generates all knight moves
    moves = []
    attacks = get_knight_attacks(hp.lsb(src))
    moves += gen_moves(position, Piece.KNIGHT, src, attacks)
    
    return moves

def gen_bishop_moves(position, src):
    # generates all bishop moves
    moves = []
    attacks = get_bishop_attacks(hp.lsb(src), position.occupancy)
    moves += gen_moves(position, Piece.BISHOP, src, attacks)
    
    return moves

def gen_rook_moves(position, src):
    # generates all rook moves
    moves = []
    attacks = get_rook_attacks(hp.lsb(src), position.occupancy)
    moves += gen_moves(position, Piece.ROOK, src, attacks)
    # rook original squares
    a1 = Square(0).to_bitboard()
    a8 = Square(56).to_bitboard()
    h1 = Square(7).to_bitboard()
    h8 = Square(63).to_bitboard()
    # castling availability
    queenside = position.castle[position.turn][Castle.OOO]
    kingside = position.castle[position.turn][Castle.OO]
    # if rook moves from its original square castling to that side is no longer available
    for move in moves:
        if position.turn == Color.WHITE:
            if (move.src & a1) and queenside != 0: move.castle = Castle.OOO
            if (move.src & h1) and kingside != 0: move.castle = Castle.OO
        if position.turn == Color.BLACK:
            if (move.src & a8) and queenside != 0: move.castle = Castle.OOO
            if (move.src & h8) and kingside != 0: move.castle = Castle.OO
    
    return moves

def gen_queen_moves(position, src):
    # generates all queen moves
    moves = []
    attacks = get_queen_attacks(hp.lsb(src), position.occupancy)
    moves += gen_moves(position, Piece.QUEEN, src, attacks)
    
    return moves

def gen_king_moves(position, src):
    # generates kning moves
    moves = []
    attacks = get_king_attacks(hp.lsb(src))
    moves += (gen_moves(position, Piece.KING, src, attacks))
    
    return moves

def check_castle(position):
    # generates all castle moves available (kingside, queenside)
    moves = []
    king = position.pieces[position.turn][Piece.KING]
    
    queenside = position.castle[position.turn][Castle.OOO]
    kingside = position.castle[position.turn][Castle.OO]
    # can actually castle
    if not (queenside or kingside): return moves
    # king must not be in check
    if position.king_in_check(position.turn): return moves
    # king is not on his original square
    if position.turn == Color.WHITE and king != Square(4).to_bitboard():
        return moves
    if position.turn == Color.BLACK and king != Square(60).to_bitboard():
        return moves
    # squares between kning and rook are empty
    b = king >> np.uint(3) & ~position.occupancy
    c = king >> np.uint(2) & ~position.occupancy
    d = king >> np.uint(1) & ~position.occupancy
    g = king << np.uint(2) & ~position.occupancy
    f = king << np.uint(1) & ~position.occupancy
    if  c != 0 and d != 0:
        c_attacked = is_attacked(position, hp.lsb(c), position.turn ^ 1)
        d_attacked = is_attacked(position, hp.lsb(d), position.turn ^ 1)
    else:
        c_attacked = True
        d_attacked = True
    if g != 0 and f != 0:
        g_attacked = is_attacked(position, hp.lsb(g), position.turn ^ 1)
        f_attacked = is_attacked(position, hp.lsb(f), position.turn ^ 1)
    else:
        g_attacked = True
        f_attacked = True

    if c_attacked or d_attacked:
        queenside = 0
    if g_attacked or f_attacked:
        kingside = 0
    # generating moves if castle for the side is available
    if (b and c and d) and queenside:
        move = Move(king, c, Piece.KING, castle=Castle.OOO)
        moves.append(move)
    if (f and g) and kingside:
        move = Move(king, g, Piece.KING, castle=Castle.OO)
        moves.append(move)

    return moves

def check_capture(position, move):
    # checks if a move is a capture
   for piece in Piece:
       if move.dest & position.pieces[position.turn ^ 1][piece]:
           move.captured = piece

def gen_moves(position, piece, src, attacks):
    # generates move class instance from attack set
    moves = []
    while attacks:
        attack = Square(hp.lsb(attacks)).to_bitboard()
        if attack & ~position.colors[position.turn]:
            move = Move(src, attack, piece)
            check_capture(position, move)
            moves.append(move)
        attacks = hp.clear_bit(attacks, hp.lsb(attacks))
    
    return moves

def is_attacked(position, i, color):
    # returns if a square is attacked by a color given
    if get_pawn_attacks(i, color ^ 1) & position.pieces[color][Piece.PAWN]:
        return True
    if get_knight_attacks(i) & position.pieces[color][Piece.KNIGHT]:
        return True
    if get_king_attacks(i) & position.pieces[color][Piece.KING]:
        return True
    if get_bishop_attacks(i, position.occupancy) & position.pieces[color][Piece.BISHOP]:
        return True
    if get_rook_attacks(i, position.occupancy) & position.pieces[color][Piece.ROOK]:
        return True
    if get_queen_attacks(i, position.occupancy) & position.pieces[color][Piece.QUEEN]:
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
            # generating standard moves
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
            if piece == Piece.KING:
                moveset = gen_king_moves(position, src)
            moves += [move for move in moveset if move.is_valid()]
            piece_bb = hp.clear_bit(piece_bb, hp.lsb(src))
    
    under_promos = []
    # if move is a promo, we must add 4 under promotoin moves (knight to rook)
    for move in moves:
        if move.piece == Piece.PAWN:
            if move.dest & tb.RANKS[7 - position.turn*7]:
                move.promo = Piece.QUEEN
                for piece in Piece:
                    if piece == Piece.PAWN: continue # a pawn cannot promote to a pawn
                    if piece == Piece.QUEEN: break # the original promo move is a queen promo
                    promo_copy = copy.deepcopy(move) # copying the move
                    promo_copy.promo = piece # new piece
                    under_promos.append(promo_copy)
    moves += under_promos
    # generating castle moves
    moves += [move for move in check_castle(position) if move.is_valid()]

    # scoring a move to improve alpha beta pruning
    for move in moves:
        mord.score_move(move)
    ordered = sorted(moves, key=lambda move: move.score, reverse=True)

    return ordered

def get_legal_moves(position):
    # return only legal moves
    legal_moves = []
    for move in generate_moves(position):
        new_position = position.copy_make(move)
        if not new_position.king_in_check(new_position.turn ^ 1):
            legal_moves.append(move)
    return legal_moves
