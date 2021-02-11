from flask import render_template, url_for, redirect, Blueprint, jsonify
import random as rn
from engine.chessboard import Chessboard
from engine.movegen import generate_moves

routes = Blueprint('routes', __name__)

@routes.route('/')
@routes.route('/home')
def home():
    return render_template('home.html')

@routes.route('/handle_request', methods=['POST'])
def handle_request():
    fen = 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2'
    return jsonify(fen=fen)