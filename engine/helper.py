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

def bit_count(bb):
    # returns a number of bits set to 1
    total = 0
    for i in range(64):
        if (bb >> np.uint8(i)) & np.uint8(1):
            total += 1
    return total

def validate_fen(fen):
    # validates a fen string received from the client
    valid = True
    kings = 0
    pieces = 0
    squares = 0

    parts = fen.split()
    # format
    if len(parts) != 6:
       valid = False
    else:
        # first part format
        if len(parts[0].split('/')) != 8:
            valid = False
        else:
            for char in parts[0]:
                # counting squares
                if char >= '1' and char <= '8':
                    squares += int(char)
                # piece handling
                if char.lower() in ['p', 'n', 'b', 'r', 'q' , 'k']:
                    pieces += 1
                    squares += 1
                    if char in ['k', 'K']:
                        kings += 1
            # 64 squares, not empty and max 1 king per side
            if squares != 64: valid = False
            if pieces == 0: valid = False
            if kings > 2 or kings == 0: valid = False
            # valid side to move
            if parts[1] not in ['w', 'b']: valid = False
            # valid castling
            for char in parts[2]:
                if char not in ['K', 'k', 'Q', 'q', '-']: valid = False
            # valid en passant square - no en passant square is notated as '-'
            if len(parts[3]) == 1 and parts[3] != '-': valid = False
            if len(parts[3]) > 2 and len(parts[3]) < 1:
                valid = False
            if len(parts[3]) == 2:
                if parts[3][0] not in ['a' 'b', 'c' , 'd', 'e', 'f' ,'g', 'h']:
                    valid = False
                else:
                    if parts[3][1] not in ['1', '2', '3', '4', '5', '6', '7', '8']:
                        valid = False

            # move counters are non-negative integers and fullmove clock must be lower than halfmove
            if int(parts[4]) < 0: valid = False
            if int(parts[4]) > int(parts[5]): valid = False
            if int(parts[5]) < 0: valid = False

    
    return valid