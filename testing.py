from engine.movegen import generate_legal_moves, generate_moves
import engine.chessboard as cb
import engine.movegen as mg
import engine.helper as hp
import random as rn
import numpy as np

fen = ''
board = cb.Chessboard()
board.set_board(fen)
perft_driver(board, 2)
