import numpy as np
import textwrap as tw

def print_bitboard(board):
    binary = np.binary_repr(board)
    chessboard = list(binary.zfill(64))
    for i in range(64):
        if chessboard[i] == '0':
            chessboard[i] = '.'
    chessboard = tw.wrap(''.join(chessboard), 8)
    for i in range(8):
            print(' '.join(chessboard[i][::-1]))

def bit_on(bb, sq):
    return bb | np.uint64(1) << np.uint64(sq)

def bit_off(bb, sq):
    return bb ^ np.uint64(1) << np.uint64(sq)