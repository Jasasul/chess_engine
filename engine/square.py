import numpy as np
import engine.helper as hp

class Square:
    def __init__(self, index):
        self.index = np.uint8(index)
    
    def __repr__(self):
        rank = self.index // 8
        file = self.index % 8
        string = chr(ord('a') + file) + str(rank + 1)
        return string

    def get_char(self):
        rank = self.index // 8
        file = self.index % 8
        string = chr(ord('a') + file) + str(rank + 1)
        return string

    def to_bitboard(self):
        return hp.set_bit(np.uint64(0), self.index)

    @classmethod
    def get_index(self, string):
        file = ord(string[0]) - ord('a')
        rank = int(string[1]) - 1
        index = 8*rank + file
        return index