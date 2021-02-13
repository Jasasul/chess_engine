from engine.movegen import generate_moves
from engine.chessboard import Chessboard

board = Chessboard()
board.set_board(board.start_fen)
moves = generate_moves(board)
print(moves)