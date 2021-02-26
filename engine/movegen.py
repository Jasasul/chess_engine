import copy
import numpy as np
import engine.lookup_tables as tb
import engine.helper as hp
import engine.chessboard as cb
from engine.constants import Color, Piece, Rank, Castle
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
    
    if move.dest & tb.RANKS[7 - 7*position.turn]:
        move.promo = Piece.QUEEN
    
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
        # generating under promo moves if the move is a promo
        if single.promo != None:
            for piece in Piece:
                if piece == Piece.PAWN:
                    continue
                if piece == Piece.QUEEN:
                    break
                promo_move = copy.deepcopy(single)
                promo_move.promo = piece
                moves.append(promo_move)
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
    # if there is an en passant target generate ep moves
    moves = []
    if position.ep_square != None:
        possible_squares = get_pawn_attacks(
            hp.lsb(position.ep_square),
            position.turn ^ 1)
        attacks = possible_squares & position.pieces[position.turn][Piece.PAWN]
        while attacks:
            attack = Square(hp.lsb(attacks)).to_bitboard()
            move = Move(attack, position.ep_square, Piece.PAWN, is_ep=True)
            moves.append(move)
            attacks = hp.clear_bit(attacks, hp.lsb(attack))
    
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
    king = position.pieces[position.turn][Piece.KING]
    moves = []
    king_side = Move()
    queen_side = Move()
    # squares must be empty
    f_square = king << np.uint8(1)
    g_square = king << np.uint8(2)
    d_square = king >> np.uint8(1)
    c_square = king >> np.uint8(2)
    b_square = king >> np.uint8(3)

    f_empty = f_square & ~position.occupancy
    g_empty = g_square & ~position.occupancy
    d_empty = d_square & ~position.occupancy
    c_empty = c_square & ~position.occupancy
    b_empty = b_square & ~position.occupancy
    # squares must not be under attack
    f_attacked = is_attacked(position, hp.lsb(f_square), position.turn ^ 1)
    g_attacked = is_attacked(position, hp.lsb(g_square), position.turn ^ 1)
    d_attacked = is_attacked(position, hp.lsb(d_square), position.turn ^ 1)
    c_attacked = is_attacked(position, hp.lsb(c_square), position.turn ^ 1)
    b_attacked = is_attacked(position, hp.lsb(b_square), position.turn ^ 1)
    # kingside and queenside castle
    if position.castle[position.turn][Castle.OO]:
        if f_empty and g_empty:
            if not(f_attacked or g_attacked):
                king_side.src = king
                king_side.dest = g_square
                king_side.piece = Piece.KING
                king_side.castle = Castle.OO
                moves.append(king_side)
    if position.castle[position.turn][Castle.OOO]:
        if d_empty and c_empty and b_empty:
            if not(d_attacked or c_attacked or b_attacked):
                queen_side.src = king
                queen_side.dest = c_square
                queen_side.piece = Piece.KING
                queen_side.castle = Castle.OOO
                moves.append(queen_side)
    return moves

def check_capture(position, move):
    # checks if a move is a capture
   for piece in Piece:
       if move.dest & position.pieces[position.turn ^ 1][piece]:
           move.captured = piece

def gen_moves(position, piece, src, attacks):
    # generates move from attack set
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
    if get_pawn_attacks(i, color) & position.pieces[color ^ 1][Piece.PAWN]:
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

def is_legal(position, move):
    # move is illegal if it leaves king in check
    test_board = cb.Chessboard()
    test_board.set_board(position.fen)
    test_board.make_move(move)
    if move.piece == Piece.PAWN:
        pass
    king = test_board.pieces[position.turn][Piece.KING]
    attacked = is_attacked(test_board, hp.lsb(king), position.turn ^ 1)

    return not attacked

def generate_moves(position):
    # generates moves for all pieces on all squares for a side to move
    moves = []
    can_castle = False
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
    # generating castle moves
    for castle in Castle:
        if position.castle[position.turn][castle]:
            can_castle = True
    if can_castle:
        moves += [move for move in check_castle(position) if move.is_valid()]

    king = position.pieces[position.turn][Piece.KING]
    legal_moves = [move for move in moves if is_legal(position, move)]

    return legal_moves