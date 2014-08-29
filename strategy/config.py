import json

with open('strategy/preflop_move.json') as f:
    preflop_move_str_version = json.load(f)
    preflop_move = {}
    for k1 in preflop_move_str_version:
        preflop_move[int(k1)] = {}
        for k2 in preflop_move_str_version[k1]:
            preflop_move[int(k1)][int(k2)] = preflop_move_str_version[k1][k2]

with open('strategy/prob_factor.json') as f:
    prob_factor = json.load(f)
