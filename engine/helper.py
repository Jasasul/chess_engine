import numpy as np
import textwrap as tw

def print_bitboard(board):
    # prints bitboard in human readable format
    binary = np.binary_repr(board)
    chessboard = list(binary.zfill(64))
    for i in range(64):
        if chessboard[i] == '0':
            chessboard[i] = '.'
    chessboard = tw.wrap(''.join(chessboard), 8)
    for i in range(8):
            print(' '.join(chessboard[i][::-1]))
    print()

def set_bit(bb, sq):
    # sets bit on bb to 1
    return bb | np.uint64(1) << np.uint64(sq)

def clear_bit(bb, sq):
    # sets bit on bb to 0
    return bb ^ np.uint64(1) << np.uint64(sq)

def lsb(bb):
    # gets an index of the leeast significant bit (Little endian square mapping)
    for i in range(64):
        if (bb >> np.uint8(i)) & np.uint8(1):
            return i
