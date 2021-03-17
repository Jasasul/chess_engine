import numpy as np
import engine.evaluate as ev
import engine.movegen as mg
import copy
from engine.constants import Color

def maxi(position, depth, alpha, beta, is_start=False):
    # white - best move = move with the largest score
    if depth == 0: return ev.get_score(position)

    moves_scored = []
    scores = []

    max_score = -float('inf')
    # all moves
    moves = mg.generate_moves(position)
    for move in moves:
        # only if legal
        if move.is_legal(position):
            # make move
            new_position = position.copy_make(move)
            # evaluate for child position
            score = mini(new_position, depth - 1, alpha, beta)
            moves_scored.append(move)
            scores.append(score)
            # if current move is better
            max_score = max(max_score, score)
            del new_position
            alpha = max(alpha, score)
            if beta <= alpha:
                break
    # if no moves
    if len(moves_scored) == 0 and not is_start:
        return game_end_score(position)
    # if root node: return best move
    if is_start: return get_best(moves_scored, scores, True)
    # else return best move
    return max_score

def mini(position, depth, alpha, beta, is_start=False):
    # black - best move = move with the smallest score
    if depth == 0: return ev.get_score(position)
    
    moves_scored = []
    scores = []

    min_score = float('inf')
    moves = mg.generate_moves(position)
    for move in moves:
        # moves
        if move.is_legal(position):
            # only legal
            new_position = position.copy_make(move)
            score = maxi(new_position, depth - 1, alpha, beta)
            moves_scored.append(move)
            scores.append(score)
            # black is minimizing (best negative score)
            min_score = min(beta, score)
            del new_position
            beta = min(beta, score)
            if beta <= alpha:
                break
    # checkmate or check
    if len(moves_scored) == 0 and not is_start:
        return game_end_score(position)
    # if root node: return best move
    if is_start: return get_best(moves_scored, scores, False)
    # else: return lowest score (best for black)
    return min_score


def king_in_check(position):
    # return if king of the side to move is in check
    if len(position.move_list) == 0:
        return False
    return position.move_list[0].is_check

def game_end_score(position):
    # detects checkmates and draws
    if king_in_check(position):
        # current position is checkmate
        if position.turn == Color.WHITE:
            # checkmate score for each side
            return -49000
        return 49000
    # draw
    return 0

def get_best(moves, scores, is_maximizing):
    # finds best move from scores generated
    best_move = moves[0]
    best_score = scores[0]

    for i in range(len(moves)):
        if is_maximizing:
            # is white
            if scores[i] > best_score:
                best_move = moves[i]
                best_score = scores[i]
        else:
            # is black
            if scores[i] < best_score:
                best_move = moves[i]
                best_score = scores[i]

    move_notation = best_move.get_notation(moves)
    return move_notation