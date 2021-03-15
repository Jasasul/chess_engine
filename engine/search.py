import numpy as np
import engine.evaluate as ev
import engine.movegen as mg
import copy
from engine.constants import Color

def minimax(position, depth, is_maximizing, start=False):
    # finds best move
    if depth == 0: return ev.get_score(position)

    # king is in check if last move was in check
    if len(position.move_list) > 0:
        king_in_check = position.move_list[-1].is_check
    else:
        king_in_check = False

    # where are moves for the first positin stored and their scores
    moves_scored = []
    scores = []

    # for white
    if is_maximizing:
        max_score = -float('inf')
        # all moves
        moves = mg.generate_moves(position)
        for move in moves:
            # only if legal
            if mg.is_legal(position, move):
                # make move
                new_pos = copy.deepcopy(position)
                new_pos.make_move(move)
                # evaluate for child position
                score = minimax(new_pos, depth - 1, False)
                moves_scored.append(move)
                scores.append(score)
                # if current move is better
                max_score = max(max_score, score)
                del new_pos
        # if no moves
        if len(moves_scored) == 0 and not start:
            if king_in_check:
                # checkmate
                return -49000
            # draw
            return 0
        for i in range(len(moves_scored)):
            if move.captured != None:
                print(scores[i])
        # if root node: return best move
        if start: return get_best(moves_scored, scores, True)
        # else return best move
        return max_score

    # for black
    else:
        min_score = float('inf')
        moves = mg.generate_moves(position)
        for move in moves:
            # moves
            if mg.is_legal(position, move):
                # only legal
                new_pos = copy.deepcopy(position)
                new_pos.make_move(move)
                score = minimax(new_pos, depth - 1, True)
                moves_scored.append(move)
                scores.append(score)
                # black is minimizing (best negative score)
                max_score = min(min_score, score)
                del new_pos
        # checkmate or check
        if len(moves_scored) == 0 and not start:
            if king_in_check:
                return 49000
            return 0
        # if root node: return best move
        if start: return get_best(moves_scored, scores, False)
        # else: return lowest score (best for black)
        return min_score

def maxi(position, depth, is_start=False):
    # white - best move = move with the largest score
    if depth == 0: return ev.get_score(position)

    moves_scored = []
    scores = []

    max_score = -float('inf')
    # all moves
    moves = mg.generate_moves(position)
    for move in moves:
        # only if legal
        if mg.is_legal(position, move):
            # make move
            new_pos = copy.deepcopy(position)
            new_pos.make_move(move)
            # evaluate for child position
            score = mini(new_pos, depth - 1)
            moves_scored.append(move)
            scores.append(score)
            # if current move is better
            max_score = max(max_score, score)
            del new_pos
    # if no moves
    if len(moves_scored) == 0 and not is_start:
        return game_end_score(position)
    # if root node: return best move
    if is_start: return get_best(moves_scored, scores, True)
    # else return best move
    return max_score

def mini(position, depth, is_start=False):
    # black - best move = move with the smallest score
    if depth == 0: return ev.get_score(position)
    
    moves_scored = []
    scores = []

    min_score = float('inf')
    moves = mg.generate_moves(position)
    for move in moves:
        # moves
        if mg.is_legal(position, move):
            # only legal
            new_pos = copy.deepcopy(position)
            new_pos.make_move(move)
            score = maxi(new_pos, depth - 1)
            moves_scored.append(move)
            scores.append(score)
            # black is minimizing (best negative score)
            max_score = min(max_score, score)
            del new_pos
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
    return position.move_list.is_check

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