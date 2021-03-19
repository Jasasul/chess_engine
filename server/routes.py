from flask import render_template, url_for, redirect, Blueprint, jsonify, request
import random as rn
import engine.helper as hp
import engine.chessboard as cb
import engine.movegen as mg
import engine.search as search
from engine.constants import Piece, Color

routes = Blueprint('routes', __name__)

@routes.route('/')
@routes.route('/editor')
def editor():
    return render_template('home.html')

@routes.route('/menu')
def menu():
    return render_template('menu.html')

@routes.route('/handle_request', methods=['POST'])
def handle_request():
    # initial position
    fen = request.get_data().decode()
    if hp.validate_fen(fen):
        # setting up board
        board = cb.Chessboard()
        board.set_board(fen)
        # we can still play
        board_status = board.get_game_status()
        # detecting game end
        if board_status != 'Valid':
            return jsonify(move=board_status)
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