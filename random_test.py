import numpy as np
from numpy.core.numeric import binary_repr
import engine.chessboard as cb
import engine.square as sq
import engine.helper as hp
import engine.evaluate as ev
import engine.movegen as mg
from engine.constants import Piece, Castle, Color

board = cb.Chessboard()
starting = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
tricky = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'
random = '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1'
board.set_board(tricky)
x = ev.get_score(board)
print(x)
legal = mg.legal_moves(board)
notation = [move.get_notation(legal) for move in legal]
print(notation)