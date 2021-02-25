from flask import render_template, url_for, redirect, Blueprint, jsonify, request
import random as rn
import engine.helper as hp
from engine.chessboard import Chessboard
from engine.movegen import generate_moves

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
    if hp.validate_fen(fen):
        board.set_board(fen)
        # move generation
        moves = generate_moves(board)
        for move in moves:
            if move.promo != None: break
        board.make_move(move)
        board.unmake_move(move)
        move_string = str(move)
        # sending move generated back to the GUI
        return jsonify(move=move_string)
    else:
        return jsonify(move='Invalid fen')