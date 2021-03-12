import numpy as np
import engine.evaluate as ev
import engine.movegen as mg
import copy

def minimax(position, depth, is_maximizing, start=False):
    # finds best move
    if depth == 0: return ev.get_score(position)

    moves_scored = []
    scores = []

    if is_maximizing:
        max_score = -float('inf')
        moves = mg.generate_moves(position)
        for move in moves:
            if mg.is_legal(position, move):
                new_pos = copy.deepcopy(position)
                new_pos.make_move(move)
                score = minimax(new_pos, depth - 1, False)
                moves_scored.append(move)
                scores.append(score)
                if score > max_score:
                    max_score = score
                del new_pos
        if start: return get_best(moves, scores, True)
        return max_score

    else:
        min_score = float('inf')
        moves = mg.generate_moves(position)
        for move in moves:
            if mg.is_legal(position, move):
                new_pos = copy.deepcopy(position)
                new_pos.make_move(move)
                score = minimax(new_pos, depth - 1, True)
                moves_scored.append(move)
                scores.append(score)
                if score < min_score:
                    min_score = score
                del new_pos
        if start: return get_best(moves, scores, False)
        return min_score

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