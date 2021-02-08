import numpy as np
import helper as hp

class Square:
    def __init__(self, index):
        self.index = np.uint8(index)

    def __str__(index):
        rank = index // 8
        file = index % 8
        string = chr(ord('a') + file) + str(rank + 1)
        return string

    def to_bitboard(self):
        return hp.bit_on(np.uint64(0), self.index)

    @classmethod
    def get_index(self, string):
        rank = index // 8
        file = index % 8
        string = chr(ord('a') + file) + str(rank + 1)
        return string