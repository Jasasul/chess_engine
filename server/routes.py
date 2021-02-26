from flask import render_template, url_for, redirect, Blueprint, jsonify, request
import random as rn
import engine.helper as hp
import engine.chessboard as cb
import engine.movegen as mg
from engine.constants import Piece

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
        board.set_board(fen)
        # move generation
        moves = mg.generate_moves(board)
        if moves == []:
            return jsonify(move=in_check(board))
        move = rn.choice(moves)
        move_string = str(move)
        board.make_move(move)
        board.unmake_move(move)
        # sending move generated back to the GUI
        return jsonify(move=move_string)
    return jsonify(move='Invalid fen')

def in_check(position):
    king = position.pieces[position.turn][Piece.KING]
    if mg.is_attacked(position, hp.lsb(king), position.turn ^ 1):
        return 'Checkmate'
    return 'Draw'