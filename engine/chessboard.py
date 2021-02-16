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
        self.move_list = []

    def reset(self):
        # resets all properties of the position obj
        self.pieces = np.zeros((2, 6), dtype=np.uint64)
        self.colors = np.zeros(2, dtype=np.uint64)
        self.occupancy = np.uint64(0)
        self.turn = np.uint64(0)
        self.castle = np.zeros(4, dtype=np.uint64)
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
            if char in self.castle_chars:
                self.castle[self.castle_chars.index(char)] = 1
        # en passant target square if any
        if ep_fen != '-':
            self.en_passant = Square(Square.get_index(ep_fen))
    
    def set_move_clock(self, half_fen, full_fen):
        # sets halfmove and fullmove clock
        self.halfmove = half_fen
        self.fullmove = full_fen
    
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

        fen_parts = fen.split()

        self.set_pieces(fen_parts[0])
        self.set_side(fen_parts[1])
        self.set_special(fen_parts[2], fen_parts[3])
        self.set_move_clock(fen_parts[4], fen_parts[5])
        self.bb_adjust()
    
    def make_move(self, move):
        # makes a move on internal chessboard
        self.pieces[self.turn][move.piece] ^= move.src | move.dest
        if move.captured != None:
            self.pieces[self.turn ^ 1][move.captured] ^= move.dest
        self.bb_adjust()
        self.turn ^= 1
        hp.print_bitboard(self.pieces[self.turn][move.captured])