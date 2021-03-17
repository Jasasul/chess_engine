from engine.square import Square
from engine.constants import File, Rank, Piece, Castle
import engine.helper as hp
import engine.lookup_tables as tb

class Move(object):
    def __init__(self, src=None, dest=None, piece=None,
                 captured=None, promo=None, is_ep=False,
                 castle=None, new_ep=None, is_check=False):
        self.src = src # source square bb
        self.dest = dest # destination square bb
        self.piece = piece # piece (0-5)
        # optional
        self.promo = promo # promotion piece (0-5)
        self.is_ep = is_ep # is ep capture
        self.castle = castle # if move is a castle queenside or kindside
        self.captured = captured # capture piece (0-5) 
        self.new_ep = new_ep # stores new ep target square for opposite side if the move is double-push
        self.is_check = is_check
    
    def is_valid(self):
        # a move has to have a source, a destination and a piece
        if self.src != None and self.dest != None and self.piece in [0, 1, 2, 3, 4, 5]:
            return True
        return False
    
    def get_piece(self):
        # gets a piece notation of a move - none for a  pawn
        piece = self.piece.to_char().upper()
        if piece == 'P':
            return ''
        return piece
    
    def get_destination(self):
        # destination square of a move
        dest = Square(hp.lsb(self.dest)).get_char()
        return dest
    
    def get_file(self):
        # from what file piece moves
        file_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for file in File:
            if tb.FILES[file] & self.src:
                return file_letters[file]
    
    def get_rank(self):
        # from waht rank piece moves
        rank_nums = ['1', '2', '3', '4' , '5', '6', '7', '8']
        for rank in Rank:
            if tb.RANKS[rank] & self.src:
                return rank_nums[rank]
    
    def get_capture(self):
        # gets a capture format of a move
        capture = ''
        if self.piece == Piece.PAWN and self.captured != None:
            capture += self.get_file()
        if self.captured != None:
            capture += 'x'
        return capture
    
    def get_check(self):
        # gets check format of a move
        check = ''
        if self.is_check:
            check += '+'
        return check

    def get_notation(self, move_list):
        # creates a move notation in standard format
        same_dest = []
        ag_notation = ''
        # N - knight B - bishop, R - rook, Q - queen, K - king, a pawn does not have any character
        ag_notation += self.get_piece()

        for move in move_list:
            # finding moves where 2 pieces of the same type move to the same square
            if move == self: continue
            if move.piece == Piece.PAWN: continue
            if move.dest == self.dest and move.piece == self.piece:
                same_dest.append(move)
        # resolving ambiguity
        file = self.get_file()
        rank = self.get_rank()
        src_sq = ''
        if len(same_dest) > 1:
            # if more than one move, file or rank is not enough
            src_sq = f'{file}{rank}'
        if len(same_dest) == 1:
            # file first, and if the pieces move from the same file, we add rank
            move = same_dest[0]
            move_file = move.get_file()
            move_rank = move.get_rank()
            if move_file != file: src_sq = file
            elif move_rank != rank: src_sq = rank
        # appending after piece notation
        ag_notation += src_sq
        # x is for capture if the move is one
        ag_notation += self.get_capture()
        # destination is last
        ag_notation += self.get_destination()
        # special cases - Castle king side - O-O, Castle queen side - O-O-O
        if self.piece == Piece.KING:
            if self.castle == Castle.OO:
                ag_notation = 'O-O'
            if self.castle == Castle.OOO:
                ag_notation = 'O-O-O'
        
        if self.promo != None:
            # format of promotion is destination + = + piece pawn is promoted to
            self.ag_notation += '=' + self.promo.get_char().upper()
        # + for check at the end
        ag_notation += self.get_check()

        return ag_notation
    
    def __repr__(self):
        # human readable format of a move
        source = Square(hp.lsb(self.src)).get_char()
        destination = Square(hp.lsb(self.dest)).get_char()
        return f'{source} {destination}'