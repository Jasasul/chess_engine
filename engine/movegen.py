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
    if get_pawn_attacks(i, color) & position.pieces[color ^ 1][Piece.PAWN]: return True
    if get_knight_attacks(i) & position.pieces[color][Piece.KNIGHT]: return True
    if get_king_attacks(i) & position.pieces[color][Piece.KING]: return True
    if get_bishop_attacks(i, board.occupancy) & position.pieces[color][Piece.BISHOP]: return True
    if get_rook_attacks(i, board.occupancy) & position.pieces[color][Piece.ROOK]: return True
    if get_queen_attacks(i, board.occupancy) & position.pieces[color][Piece.QUEEN]: return True

    return False

def generate_moves(position):
    movelist = []
    for piece in Piece:
        bb = position.pieces[position.turn][piece]
        while bb:
            i = hp.lsb(bb)
            bb = hp.clear_bit(bb, i)
            if piece == Piece.PAWN:
                pawn = Square(i).to_bitboard()
                # single push moves
                if position.turn == Color.WHITE:
                    single_push = (pawn << np.uint8(8)) & ~position.occupancy
                elif position.turn == Color.BLACK:
                    single_push = (pawn >> np.uint8(8)) & ~position.occupancy
                # single push available
                if single_push != 0:
                    single = Move(i, hp.lsb(single_push), Piece.PAWN)
                    # promotion handling
                    if Square(single.dest).to_bitboard() & tb.RANKS[7 - position.turn*7]:
                        single.promo = Piece.QUEEN
                    # we can double push only if 2 squares in front of the pawn are empty
                    if position.turn == Color.WHITE:
                        double_push = ((pawn & tb.RANKS[(position.turn * 5) + 1]) << np.uint8(16)) & ~position.occupancy
                    elif position.turn == Color.BLACK:
                        double_push = ((pawn & tb.RANKS[(position.turn * 5) + 1]) >> np.uint8(16)) & ~position.occupancy
                    # there is a double push
                    if double_push != 0:
                        # en passant target is set to the pawn's single push (there must be a single push if double is available)
                        double = Move(i, hp.lsb(double_push), Piece.PAWN, ep=hp.lsb(single_push))
                        movelist.append(double)
                    movelist.append(single)
                    # pawn attacks only available if there is an enemy piece to SW or SE
                pawn_attacks = get_pawn_attacks(i, position.turn)
                # en passant handling
                if position.en_passant != None:
                    if pawn_attacks & Square(position.en_passant).to_bitboard():
                        move = Move(i, position.en_passant, Piece.PAWN, captured_piece=Piece.PAWN)
                        movelist.append(move)
                        pawn_attacks = hp.clear_bit(pawn_attacks, hp.lsb(position.en_passant))
                # check for attacked enemy pieces
                pawn_attacks = pawn_attacks & position.colors[position.turn ^ 1]
                # max 2 attacks (including en passant)
                while pawn_attacks:
                    attacked_square = Square(hp.lsb(pawn_attacks))
                    for attacked_piece in Piece:
                        # finds what piece is attacked
                        if position.pieces[position.turn ^ 1][attacked_piece] & attacked_square.to_bitboard():
                            attack = Move(i, hp.lsb(pawn_attacks), Piece.PAWN, captured_piece=attacked_piece)
                            movelist.append(attack)
                    pawn_attacks = hp.clear_bit(pawn_attacks, attacked_square.index)
                    
            if piece == Piece.KNIGHT:
                attacks = get_knight_attacks(i) & ~position.colors[position.turn]
                while attacks:
                    attacked_square = Square(hp.lsb(attacks))
                    attacks = hp.clear_bit(attacks, attacked_square.index)
                    move = Move(i, attacked_square.index, Piece.KNIGHT)
                    for piece in Piece:
                        if Square(move.dest).to_bitboard() & position.colors[position.turn ^ 1]:
                            move.captured_piece = piece
                    movelist.append(move)
        
    return movelist