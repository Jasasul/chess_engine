class Move(object):
    def __init__(self, src, dest, promo=None):
        self.scr = src
        self.dest = dest
        self.promo = promo