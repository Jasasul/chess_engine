from flask import render_template, url_for, redirect, Blueprint, jsonify, request
import random as rn
import engine.helper as hp
import engine.chessboard as cb
import engine.movegen as mg
from engine.constants import Piece, Color

routes = Blueprint('routes', __name__)

@routes.route('/')
@routes.route('/home')
def home():
    return render_template('home.html')

@routes.route('/handle_request', methods=['POST'])
def handle_request():
    # initial position
    board = cb.Chessboard()
    fen = request.get_data().decode()
    if hp.validate_fen(fen):
        # if position is valid
        board.set_board(fen)
        legal = mg.legal_moves(board)
        # move generation
        moves = [move.get_notation(legal) for move in legal]
        if len(moves) > 0:
            move = rn.choice(moves)
            # sending move generated back to the GUI
            return jsonify(move=move)
    return jsonify(move='Invalid fen')