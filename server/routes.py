from flask import render_template, url_for, redirect, Blueprint, jsonify, request
import random as rn
import engine.helper as hp
import engine.chessboard as cb
import engine.movegen as mg
import engine.search as search
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
        if board.turn == Color.WHITE:
            best = search.minimax(board, 3, True, True)
        else:
            best = search.minimax(board, 3, False, True)
        return jsonify(move=best)
    return jsonify(move='Invalid fen')