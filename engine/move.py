from engine.square import Square
import engine.helper as hp

class Move(object):
    def __init__(self, src, dest, piece, captured=None, promo=None, ep=None, castle=False):
        self.src = hp.lsb(src) # from (0-63)
        self.dest = hp.lsb(dest) # to (0-63)
        self.piece = piece # piece type (0-5)
        self.promo = promo # promotion piece type (0-5)
        self.ep = ep # en passant target on the next turn (0-63)
        self.castle = castle # handle castling rights (True or False)
        self.captured_piece = captured 
    
    def is_valid(self):
        # a move has to have a source, a destination and a piece
        if self.src and self.dest and self.piece in [0, 1, 2, 3, 4, 5]:
            return True
        return False
    
    def __repr__(self):
        # human readable format of a move
        return f'{Square(self.src).get_char()} {Square(self.dest).get_char()}'