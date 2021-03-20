from numpy import clongdouble
from engine.square_tables import QUEEN
import engine.evaluate as ev
import engine.movegen as mg
from engine.constants import Color

def maxi(position, depth, alpha, beta, is_start=False):
    # white - best move = move with the largest score
    if depth == 0: return ev.get_score(position)

    if is_start:
        moves_scored = []
        scores = []

    max_score = -float('inf')
    # all moves
    moves = mg.generate_moves(position)
    legal = 0
    for move in moves:
        # only if legal
        new_position = position.copy_make(move)
        if new_position.is_legal():
            legal += 1
            # make move
            # evaluate for child position
            score = mini(new_position, depth - 1, alpha, beta)
            # we are returning moves
            if is_start:
                moves_scored.append(move)
                scores.append(score)
            # if current move is better
            max_score = max(max_score, score)
            del new_position
            alpha = max(alpha, score)
            if beta <= alpha:
                break
    # game end - checkmate or draw
    if position.halfmove >= 50:
        return 0
    if legal == 0 and not is_start:
        return game_end_score(position)
    # if root node: return best move
    if is_start: return get_best(moves_scored, scores, True)
    # else return best move
    return max_score

def mini(position, depth, alpha, beta, is_start=False):
    # black - best move = move with the smallest score
    if depth == 0: return ev.get_score(position)

    if is_start:
        moves_scored = []
        scores = []

    min_score = float('inf')
    moves = mg.generate_moves(position)
    legal = 0
    for move in moves:
        new_position = position.copy_make(move)
        if new_position.is_legal():
            legal += 1
            # only legal
            score = maxi(new_position, depth - 1, alpha, beta)
            # we are returning best move
            if is_start:
                moves_scored.append(move)
                scores.append(score)
            # black is minimizing (best negative score)
            min_score = min(min_score, score)
            del new_position
            beta = min(beta, score)
            if beta <= alpha:
                break
    # game end - checkmate or draw
    if position.halfmove >= 50:
        return 0
    if legal == 0 and not is_start:
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
    if position.king_in_check(position.turn):
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
    print(move_notation)
    return move_notation