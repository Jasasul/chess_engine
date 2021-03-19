import numpy as np

#    (Victims) Pawn Knight Bishop   Rook  Queen   King
#    (Attackers)
#        Pawn   105    205    305    405    505    605
#      Knight   104    204    304    404    504    604
#      Bishop   103    203    303    403    503    603
#        Rook   102    202    302    402    502    602
#       Queen   101    201    301    401    501    601
#        King   100    200    300    400    500    600

# most valuable attacker - least valuable victim
# when a move is a capture, score is acquired for which piece type captures which enemy piece type
# i.e. it is better for a pawn to capture a queen, rather than for a queen to capture a pawn
mvv_lva = np.array([
    105, 205, 305, 405, 505, 605,
    104, 204, 304, 404, 504, 604,
    103, 203, 303, 403, 503, 603,
    102, 202, 302, 402, 502, 602,
    101, 201, 301, 401, 501, 601,
    100, 200, 300, 400, 500, 600
]).reshape((6, 6))

def score_move(move):
    # assings score to a move, so it gets searched sooner than others
    values = [100, 200, 300, 400, 500, 600]
    score = 0
    if move.captured != None:
        # if a move is capture, we apply mvv lva
        score = values[move.captured] - values[move.piece]
    move.score = score