import json
from public import find_out
from random import randint
import sys
sys.path.insert(0, '/Library/Python/2.7/site-packages/')
from sklearn.cluster import KMeans
from numpy import std
from numpy import average


N = 10000

with open('learning/board_feature/standard_stats.json') as f:
    ss = json.load(f)
    standard_stats = {}
    for n1 in ss:
        if int(n1) not in standard_stats:
            standard_stats[int(n1)] = {}
        for c1 in ss[n1]:
            if int(c1) not in standard_stats[int(n1)]:
                standard_stats[int(n1)][int(c1)] = {}
            for n2 in ss[n1][c1]:
                if int(n2) not in standard_stats[int(n1)][int(c1)]:
                    standard_stats[int(n1)][int(c1)][int(n2)] = {}
                for c2 in ss[n1][c1][n2]:
                    if int(c2) not in standard_stats[int(n1)][int(c1)][int(n2)]:
                        standard_stats[int(n1)][int(c1)][int(n2)][int(c2)] = {}
                    standard_stats[int(n1)][int(c1)][int(n2)][int(c2)]\
                            = ss[n1][c1][n2][c2]

def rand_card(n):
    result = list()
    for i in xrange(n):
        n1 = randint(2, 14)
        c1 = randint(1, 4)
        while [n1, c1] in result:
            n1 = randint(2, 14)
            c1 = randint(1, 4)
        result.append([n1, c1])
    return result

def classify(fo, cards):
    if fo[0] >= 6:
        return 8
    if fo[0] == 5:
        return 7
    if fo[0] == 4:
        return 6
    if fo[0] == 3:
        return 5
    if fo[0] == 2:
        if find_out(cards[2:])[0] == 0:
            return 4
        elif find_out(cards[2:])[0] == 1:
            if fo[1] == cards[0][0] or fo[1] == cards[1][0]:
                if fo[1] > max(map(lambda x:x[0], cards[2:])):
                    return 3
                elif fo[1] == max(map(lambda x:x[0], cards[2:])):
                    return 2
                else:
                    return 1
            else:
                is_top_pair = 1
                for c in cards[2:]:
                    if c[0] != fo[1] and c[0] > fo[2]:
                        is_top_pair = 0
                        break
                if is_top_pair:
                    return 2
                else:
                    return 1
        else:
            return 0
    if fo[0] == 1 and cards[0][0] == cards[1][0] and cards[0][0] > max(map(lambda x:x[0], cards[2:])):
        return 3
    if fo[0] == 1 and fo[1] == max(map(lambda x:x[0], cards[2:])):
        return 2
    if fo[0] == 1:
        return 1
    return 0

def get_distribution(cards):
    result = [0] * 9
    prob_sum = 0
    for i in xrange(N):
        hc1 = rand_card(1)
        while hc1[0] in cards:
            hc1 = rand_card(1)
        hc2 = rand_card(1)
        while hc2[0] in cards+hc1:
            hc2 = rand_card(1)
        tc = rand_card(1)
        while tc[0] in cards+hc1+hc2:
            tc = rand_card(1)
        rc = rand_card(1)
        while rc[0] in cards+hc1+hc2+tc:
            rc = rand_card(1)
        fo = find_out(cards+hc1+hc2+tc+rc)
        hc1, hc2 = min([hc1, hc2]), max([hc1, hc2])
        print hc1+hc2+cards+tc+rc, '\t\t', fo, standard_stats[hc1[0][0]][hc1[0][1]][hc2[0][0]][hc2[0][1]]
        result[classify(fo, hc1+hc2+cards+tc+rc)]\
                += standard_stats[hc1[0][0]][hc1[0][1]][hc2[0][0]][hc2[0][1]]
        prob_sum += standard_stats[hc1[0][0]][hc1[0][1]][hc2[0][0]][hc2[0][1]]
    return map(lambda x:x*1.0/prob_sum, result)

def make_data():
    data = list()
    board = list()
    for i in xrange(100):
        print i
        c = rand_card(3)
        d = get_distribution(c)
        data.append(c)
        board.append(d)
    return data, board

def norm(data):
    avgs = [0] * 9
    stds = [0] * 9
    for i in xrange(9):
        d = map(lambda x:x[i], data)
        avgs[i] = average(d)
        stds[i] = std(d)
    for d in data:
        for i in xrange(9):
            d[i] = (d[i]-avgs[i]) / stds[i]
    return data

def add_weight(data):
    weights = [1, 1, 1, 1, 0.5, 1, 5, 5, 1]
    for d in data:
        for i in xrange(9):
            d[i] *= weights[i]
    return data

def test(board):
    k = KMeans()
    k.n_clusters = 8
    k.fit(norm(board))
    return k 

if __name__ == '__main__':
    d,b = make_data()
    for i in xrange(100):
        print d[i], '<<<>>>', map(lambda x:round(x,2), b[i])
    k = test(b)
    for label in xrange(10):
        for i in xrange(100):
            if k.labels_[i] == label:
                print d[i]
        print k.cluster_centers_[label]
        print '\n\n'+'='*40+'\n\n'
