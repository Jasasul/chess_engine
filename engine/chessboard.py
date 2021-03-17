import numpy as np
import copy
import engine.helper as hp
import engine.movegen as mg
from engine.constants import Color, Piece, Castle
from engine.square import Square


class Chessboard(object):
    def __init__(self):
        self.piece_chars = ['P', 'N', 'B', 'R', 'Q', 'K'] # for fen
        self.castle_chars = ['K', 'Q', 'k', 'q'] # for fen
        self.pieces = np.zeros((2, 6), dtype=np.uint64) # one for each piece type 2 colors
        self.colors = np.zeros(2, dtype=np.uint64) # total pieces for 2 colors
        self.occupancy = np.uint64(0) # total pieces on board
        self.turn = np.uint64(0) # white or black
        self.castle = np.zeros((2, 2), dtype=np.uint64) # kindside and queenside for white and black
        self.ep_square = None # en passant target square
        self.halfmove = np.uint64(0) # halfmove clock
        self.fullmove = np.uint64(0) # fullmove clock
        self.fen = None # position in string format
        self.move_list = [] # what moves has been played up to now

    def reset(self):
        # resets all properties of the position obj
        self.fen = None
        self.pieces = np.zeros((2, 6), dtype=np.uint64)
        self.colors = np.zeros(2, dtype=np.uint64)
        self.occupancy = np.uint64(0)
        self.turn = np.uint64(0)
        self.castle = np.zeros((2, 2), dtype=np.uint64)
        self.ep_square = None
        self.halfmove = np.uint64(0)
        self.fullmove = np.uint64(0)
    
    def set_pieces(self, piece_fen):
        # sets bitboards
        rank = 7
        file = 0
        fen_index = 0
        for char in piece_fen:
            # fen goes from 8th to 1st rank (white perspective)
            # from A to H file
            sq = Square(8*rank + file)
            if char >= '1' and char <= '8':
                # empty square (1-8)
                file += int(char)
            if char.upper() in self.piece_chars:
                # there is a piece
                piece = self.piece_chars.index(char.upper())
                self.add_to_bb(char, sq, piece)
                file += 1
            # end of a rank reached (8 -> 1)
            if file > 7:
                file = 0
                rank -= 1
    
    def add_to_bb(self, char, sq, piece):
        # adds a piece to its bitboard
        if char.isupper():
            # white piece
            bitboard = hp.set_bit(self.pieces[Color.WHITE][piece], sq.index)
            self.pieces[Color.WHITE][piece] = bitboard
        if char.islower():
            # black piece
            bitboard = hp.set_bit(self.pieces[Color.BLACK][piece], sq.index)
            self.pieces[Color.BLACK][piece] = bitboard
    
    def set_side(self, side_fen):
        # sets side to move
        if side_fen == 'w':
            self.turn = Color.WHITE
        elif side_fen == 'b':
            self.turn = Color.BLACK
    
    def set_special(self, castle_fen, ep_fen):
        # castling availability: K-king side white, Q-queen side white
        #                        k-king side black, q-queen side black
        for char in castle_fen:
            if char == 'K':
                self.castle[Color.WHITE][Castle.OO] = 1
            if char == 'Q':
                self.castle[Color.WHITE][Castle.OOO] = 1
            if char == 'k':
                self.castle[Color.BLACK][Castle.OO] = 1
            if char == 'q':
                self.castle[Color.BLACK][Castle.OOO] = 1
        # en passant target square if any
        if ep_fen != '-':
            self.ep_square = Square(Square.from_str(ep_fen)).to_bitboard()
    
    def set_move_clock(self, half_fen, full_fen):
        # sets halfmove and fullmove clock
        self.halfmove = int(half_fen)
        self.fullmove = int(full_fen)
    
    def bb_adjust(self):
        # sets up helper bitboards from piece bb
        # one for each color and one for total occupancy
        self.colors = np.zeros(2, dtype=np.uint64)
        self.occupancy = np.uint64(0)
        for color in Color:
            for piece in Piece:
                self.colors[color] |= self.pieces[color][piece]
        for color in Color:
            self.occupancy |= self.colors[color]

    def set_board(self, fen):
        # sets a chessboard object according to the FEN given
        self.reset()
        self.fen = fen

        fen_parts = fen.split()
        # piece placement
        self.set_pieces(fen_parts[0])
        # side to move
        self.set_side(fen_parts[1])
        # castling rights and en passant
        self.set_special(fen_parts[2], fen_parts[3])
        # halfmoves and fullmoves
        self.set_move_clock(fen_parts[4], fen_parts[5])
        # updates helper bitboards
        self.bb_adjust()
    
    
    def make_ep(self, move):
        # makes en passant move
        if self.turn == Color.WHITE:
            target = move.dest >> np.uint8(8)
        if self.turn == Color.BLACK:
            target = move.dest << np.uint8(8)
        self.pieces[self.turn ^ 1][Piece.PAWN] ^= target
    
    def make_castle(self, move):
        # makes a castle move for the rooks
        a1 = Square(0).to_bitboard()
        a8 = Square(56).to_bitboard()
        h1 = Square(7).to_bitboard()
        h8 = Square(63).to_bitboard()
        if self.turn == Color.WHITE:
            # moving rook for white
            if move.castle == Castle.OOO:
                self.pieces[self.turn][Piece.ROOK] ^= a1
                self.pieces[self.turn][Piece.ROOK] |= a1 << np.uint(3)
            if move.castle == Castle.OO:
                self.pieces[self.turn][Piece.ROOK] ^= h1
                self.pieces[self.turn][Piece.ROOK] |= h1 >> np.uint(2)
        if self.turn == Color.BLACK:
            # moving rooks for black
            if move.castle == Castle.OOO:
                self.pieces[self.turn][Piece.ROOK] ^= a8
                self.pieces[self.turn][Piece.ROOK] |= a8 << np.uint(3)
            if move.castle == Castle.OO:
                self.pieces[self.turn][Piece.ROOK] ^= h8
                self.pieces[self.turn][Piece.ROOK] |= h8 >> np.uint(2)


    
    def make_move(self, move):
        # makes a move using copy/make approach
        self.pieces[self.turn][move.piece] ^= move.src
        self.pieces[self.turn][move.piece] |= move.dest
        # capture handling
        if move.captured != None:
            self.pieces[self.turn ^ 1][move.captured] ^= move.dest
        # promo handling
        if move.promo != None:
            self.pieces[self.turn][move.promo] |= move.dest
            self.pieces[self.turn][Piece.PAWN] ^= move.dest
        # en passant capture handling
        if move.is_ep:
            self.make_ep(move)
        self.ep_square = move.new_ep
        # castle handling
        if move.piece == Piece.ROOK and move.castle != None:
            self.castle[self.turn][move.castle] = 0
        if move.piece == Piece.KING:
            self.castle[self.turn][Castle.OO] = 0
            self.castle[self.turn][Castle.OOO] = 0
            if move.castle != None:
                self.make_castle(move)
        self.bb_adjust()
        self.move_list.append(move)
        # move clock - halfmove is every move which is not a capture or pawn move
        self.halfmove += 1
        if self.turn == Color.BLACK:
            # one fullmove is after both sides moved - 1 fullmove = 2 halfmoves
            self.fullmove += 1
        # opponents turn
        self.turn ^= 1
    
    def copy_make(self, move):
        # copies itself and makes a move in the copy
        new_position = copy.deepcopy(self)
        new_position.make_move(move)
        return new_position
    
    def king_in_check(self, color):
        # returns if a given color's king is in check in current position
        king = self.pieces[color][Piece.KING]
        return mg.is_attacked(self, hp.lsb(king), color ^ 1)

    def is_legal(self):
        if self.king_in_check(self.turn ^ 1):
            return False
        return True
    
    def get_game_status(self):
        # if game ended, there is no point in searching
        test_board = copy.deepcopy(self)
        legal_moves = mg.get_legal_moves(test_board)
        # Checkmate - no moves and check; Draw - no moves and no check
        # we have to check for both sides
        if len(legal_moves) == 0:
            if test_board.king_in_check(test_board.turn):
                return 'Checkmate'
            return 'Draw'
        test_board.turn ^= 1 # other side
        legal_moves = mg.get_legal_moves(test_board)
        if len(legal_moves) == 0:
            if test_board.king_in_check(test_board.turn):
                return 'Checkmate'
            return 'Draw'
        return 'Valid'