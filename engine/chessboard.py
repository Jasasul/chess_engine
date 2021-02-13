import numpy as np
import engine.helper as hp
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
        self.castle = np.zeros(4, dtype=np.uint64)
        self.en_passant = None
        self.halfmove = np.uint64(0)
        self.fullmove = np.uint64(0)
        self.start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def set_board(self, fen):
        # sets a chessboard object according a fen string
        self.pieces = np.zeros((2, 6), dtype=np.uint64)
        self.colors = np.zeros(2, dtype=np.uint64)
        self.occupancy = np.uint64(0)
        self.turn = np.uint64(0)
        self.castle = np.zeros(4, dtype=np.uint64)
        self.enpassant = False
        self.halfmove = np.uint64(0)
        self.fullmove = np.uint64(0)

        fen_parts = fen.split()
        rank = 7
        file = 0
        fen_index = 0
        # setting up pieces
        # P N B R Q K for white
        # p n b r q k for black
        for char in fen_parts[0]:
            # fen goes from 8th to 1st rank (white perspective)
            # from A to H file
            sq = Square(8*rank + file)
            if char >= '1' and char <= '8':
                # empty square (1-8)
                file += int(char)
            if char.upper() in self.piece_chars:
                # there is a piece
                # set it to its bitboard
                if char.isupper():
                    # white piece
                    bitboard = hp.set_bit(
                        self.pieces[Color.WHITE][self.piece_chars.index(char)],
                        sq.index)
                    self.pieces[Color.WHITE][self.piece_chars.index(char)] = bitboard
                if char.islower():
                    # black piece
                    bitboard = hp.set_bit(
                        self.pieces[Color.BLACK][self.piece_chars.index(char.upper())],
                        sq.index)
                    self.pieces[Color.BLACK][self.piece_chars.index(char.upper())] = bitboard
                file += 1
            # end of a rank reached
            # new rank from 7 to 0 (8 to 1)
            if file > 7:
                file = 0
                rank -= 1
        # side to move w-white b-black
        if fen_parts[1] == 'w':
            self.turn = Color.WHITE
        elif fen_parts[1] == 'b':
            self.turn = Color.BLACK
        # castling availability: K-king side white, Q-queen side white
        #                        k-king side black, q-queen side black
        for char in fen_parts[2]:
            if char in self.castle_chars:
                self.castle[self.castle_chars.index(char)] = 1
        # en passant target square if any
        if fen_parts[3] != '-':
            self.en_passant = Square(Square.get_index(fen_parts[3]))
        # halfmove clock - 50 moves rule
        self.halfmove = fen_parts[4]
        # fullmove clock
        self.fullmove = fen_parts[5]
        # bitboard for all pieces of one color
        for color in Color:
            for piece in Piece:
                self.colors[color] |= self.pieces[color][piece]
        # total occupancy
        for color in Color:
            self.occupancy |= self.colors[color]