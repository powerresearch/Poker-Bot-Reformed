#coding:utf-8

import json
import pickle
import neurolab
import random
from public import find_out


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
        self.learn(fighters, data)#}}}

    def learn(self, fighter, data):
        UPDATE PARAMETERS

    def play_game(cards, f1, f2):
        para1 = list()
        para2 = list()
        Y1 = list()
        Y2 = list()
        d1 = list()
        d2 = list()
        pot1 = list()#在每个阶段的时候已经投入了多少
        pot2 = list()
        bet_round = 1
        if cards[2] == 0:
            betting = [1, 2]
            to_act = 1
        else:
            betting = [2, 1]
            to_act = 2
        while True:
            if to_act == 1:
                p1 = [0]*12
                p1[cards[0]] = 1
                p1[5+cards[2]] = 1
                p1[6+bet_round] = 1
                pot1.append(betting[0])
                para1.append(p1)
                decision = f1.step(p1)
                if decision[0] == max(decision):#FOLD
                    d1.append('f')
                elif decision[1] == max(decision):#CALL
                    d1.append('c')
                else:#RAISE
                    d1.append('r')
    # TO BE CONTINUE


class Fighter():
    def __init__(self):
        self.net = neurolab.net.newff([[0, 1]]*12, [100, 3])
        net.init()
