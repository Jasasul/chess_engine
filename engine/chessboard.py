import numpy as np
import engine.helper as hp
import engine.lookup_tables as tb
from engine.constants import Color, Rank, File, Piece, Castle
from engine.square import Square


class Chessboard(object):
    def __init__(self):
        self.piece_chars = ['P', 'N', 'B', 'R', 'Q', 'K']
        self.castle_chars = ['K', 'Q', 'k', 'q']
        self.pieces = np.zeros((2, 6), dtype=np.uint64)
        self.colors = np.zeros(2, dtype=np.uint64)
        self.occupancy = np.uint64(0)
        self.turn = np.uint64(0)
        self.castle = np.zeros((2, 2), dtype=np.uint64)
        self.en_passant = None
        self.halfmove = np.uint64(0)
        self.fullmove = np.uint64(0)
        self.fen = None
        self.move_list = []

    def reset(self):
        # resets all properties of the position obj
        self.fen = None
        self.pieces = np.zeros((2, 6), dtype=np.uint64)
        self.colors = np.zeros(2, dtype=np.uint64)
        self.occupancy = np.uint64(0)
        self.turn = np.uint64(0)
        self.castle = np.zeros((2, 2), dtype=np.uint64)
        self.enpassant = False
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
            self.en_passant = Square(Square.get_index(ep_fen)).to_bitboard()
    
    def set_move_clock(self, half_fen, full_fen):
        # sets halfmove and fullmove clock
        self.halfmove = int(half_fen)
        self.fullmove = int(full_fen)
    
    def bb_adjust(self):
        # sets up helper bitboards from piece bb
        # one for each color and one for total occupancy
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

        self.set_pieces(fen_parts[0])
        self.set_side(fen_parts[1])
        self.set_special(fen_parts[2], fen_parts[3])
        self.set_move_clock(fen_parts[4], fen_parts[5])
        self.bb_adjust()
    
    def set_en_passant(self, move):
        # if the move is double push, sets single push as en passant target square
        if move.piece == Piece.PAWN:
            if self.turn == Color.WHITE:
                double = move.dest & (move.src << np.uint(16))
                if double:
                    self.en_passant = move.src << np.uint(8)
            if self.turn == Color.BLACK:
                double = move.dest & (move.src >> np.uint(16))
                if double:
                    self.en_passant = move.src >> np.uint(8)
    
    def set_castle(self, move):
        # if a king or a rook moves form their original square
        # that side castle right is lost
        a1 = Square(0).to_bitboard()
        h1 = Square(7).to_bitboard()
        a8 = Square(56).to_bitboard()
        h8 = Square(63).to_bitboard()

        if move.piece == Piece.ROOK:
            # if a rook moves from its original position
            # that side castle is disabled
            if (move.src & a1) or (move.src & a8):
                self.castle[self.turn][Castle.OOO] = 0
            if (move.src & h1) or (move.src & h8):
                self.castle[self.turn][Castle.OO] = 0
        
        if move.piece == Piece.KING:
            # if a king moves from its original square
            # then the side looses all castling rights
            self.castle[self.turn][Castle.OO] = 0
            self.castle[self.turn][Castle.OOO] = 0
    
    def make_castle(self, move):
        # if a move is a castle, move a rook accodringly
        a_rook = self.pieces[self.turn][Piece.ROOK] & tb.FILES[File.A]
        h_rook = self.pieces[self.turn][Piece.ROOK] & tb.FILES[File.H]
        # kingside castle - rook on H file is moved
        if move.castle == Castle.OO:
            castled = h_rook >> np.uint8(2) 
            self.pieces[self.turn][Piece.ROOK] ^= h_rook
            self.pieces[self.turn][Piece.ROOK] ^= castled
        # queenside caslte - rook on A file is moved1
        if move.castle == Castle.OOO:
            castled = a_rook << np.uint8(3) 
            self.pieces[self.turn][Piece.ROOK] ^= a_rook
            self.pieces[self.turn][Piece.ROOK] ^= castled


    def make_move(self, move):
        # makes a move on internal chessboard
        self.pieces[self.turn][move.piece] ^= move.src | move.dest
        if move.captured != None:
            self.pieces[self.turn ^ 1][move.captured] ^= move.dest
        self.bb_adjust()
        self.set_en_passant(move)
        if move.piece == Piece.KING or move.piece == Piece.ROOK:
            self.set_castle(move)
        if move.castle != None:
            self.make_castle(move)
        # the 50 move rule - if a moveblack or white is not a capture
        # or a pawn move for 50 turns the game is considered draw
        self.halfmove += 1
        if move.piece == Piece.PAWN or move.captured != None:
            halfmove = 0
        # a full move consist of white and black move
        if self.turn == Color.BLACK:
            self.fullmove += 1
        self.turn ^= 1