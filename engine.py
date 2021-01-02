import textwrap
import math

class Engine():
    def __init__(self):
        # bitboard has 64 squares - 1 bit per square, no need to store more
        self.bitboard_length_mask = int('1'*64, 2)
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
    
    def print_bitboard(self, bitboard):
        # prints a bitboard in human readable format
        binary = bin(bitboard)[2:]
        padded_binary = binary.zfill(64)
        splitted_binary = textwrap.wrap(padded_binary, 8)
        for i in range(8):
            print(' '.join(splitted_binary[i][::-1]))
    
    def lshift(self, bitboard, bits):
        # shifts bitboard to the left, discarding bits exceeding 64 bit format
        return (bitboard << bits) & self.bitboard_length_mask
    
    def rshift(self, bitboard, bits):
        # shifts bitboard to the right, discarding bits exceeding 0
        return bitboard >> bits
    
    def turn_bit_on(self, bitboard, index):
        # sets a bit at a index to 1
        return bitboard | self.lshift(1, index)
    
    

engine = Engine()
engine.print_bitboard(engine.turn_bit_on(0, engine.squares['e4']))
