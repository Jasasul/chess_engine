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

def perft(position, test_board, depth):
    if depth == 0: return 1

    count = 0
    moves = mg.generate_moves(position)
    string_moves = [str(move) + str(move.piece) for move in moves]
    for move in moves:
        if is_legal(position, move):
            new_pos = copy.deepcopy(position)
            new_pos.make_move(move)
            test_string = str(move)
            test_string = ''.join(test_string.split())
            test_move = chess.Move.from_uci(test_string)
            new_pos = copy.deepcopy(position)
            new_pos.make_move(move)
            test_board.push(test_move)
            count += perft(new_pos, test_board, depth-1)
            test_board.pop()
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
test_board = chess.Board(tricky)
x = perft(board, test_board, 2)
print(x)