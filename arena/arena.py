#coding:utf-8

import json
import pickle
import neurolab
import random


class Arena():
    def __init__(self, fighter1, fighter2):
        self.f1 = fighter1
        self.f2 = fighter2

    @staticmethod
    def draw_cards():
        c1 = int(random.random()*5)#{{{
        c2 = c1
        while c2 == c1:
            c2 = int(random.random()*5)
        if random.random() > 0.5:
            p1 = 0
            p2 = 1
        else:
            p1 = 1
            p2 = 0
        return [c1, c2, p1, p2]#}}}
    
    def battle(self, times=10000):
        X1 = list()#{{{
        Y1 = list()
        X2 = list()
        Y2 = list()
        chip1 = 0
        chip2 = 0
        for game in xrange(times):
            cards = self.draw_cards()
            result = self.play_game(cards, self.f1, self.f2)
            X1 += result[0][0]
            Y1 += result[1][0]
            X2 += result[0][1]
            Y2 += result[1][1]
            chip1 += result[2][0]
            chip2 += result[2][1]
        print chip1, chip2
        self.learn(self.f1, self.f2, [X1, Y1], [X2, Y2])#}}}

    def learn(self, f1, f2, data1, data2):
        print 'Training'
        f1.net.train(data1[0], data1[1])
        f2.net.train(data2[0], data2[1])
        print 'Done: Training'

    def play_game(self, cards, f1, f2):
        para1 = list()
        para2 = list()
        Y1 = list()
        Y2 = list()
        adjustedY1 = list()
        adjustedY2 = list()
        adjustedX1 = list()
        adjustedX2 = list()
        d1 = list()
        d2 = list()
        pot1 = list()#在每个阶段的时候已经投入了多少
        pot2 = list()
        bet_round = 1
        result1 = 0
        result2 = 0
        if cards[2] == 0:
            betting = [1, 2]
            to_act = 1
        else:
            betting = [2, 1]
            to_act = 2
        while True:
            if to_act == 1:#{{{
                p1 = [0]*12
                p1[cards[0]] = 1
                p1[5+cards[2]] = 1
                p1[6+bet_round] = 1
                pot1.append(betting[0])
                para1.append(p1)
                decision = f1.net.step(p1)
                if bet_round == 5:
                    decision[2] = -9999
                if decision[0] == max(decision):#FOLD
                    d1.append('f')
                    result1 = -betting[0]
                    result2 = betting[0]
                    chip_change1, chip_change2 = finish(pot1, pot2, betting, 0, sum(betting))
                    break
                elif decision[1] == max(decision):#CALL
                    d1.append('c')
                    betting[0] = betting[1]
                    if cards[0] < cards[1]:
                        result1 = -betting[0]
                        result2 = betting[0]
                        chip_change1, chip_change2 = finish(pot1, pot2, betting, 0, sum(betting))
                    else:
                        result1 = betting[0]
                        result2 = -betting[0]
                        chip_change1, chip_change2 = finish(pot1, pot2, betting, sum(betting), 0)
                    break
                else:#RAISE
                    d1.append('r')
                    bet_round += 1
                    betting[0] = 2*betting[1]
                    to_act = 2
            else:
                p2 = [0]*12
                p2[cards[1]] = 1
                p2[5+cards[3]] = 1
                p2[6+bet_round] = 1
                pot2.append(betting[1])
                para2.append(p2)
                decision = f2.net.step(p2)
                if bet_round == 5:
                    decision[2] = -9999
                if decision[0] == max(decision):#FOLD
                    d2.append('f')
                    result1 = betting[1]
                    result2 = -betting[1]
                    chip_change1, chip_change2 = finish(pot1, pot2, betting, sum(betting), 0)
                    break
                elif decision[1] == max(decision):#CALL
                    d2.append('c')
                    betting[1] = betting[0]
                    if cards[0] < cards[1]:
                        result1 = -betting[0]
                        result2 = betting[0]
                        chip_change1, chip_change2 = finish(pot1, pot2, betting, 0, sum(betting))
                    else:
                        result1 = betting[0]
                        result2 = -betting[0]
                        chip_change1, chip_change2 = finish(pot1, pot2, betting, sum(betting), 0)
                    break
                else:#RAISE
                    d2.append('r')
                    bet_round += 1
                    betting[1] = 2*betting[0]
                    to_act = 1#}}}
        for (d, cc) in zip(d1, chip_change1):
            if cc > 0:#{{{
                if d == 'c':
                    y = [0, 1, 1]
                    Y1.append(y)
                if d == 'r':
                    y = [0, 0, 1]
                    Y1.append(y)
                if d == 'f':
                    y = [0, 1, 1]
                    Y1.append(y)
            else:
                if d == 'c':
                    y = [1, 0, 0]
                    Y1.append(y)
                if d == 'r':
                    y = [1, 0, 0]
                    Y1.append(y)
                if d == 'f':
                    y = [0, 0, 0]
                    Y1.append(y)
        for (d, cc) in zip(d2, chip_change2):
            if cc > 0:
                if d == 'c':
                    y = [0, 1, 1]
                    Y2.append(y)
                if d == 'r':
                    y = [0, 0, 1]
                    Y2.append(y)
                if d == 'f':
                    y = [0, 1, 1]
                    Y2.append(y)
            else:
                if d == 'c':
                    y = [1, 0, 0]
                    Y2.append(y)
                if d == 'r':
                    y = [1, 0, 0]
                    Y2.append(y)
                if d == 'f':
                    y = [0, 0, 0]
                    Y2.append(y)#}}}
        for (p, y, c) in zip(para1, Y1, chip_change1):
            adjustedX1 += [p]*abs(c)
            adjustedY1 += [y]*abs(c)
        for (p, y, c) in zip(para2, Y2, chip_change2):
            adjustedX2 += [p]*abs(c)
            adjustedY2 += [y]*abs(c)
        return [[adjustedX1, adjustedX2], [adjustedY1, adjustedY2], [result1, result2]] 


class Fighter():
    def __init__(self):
        self.net = neurolab.net.newff([[0, 1]]*12, [20, 3])
        self.net.init()


def finish(pot1, pot2, betting, result1, result2):
    chip_change1 = list()
    chip_change2 = list()
    if result1:
        for k in pot1:
            chip_change1.append(k+betting[1])
        for k in pot2:
            chip_change2.append(-betting[1]+k)
    if result2:
        for k in pot1:
            chip_change1.append(-betting[0]+k)
        for k in pot2:
            chip_change2.append(k+betting[0])
    return chip_change1, chip_change2

