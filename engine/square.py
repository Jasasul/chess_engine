import numpy as np
import engine.helper as hp

class Square:
    def __init__(self, index):
        self.index = np.uint8(index) # 0 - 63 (64 squares on chessboard)
    
    def get_char(self):
        # returns standard notation of a square
        rank = self.index // 8
        file = self.index % 8
        string = chr(ord('a') + file) + str(rank + 1)
        return string

    def to_bitboard(self):
        # convert the index to 64 bit unsigned integer - the bitboard
        return hp.set_bit(np.uint64(0), self.index)

    @classmethod
    def from_str(self, string):
        file = np.uint8(ord(string[0]) - ord('A'))
        rank = np.uint8(int(string[1]) - 1)
        return (rank << np.uint(3)) | file