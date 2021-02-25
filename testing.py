from engine.movegen import generate_moves, get_queen_attacks
from engine.chessboard import Chessboard
import engine.helper as hp
import random as rn

x = 16
print(bin(x & ~(1 << 2)))