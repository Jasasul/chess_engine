from flask import render_template, url_for, redirect, Blueprint, jsonify, request
import random as rn
from engine.chessboard import Chessboard
from engine.movegen import generate_moves
import time

routes = Blueprint('routes', __name__)

@routes.route('/')
@routes.route('/home')
def home():
    return render_template('home.html')

@routes.route('/handle_request', methods=['POST'])
def handle_request():
    # initial position
    board = Chessboard()
    fen = request.get_data().decode()
    board.set_board(fen)
    # move generation
    moves = generate_moves(board)
    move = rn.choice(moves)
    board.make_move(move)
    move_string = str(move)
    # sending move generated back to the GUI
    return jsonify(move=move_string)