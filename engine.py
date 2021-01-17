import textwrap
import math
import random as rn

class Engine():
    def __init__(self):
        # bitboard has 64 squares - 1 bit per square, no need to store more
        self.mask_64 = int('1'*64, 2)
        # square mapping - little endian a1, b1, ... g8, h8 = 0, 1, ... 63, 63
        self.square_names = ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1',
                             'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
                             'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
                             'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
                             'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
                             'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
                             'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
                             'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8']
        # creates a dictionary with those values
        self.squares = {self.square_names[i]: i for i in range(64)}

        # files that would cause piece moves overlaps from a file to h and vice versa
        # are ignored during move genration for certain pieces
        # binary form is shorter
        self.not_a_file = 0xfefefefefefefefe
        self.not_h_file = 0x7f7f7f7f7f7f7f7f
        self.not_gh_file = 0x3f3f3f3f3f3f3f3f
        self.not_ab_file = 0xfcfcfcfcfcfcfcfc
        self.first_rank = 0x0101010101010101
        self.eight_rank = 0x8080808080808080
        self.light_squares = 0x55AA55AA55AA55AA
        self.dark_squares = 0xAA55AA55AA55AA55
        
        self.bishop_relevant_occupancy = [
            6, 5, 5, 5, 5, 5, 5, 6, 
            5, 5, 5, 5, 5, 5, 5, 5,
            5, 5, 7, 7, 7, 7, 5, 5,
            5, 5, 7, 9, 9, 7, 5, 5,
            5, 5, 7, 9, 9, 7, 5, 5,
            5, 5, 7, 7, 7, 7, 5, 5,
            5, 5, 5, 5, 5, 5, 5, 5,
            6, 5, 5, 5, 5, 5, 5, 6,
        ]
        self.rook_relevant_occupancy = [
            12, 11, 11, 11, 11, 11, 11, 12,
            11, 10, 10, 10, 10, 10, 10, 11,
            11, 10, 10, 10, 10, 10, 10, 11,
            11, 10, 10, 10, 10, 10, 10, 11,
            11, 10, 10, 10, 10, 10, 10, 11,
            11, 10, 10, 10, 10, 10, 10, 11,
            11, 10, 10, 10, 10, 10, 10, 11,
            12, 11, 11, 11, 11, 11, 11, 12,
        ]
            

        self.white = 1
        self.black = 0
    
    def print_bitboard(self, bitboard):
        # prints a bitboard in human readable format
        binary = bin(bitboard)[2:]
        padded_binary = binary.zfill(64)
        splitted_binary = textwrap.wrap(padded_binary, 8)
        for i in range(8):
            print(' '.join(splitted_binary[i][::-1]))
    
    def lshift(self, bitboard, bits):
        # shifts bitboard to the left, discarding bits exceeding 64 bit format
        return (bitboard << bits) & self.mask_64
    
    def rshift(self, bitboard, bits):
        # shifts bitboard to the right, discarding bits exceeding 0
        return bitboard >> bits
    
    def turn_bit_on(self, bitboard, index):
        # sets a bit at a index to 1
        return bitboard | self.lshift(1, index)
    
    def turn_bit_off(self, bitboard, index):
        return bitboard ^ self.lshift(1, index)
    
    def bit_count(self, bitboard):
        # counts bits that are set to 1 in a number
        bits = 0
        for i in range(64):
            if self.rshift(bitboard, i) & 1:
                bits += 1
        
        return bits
    
    def get_lsb(self, bitboard):
        # finds the least significant bit (bit with the lowest index set to 1)
        for i in range(64):
            if self.rshift(bitboard, i) & 1:
                return i
    
    def get_msb(self, bitboard):
        # finds the most significaant bit (bit with the highest index set to 1)
        return len(bin(bitboard)[2:]) - 1
    
    def square_to_coordinates(self, square):
        return self.square_names[square]
    
    def mask_pawn_attacks(self, square, side):
        # generates both pawn attacks (diagonals) for a square
        # white is up (lshift), black is down(rshift)
        attacks = 0
        pawn = 0
        # base square
        pawn = self.turn_bit_on(pawn, self.squares[square])

        if side:
            # white pawns
            # NoEa
            attacks |= self.lshift(pawn & self.not_h_file, 9)
            # NoWe
            attacks |= self.lshift(pawn & self.not_a_file, 7)
        else:
            # black pawns
            # SoWe
            attacks |= self.rshift(pawn & self.not_a_file, 9)
            # SoEa
            attacks |= self.rshift(pawn & self.not_h_file, 7)
        
        return attacks
    
    def mask_knight_attacks(self, square):
        # generates all attacks for a knight on a square
        # like a pawn, but both sides move exactly the same
        attacks = 0
        knight = 0

        # base square
        knight = self.turn_bit_on(knight, self.squares[square])

        # NoNoEa
        attacks |= self.lshift(knight & self.not_h_file, 17) 
        # NoEaEa
        attacks |= self.lshift(knight & self.not_gh_file, 10) 
        # NoNoWe
        attacks |= self.lshift(knight & self.not_a_file, 6) 
        # NoWeWe
        attacks |= self.lshift(knight & self.not_ab_file, 15) 
        # SoEaEa
        attacks |= self.rshift(knight & self.not_h_file, 6) 
        # SoSoEa
        attacks |= self.rshift(knight & self.not_gh_file, 15) 
        # SoSoWe
        attacks |= self.rshift(knight & self.not_a_file, 17) 
        # SoWeWe
        attacks |= self.rshift(knight & self.not_ab_file, 10) 

        return attacks
    
    def mask_king_attacks(self, square):
        # generates all moves for a king
        # like a knight
        attacks = 0
        king = 0
        
        # base square
        king = self.turn_bit_on(king, self.squares[square])

        # vertical
        attacks |= self.lshift(king, 8) | self.rshift(king, 8)
        # horizontal
        attacks |= self.lshift(king & self.not_h_file, 1) | self.rshift(king & self.not_a_file, 1)
        # antidiagonal
        attacks |= self.lshift(king & self.not_a_file, 7) | self.rshift(king & self.not_h_file, 7)
        # diagonal
        attacks |= self.lshift(king & self.not_h_file, 9) | self.rshift(king & self.not_a_file, 9)
        

        return attacks
    
    def relative_bishop_attacks(self, square):
        # generates all possible bishop attacks for a square
        # without blocking (x-ray)
        attacks = 0 
        bishop = 0
        # square value necessary for calculations
        square_value = self.squares[square]
        #debugging
        bishop = self.turn_bit_on(bishop, square_value)
        # which direction are the rays gonna go
        positive_ray = 6
        negative_ray = 2

        rank = square_value // 8
        file = square_value % 8
        # NoEa
        while rank <= positive_ray - 1 and file <= positive_ray - 1:
            rank += 1
            file += 1
            attacks |= self.lshift(1, rank*8 + file)

        rank = square_value // 8
        file = square_value % 8
        # NoWe
        while rank <= positive_ray - 1  and file >= negative_ray:
            rank += 1
            file -= 1
            attacks |= self.lshift(1, rank*8 + file)
        

        rank = square_value // 8
        file = square_value % 8
        # SoEa
        while rank >= negative_ray and file <= positive_ray - 1:
            rank -= 1
            file += 1
            attacks |= self.lshift(1, rank*8 + file)

        rank = square_value // 8
        file = square_value % 8
        # SoWe
        while rank >= negative_ray and file >= negative_ray:
            rank -= 1
            file -= 1
            attacks |= self.lshift(1, rank*8 + file)
        
        return attacks

        

    def relative_rook_attacks(self, square):
        # generates all possible rook attacks
        # without piece blocking (x-ray)
        attacks = 0
        rook = 0
        square_value = self.squares[square]

        rook = self.turn_bit_on(rook, square_value)

        rook_rank = square_value // 8
        rook_file = square_value % 8

        positive_ray = 7
        negative_ray = 0
        # North
        for rank in range(rook_rank+1, positive_ray):
            attacks |= self.lshift(1, rank*8 + rook_file) 
        # East
        for file in range(rook_file+1, positive_ray):
            attacks |= self.lshift(1, rook_rank*8 + file)
        # South
        for rank in range(rook_rank-1, negative_ray, -1):
            attacks |= self.lshift(1, rank*8 + rook_file)
        # West
        for file in range(rook_file-1, negative_ray, -1):
            attacks |= self.lshift(1, rook_rank*8 + file)

        return attacks
    
    def absolute_bishop_attacks(self, square, blocker):
        # generates all possible bishop attacks for a square
        # but pieces block
        attacks = 0 
        
        # separate piece attacks
        first = 0
        second = 0
        third = 0
        fourth = 0

        # square value necessary for calculations
        square_value = self.squares[square]

        # which direction are the rays gonna go
        positive_ray = 7
        negative_ray = 1

        rank = square_value // 8
        file = square_value % 8
        # NoEa
        while rank <= positive_ray - 1 and file <= positive_ray - 1:
            rank += 1
            file += 1
            first |= self.lshift(1, rank*8 + file)
            if first & blocker:
                break

        rank = square_value // 8
        file = square_value % 8
        # NoWe
        while rank <= positive_ray and file >= negative_ray:
            rank += 1
            file -= 1
            second |= self.lshift(1, rank*8 + file)
            if second & blocker:
                break
        

        rank = square_value // 8
        file = square_value % 8
        # SoEa
        while rank >= negative_ray and file <= positive_ray - 1:
            rank -= 1
            file += 1
            third |= self.lshift(1, rank*8 + file)
            if third & blocker:
                break

        rank = square_value // 8
        file = square_value % 8
        # SoWe
        while rank >= negative_ray and file >= negative_ray:
            rank -= 1
            file -= 1
            fourth |= self.lshift(1, rank*8 + file)
            if fourth & blocker:
                break

        attacks |= first | second | third | fourth
        
        return attacks
    
    def absolute_rook_attacks(self, square, blocker):
        # generates all possible bishop attacks for a square
        # but pieces block
        attacks = 0
        # separate piece attacks
        first = 0
        second = 0
        third = 0
        fourth = 0
        # square
        square_value = self.squares[square]


        rook_rank = square_value // 8
        rook_file = square_value % 8

        positive_ray = 8
        negative_ray = -1
        # North
        for rank in range(rook_rank+1, positive_ray):
            first |= self.lshift(1, rank*8 + rook_file)
            # breaks if a piece blocks the ray
            if first & blocker:
                break
        # East
        for file in range(rook_file+1, positive_ray):
            second |= self.lshift(1, rook_rank*8 + file)
            if second & blocker:
                break
        # South
        for rank in range(rook_rank-1, negative_ray, -1):
            third |= self.lshift(1, rank*8 + rook_file)
            if third & blocker:
                break
        # West
        for file in range(rook_file-1, negative_ray, -1):
            fourth |= self.lshift(1, rook_rank*8 + file)
            if fourth & blocker:
                break
        
        attacks |= first | second | third | fourth

        return attacks
    
    def set_occupancy(self, index, bits_in_mask, attack_mask):
        occupancy = 0
        for i in range(bits_in_mask):
            square = self.get_lsb(attack_mask)
            attack_mask = engine.turn_bit_off(attack_mask, square)
            if index & self.lshift(1, i):
                occupancy |= self.lshift(1, square)
        
        return occupancy

engine = Engine()