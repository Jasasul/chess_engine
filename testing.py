from engine.movegen import generate_moves, get_queen_attacks
from engine.chessboard import Chessboard
import engine.helper as hp

board = Chessboard()
board.set_board(board.start_fen)
moves = generate_moves(board)
print(moves)