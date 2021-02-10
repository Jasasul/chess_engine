from square import Square

class Move(object):
    def __init__(self, src, dest, piece=None, captured_piece=None, promo=None, ep=None, castle=False):
        self.src = src # origin square (0-63)
        self.dest = dest # destination square (0-63)
        self.piece = piece # piece type (0-5)
        self.promo = promo # promotion piece type (0-5)
        self.ep = ep # en passant target on the next turn (0-63)
        self.castle = castle # handle castling rights (True or False)
        self.captured_piece = captured_piece
    
    def __repr__(self):
        return f'{Square(self.src).get_char()} {Square(self.dest).get_char()}'