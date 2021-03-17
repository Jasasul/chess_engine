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
        # minimax search
        alpha = -float('inf')
        beta = float('inf')
        if board.turn == Color.WHITE:
            best = search.maxi(board, 3, alpha, beta, True)
        else:
            best = search.mini(board, 3, alpha, beta, True)
        # returns best move in json format
        return jsonify(move=best)
    # invalid position
    return jsonify(move='Invalid fen')