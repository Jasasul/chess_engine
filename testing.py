from engine.movegen import generate_moves, get_queen_attacks
from engine.chessboard import Chessboard
import engine.helper as hp
import random as rn

board = Chessboard()
board.set_board('8/8/8/8/8/3R4/8/8 w KQkq - 0 1')
moves = generate_moves(board)
board.make_move(rn.choice(moves))