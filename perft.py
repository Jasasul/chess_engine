from engine.lookup_tables import KING_ATTACKS
from engine.movegen import generate_moves, is_attacked, in_check, is_legal
from engine.constants import Piece, Color, Castle
import copy
import engine.chessboard as cb
import engine.movegen as mg
import engine.helper as hp
import random as rn
import numpy as np
import chess

def perft(position, depth):
    if depth == 0: return 1

    count = 0
    moves = mg.generate_moves(position)
    for move in moves:
        if is_legal(position, move):
            new_pos = copy.deepcopy(position)
            new_pos.make_move(move)
            count += perft(new_pos, depth-1)
            del new_pos

    return count

def test_perft(position, depth):
    if depth == 0: return 1

    count = 0
    for move in position.legal_moves:
        position.push(move)
        count += test_perft(position, depth-1)
        position.pop()
    return count

starting = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
tricky = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
more = 'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8'
board = cb.Chessboard()
board.set_board(tricky)
x = perft(board, 3)
print(x)