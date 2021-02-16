from engine.square import Square
import engine.helper as hp

class Move(object):
    def __init__(self, src=None, dest=None, piece=None,
                 captured=None, promo=None, ep=False, castle=False):
        self.src = src # source square bb
        self.dest = dest # destination square bb
        self.piece = piece # piece (0-5)
        self.promo = promo # promotion piece (0-5)
        self.ep = ep # is en passant
        self.castle = castle # handle castling rights (True or False)
        self.captured = captured 
    
    def is_valid(self):
        # a move has to have a source, a destination and a piece
        if self.src != None and self.dest != None and self.piece in [0, 1, 2, 3, 4, 5]:
            return True
        return False
    
    def print_self(self):
        # prints move as a bitboard
        bb = Square(self.src).to_bitboard()
        bb |= Square(self.dest).to_bitboard()
        hp.print_bitboard(bb)
    
    def __repr__(self):
        # human readable format of a move
        source = Square(hp.lsb(self.src)).get_char()
        destination = Square(hp.lsb(self.dest)).get_char()
        return f'{source} {destination}'