import numpy as np
import engine.evaluate as ev
import engine.movegen as mg
import engine.helper as hp
from engine.constants import Color, Piece

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
    if insufficient_material(position):
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

def insufficient_material(position):
    # returns True if there is not enough material to deliver a checkmate
    no_heavy = False
    no_pawns = False
    # all 12 bitboards for combining them
    wp = position.pieces[Color.WHITE][Piece.PAWN]
    wn = position.pieces[Color.WHITE][Piece.KNIGHT]
    wb = position.pieces[Color.WHITE][Piece.BISHOP]
    wr = position.pieces[Color.WHITE][Piece.ROOK]
    wq = position.pieces[Color.WHITE][Piece.QUEEN]
    wk = position.pieces[Color.WHITE][Piece.KING]

    bp = position.pieces[Color.BLACK][Piece.PAWN]
    bn = position.pieces[Color.BLACK][Piece.KNIGHT]
    bb = position.pieces[Color.BLACK][Piece.BISHOP]
    br = position.pieces[Color.BLACK][Piece.ROOK]
    bq = position.pieces[Color.BLACK][Piece.QUEEN]
    bk = position.pieces[Color.BLACK][Piece.KING]
    # you can deliver a checkmate with a single rook or queen, there can't be any
    if wq == 0 and bq == 0 and wr == 0 and br == 0:
        no_heavy = True
    # pawns can promote into the heavy pieces (rook and queen)
    if wp == 0 and bp == 0:
        no_pawns = True
    # only light pieces (knight, bishop)   
    if no_heavy and no_pawns:
        # only kings
        if wn == 0 and bn == 0 and wb == 0 and bb == 0:
            return True
        # white king and white knight vs black king
        if hp.bit_count(wn) == 1 and wb == 0 and bn == 0 and bb == 0:
            return True
        # black king and black knight vs white king
        if hp.bit_count(bn) == 1 and bb == 0 and wn == 0 and wb == 0:
            return True
        # white king and white bishop vs black king
        if wn == 0 and hp.bit_count(wb) == 1 and bn == 0 and bb == 0:
            return True
        # black king and black bishop vs white king
        if bn == 0 and hp.bit_count(bb) == 1 and wn == 0 and wb == 0:
            return True
    return False


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