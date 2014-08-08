import json

with open('stats/prob_factor_close.json') as f:
    prob_factor_close = json.load(f)

with open('stats/prob_factor_open.json') as f:
    prob_factor_open = json.load(f)

def get_preflop_prob(top_n):
    cut_points = [0.5, 1, 2, 3, 5, 10, 15, 20, 25, 100]#{{{
    coef = [0] * len(cut_points)
    for point_index in xrange(len(cut_points)):
        coef[point_index] = 1 / (1+pow(abs(cut_points[point_index]-top_n), 0.5))
    coef_sum = sum(coef)
    prob = {}
    for c1 in prob_factor[u'1']:
        prob[int(c1)] = {}
        for c2 in prob_factor[u'1'][c1]:
            s = 0
            for (c, p) in zip(coef, cut_points):
                s += c * prob_factor[unicode(p)][c1][c2]
            prob[int(c1)][int(c2)] = s / coef_sum 
    return prob#}}}

def trans_prob(small_table):
    big_table = {}#{{{
    for num1 in xrange(2, 15):
        big_table[num1] = {}
        for col1 in xrange(1, 5):
            big_table[num1][col1] = {}
            for num2 in xrange(2, 15):
                big_table[num1][col1][num2] = {}
                for col2 in xrange(1, 5):
                    if col1 == col2:
                        big_table[num1][col1][num2][col2] = small_table[min(num1, num2)][max(num1, num2)]
                    else:
                        big_table[num1][col1][num2][col2] = small_table[max(num1, num2)][min(num1, num2)]
    return big_table#}}}

def pick_top(top_n):
    big_table = test(top_n)
    all_combo = list()#{{{
    for num1 in big_table:
        for col1 in big_table[num1]:
            for num2 in big_table[num1][col1]:
                for col2 in big_table[num1][col1][num2]:
                    all_combo.append([big_table[num1][col1][num2][col2], \
                            [num1, col1], [num2, col2]])
    sorted_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
    result = list()
    for combo in sorted_combo:
        if not [combo[0], combo[1][0], combo[2][0]] in result:
            result.append([combo[0], combo[1][0], combo[2][0]])
    return result

def test(top_n):
    tmp = get_preflop_prob(top_n)
    return trans_prob(tmp)

class StatsHandler():
    def __init__(self, game_driver):
        pass        
    def preflop_update(self, p1, p2, p3, p4, p5):
        pass
    def postflop_update(self, p1, p2, p3, p4, p5):
        pass
