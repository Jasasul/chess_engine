# most valuable attacker - least valuable victim
# when a move is a capture, score is acquired for which piece type captures which enemy piece type
# i.e. it is better for a pawn to capture a queen, rather than for a queen to capture a pawn
def score_move(move):
    # assings score to a move, so it gets searched sooner than others
    values = [100, 200, 300, 400, 500, 600]
    score = 0
    if move.captured != None:
        # if a move is capture, we apply mvv lva
        score = values[move.captured] - values[move.piece]
    move.score = score