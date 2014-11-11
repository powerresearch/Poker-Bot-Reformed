import json
import time
import random
from math import exp
from pokerstars.config import BB
from pokerstars.controller import Controller
from strategy.config import preflop_move_ep
from strategy.config import preflop_move_lp
from public import * 

class PreflopDecisionMaker():#{{{
    def __init__(self, game_driver):
        self.data_manager = game_driver.data_manager#{{{
        self.controller = Controller(game_driver, game_driver.shift)
        self.game_driver = game_driver
        self.button = game_driver.button
        self.stats_handler = game_driver.stats_handler#}}}

    def get_preflop_move(self, cards):
        big_card = max([cards[0][0], cards[1][0]])#{{{
        small_card = min([cards[0][0], cards[1][0]])
        if sum(self.game_driver.active) == 2 and self.button == 4 and\
                sum(self.game_driver.active[1:5]) == 0:
            ml = 1
        else:
            ml = 0
        if cards[0][1] == cards[1][1]:
            suited = 1
        else:
            suited = 0
        if self.button == 0 or self.button == 1 or ml:
            if suited:
                my_move = preflop_move_lp[small_card][big_card]
            else:
                my_move = preflop_move_lp[big_card][small_card]
        else:
            if suited:
                my_move = preflop_move_ep[small_card][big_card]
            else:
                my_move = preflop_move_ep[big_card][small_card]
        return my_move#}}}

    def update(self, game_driver):
        self.stage = game_driver.stage#{{{
        self.button = game_driver.button
        self.cards = game_driver.cards
        self.bet_round = game_driver.bet_round
        self.people_play = game_driver.people_play
        self.all_limper = game_driver.all_limper
        self.last_better = game_driver.last_better
        self.betting = game_driver.betting
        self.pot = game_driver.pot#}}}

    def make_decision(self, game_driver):
        self.update(game_driver)#{{{
        if game_driver.stage == 0:
            self.preflop_strategy()#}}}

    def preflop_strategy(self):
        my_move = self.get_preflop_move(self.cards)#{{{
        betting = self.betting
        people_bet = self.bet_round
        button = self.button 
        people_play = self.people_play
        dm = self.data_manager
        if self.game_driver.source == 'ps':
            if sum(self.game_driver.active) == 1:
                print 'Bugged'
                self.game_driver.fold = 1
                self.controller.fold()
                return
            if my_move == 0 or my_move == 1:
                if (button == 0 or button == 1) and people_bet == 1 and people_play == 1:#{{{
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+1)%6, u'SFBS')
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS') 
                    print 'Fold To Button Steal: '+str(fold_chance)
                    if fold_chance > 0.6 or random.random() > 0.5:
                        self.controller.rais(3*BB)
                        return
                if button == 5 and people_bet == 1 and people_play == 1:
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS')
                    print 'Fold To Button Steal: '+str(fold_chance)
                    if fold_chance > 0.6:
                        self.controller.rais(3*BB)
                        return 
                if people_bet == 2 and people_play == 1 and button >= 4:
                    for i in xrange(1, 6):
                        if betting[i] == max(betting):
                            better = i
                    if better == button:
                        print 'BSA: ', dm.get_item(better, u'BSA')
                        if dm.get_item(better, u'BSA') > 0.6:
                            self.controller.rais(3*max(betting))
                            return
                if people_bet == 2:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B')
                    print 'Fold To 3 Bet: '+str(fold_chance)
                    if fold_chance > 0.7:
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return
                if people_bet == 2 and people_play == 1:
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            print 'PFR', i, dm.get_item(i, 'pfr') 
                            if dm.get_item(i, 'pfr') > 0.5:
                                self.controller.rais(max(betting)*3)
                                return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B') 
                    print 'Fold To 4 Bet: '+str(fold_chance)
                    if fold_chance > 0.7:
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return 
                if people_bet == 3 and max(betting) - betting[0] <= BB*3:
                    self.controller.call()
                    return
                if people_bet == 1 and people_play == 1 and button == 1:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    fold_chance *= (1-dm.get_item(3, 'vpip'))
                    if fold_chance > 0.8:
                        print 'Low VPIP, Steal, Fold Chance: ', fold_chance
                        self.controller.rais(BB*3)
                        return
                if people_bet == 1 and people_play == 1 and button == 0:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    if fold_chance > 0.8:
                        print 'Low VPIP, Steal, Fold Chance: ', fold_chance
                        self.controller.rais(BB*3)
                        return
                if people_bet == 1 and people_play == 1 and button == 5:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    if fold_chance > 0.9:
                        print 'Low VPIP, Steal, Fold Chance: ', fold_chance
                        self.controller.rais(BB*3)
                        return
                if people_bet == 1 and my_move == 1:
                    self.controller.rais(BB*(2+people_play))
                    return
                if betting[0] == max(betting):
                    self.controller.call()
                    return
                if people_bet == 1 and button == 4:
                    self.controller.call()
                    return
                if (max(betting)-betting[0]) / (sum(betting[1:])+max(betting)) < 0.33\
                        and self.cards[0][0] == self.cards[1][0]:
                    self.controller.call()
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 1.5:
                if (button == 0 or button == 1) and people_bet == 1 and people_play == 1:#{{{
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+1)%6, u'SFBS')
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS') 
                    print 'Fold To Button Steal: '+str(fold_chance)
                    if fold_chance > 0.6 or random.random() > 0.5:
                        self.controller.rais(3*BB)
                        return
                if button == 5 and people_bet == 1 and people_play == 1:
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS')
                    print 'Fold To Button Steal: '+str(fold_chance)
                    if fold_chance > 0.6:
                        self.controller.rais(3*BB)
                        return 
                if people_bet == 2 and people_play == 1 and button >= 4:
                    for i in xrange(1, 6):
                        if betting[i] == max(betting):
                            better = i
                    if better == button:
                        print 'BSA: ', dm.get_item(better, u'BSA')
                        if dm.get_item(better, u'BSA') > 0.6:
                            self.controller.rais(3*max(betting))
                            return
                if people_bet == 2:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B')
                    print 'Fold To 3 Bet: '+str(fold_chance)
                    if fold_chance > 0.7:
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return
                if people_bet == 2 and people_play == 1:
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            print 'PFR', i, dm.get_item(i, 'pfr') 
                            if dm.get_item(i, 'pfr') > 0.5:
                                self.controller.rais(max(betting)*3)
                                return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B') 
                    print 'Fold To 4 Bet: '+str(fold_chance)
                    if fold_chance > 0.7:
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return 
                if people_bet == 3 and max(betting) - betting[0] <= BB*3:
                    self.controller.call()
                    return
                if people_bet == 1 and people_play == 1 and button == 1:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    fold_chance *= (1-dm.get_item(3, 'vpip'))
                    if fold_chance > 0.8:
                        print 'Low VPIP, Steal, Fold Chance: ', fold_chance
                        self.controller.rais(BB*3)
                        return
                if people_bet == 1 and people_play == 1 and button == 0:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    if fold_chance > 0.8:
                        print 'Low VPIP, Steal, Fold Chance: ', fold_chance
                        self.controller.rais(BB*3)
                        return
                if people_bet == 1 and people_play == 1 and button == 5:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    if fold_chance > 0.9:
                        print 'Low VPIP, Steal, Fold Chance: ', fold_chance
                        self.controller.rais(BB*3)
                        return
                if people_bet == 1 and my_move == 1.5:
                    self.controller.rais(BB*(2+people_play))
                    return
                if betting[0] == max(betting):
                    self.controller.call()
                    return
                if people_bet == 2 and my_move == 1.5 and max(betting)-betting[0] <= 0.08:
                    self.controller.call()
                    return
                if people_bet == 1 and button == 4:
                    self.controller.call()
                    return
                if (max(betting)-betting[0]) / (sum(betting[1:])+max(betting)) < 0.33\
                        and self.cards[0][0] == self.cards[1][0]:
                    self.controller.call()
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 2:
                if people_bet == 1:#{{{
                    self.controller.rais(BB*(people_play+2))
                    return
                if people_bet == 2: 
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B')
                    print 'Fold To 3 Bet: '+str(fold_chance)
                    if fold_chance > 0.7:
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return
                if people_bet == 2 and people_play == 1 and button >= 4:
                    for i in xrange(1, 6):
                        if betting[i] == max(betting):
                            better = i
                    if better == button:
                        print better, 'BSA', dm.get_item(better, u'BSA') 
                        if dm.get_item(better, u'BSA') > 0.7:
                            self.controller.rais(3*max(betting))
                            return 
                if people_bet == 2 and people_play == 1:
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            print i, 'PFR', dm.get_item(i, 'pfr') 
                            if dm.get_item(i, 'pfr') > 0.5:
                                self.controller.rais(max(betting)*3)
                                return 
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B') 
                    print 'Fold To 4 Bet: '+str(fold_chance)
                    if fold_chance > 0.7:
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return 
                if people_bet == 2:
                    self.controller.call()
                    return 
                if people_bet == 3 and max(betting) - betting[0] <= BB*3:
                    self.controller.call()
                    return
                if betting[0] == max(betting):
                    print 'bugged'
                    self.controller.call()
                    return
                if (max(betting)-betting[0]) / (sum(betting[1:])+max(betting)) < 0.33\
                        and self.cards[0][0] == self.cards[1][0]:
                    self.controller.call()
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 3:
                if people_bet == 1:#{{{
                    self.controller.rais((people_play+2)*BB)
                    return
                if people_bet == 2:
                    self.controller.rais(max(betting)*(1.8+people_play*0.6)+2*BB)
                    return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B')
                            print i, 'F4B', dm.get_item(i, u'F4B')
                    if fold_chance > 0.8:
                        print 'Fold To 4 Bet: '+str(fold_chance)
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return 
                    else:
                        self.controller.call()
                        return
                self.controller.fold()
                return#}}}
            if my_move == 4:
                if people_bet >= 3:#{{{
                    self.controller.rais(max(betting)*(people_play+2), 5)
                else:
                    self.controller.rais(max(betting)*(people_play+2))
                return#}}}
#}}}

    def fast_fold(self, game_driver):
        self.update(game_driver)#{{{
        if game_driver.stage == 0:
            self.fast_fold_preflop()#}}}

    def fast_fold_preflop(self):
        my_move = self.get_preflop_move(self.cards)#{{{
        betting = self.betting
        people_bet = self.bet_round
        button = self.button 
        people_play = self.people_play
        if betting[0] == max(betting):
            return
        dm = self.data_manager
        if self.game_driver.source == 'ps':
            if my_move == 0 or my_move == 1:
                if (button == 0 or button == 1) and people_bet == 1 and people_play == 1:#{{{
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+1)%6, u'SFBS')
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS') 
                    if fold_chance > 0.6:
                        return
                if button == 5 and people_bet == 1 and people_play == 1:
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS')
                    if fold_chance > 0.6:
                        return 
                if people_bet == 2 and people_play == 1 and button >= 4:
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            better = i
                    if better == button:
                        if dm.get_item(better, u'BSA') > 0.7:
                            return
                if people_bet == 2:
                    fold_chance = 1.0
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B')
                    if fold_chance > 0.7:
                        return
                if people_bet == 2 and people_play == 1:
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            if dm.get_item(i, 'pfr') > 0.5:
                                return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B') 
                    if fold_chance > 0.7:
                        return 
                if people_bet == 3 and max(betting) - betting[0] <= BB*3:
                    return
                if people_bet == 1 and people_play == 1 and button == 1:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    fold_chance *= (1-dm.get_item(3, 'vpip'))
                    if fold_chance > 0.8:
                        return
                if people_bet == 1 and people_play == 1 and button == 0:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    if fold_chance > 0.8:
                        return
                if people_bet == 1 and people_play == 1 and button == 5:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    if fold_chance > 0.9:
                        return
                if people_bet == 1 and my_move == 1:
                    return
                if betting[0] == max(betting):
                    return
                if (max(betting)-betting[0]) / (sum(betting[1:])+max(betting)) < 0.33\
                        and self.cards[0][0] == self.cards[1][0]:
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 1.5:
                if (button == 0 or button == 1) and people_bet == 1 and people_play == 1:#{{{
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+1)%6, u'SFBS')
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS') 
                    if fold_chance > 0.6:
                        return
                if button == 5 and people_bet == 1 and people_play == 1:
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS')
                    if fold_chance > 0.6:
                        return 
                if people_bet == 2 and people_play == 1 and button >= 4:
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            better = i
                    if better == button:
                        if dm.get_item(better, u'BSA') > 0.7:
                            return
                if people_bet == 2:
                    fold_chance = 1.0
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B')
                    if fold_chance > 0.7:
                        return
                if people_bet == 2 and people_play == 1:
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            if dm.get_item(i, 'pfr') > 0.5:
                                return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B') 
                    if fold_chance > 0.7:
                        return 
                if people_bet == 3 and max(betting) - betting[0] <= BB*3:
                    return
                if people_bet == 1 and people_play == 1 and button == 1:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    fold_chance *= (1-dm.get_item(3, 'vpip'))
                    if fold_chance > 0.8:
                        return
                if people_bet == 1 and people_play == 1 and button == 0:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    fold_chance *= (1-dm.get_item(2, 'vpip'))
                    if fold_chance > 0.8:
                        return
                if people_bet == 1 and people_play == 1 and button == 5:
                    fold_chance = 1.0
                    fold_chance *= (1-dm.get_item(1, 'vpip'))
                    if fold_chance > 0.9:
                        return
                if people_bet == 1 and my_move == 1.5:
                    return
                if betting[0] == max(betting):
                    return
                if people_bet == 2 and my_move == 1.5 and max(betting)-betting[0] <= 4*BB:
                    return
                if (max(betting)-betting[0]) / (sum(betting[1:])+max(betting)) < 0.33\
                        and self.cards[0][0] == self.cards[1][0]:
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 2:
                if people_bet == 1:#{{{
                    return
                if people_bet == 2: 
                    fold_chance = 1.0
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B')
                    if fold_chance > 0.7:
                        return
                if people_bet == 2 and people_play == 1 and button >= 4:
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            better = i
                    if better == button:
                        if dm.get_item(better, u'BSA') > 0.7:
                            return 
                if people_bet == 2 and people_play == 1:
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            if dm.get_item(i, 'pfr') > 0.5:
                                return 
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B') 
                    if fold_chance > 0.7:
                        return 
                if people_bet == 2:
                    return 
                if betting[0] == max(betting):
                    print 'bugged'
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 3:
                if people_bet == 1:#{{{
                    return
                if people_bet == 2:
                    return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B')
                    if fold_chance > 0.8:
                        return 
                    else:
                        return
                self.controller.fold()
                return#}}}
            if my_move == 4:
                return#}}}
#}}}

class PostflopDecisionMaker():
    def __init__(self, game_driver, stats):
        self.stats          = stats#{{{
        self.game_driver    = game_driver
        self.betting        = [0, 0, 0, 0, 0, 0]
        self.controller     = Controller(game_driver, game_driver.shift)
        self.source         = game_driver.source#}}}

    def update_stats(self, actor, action):#{{{
        if self.source != 'ps':
            raw_input()
        stats_change = tree()
        if self.game_driver.stage == 1:
            if actor != 0:
                vdt = self.get_value_dummy_table_flop(actor, action)
            else:
                vdt = self.vdt
        elif self.game_driver.stage == 2:
            if actor != 0:
                vdt = self.get_value_dummy_table_turn(actor, action)
            else:
                vdt = self.vdt
        else:
            if actor != 0:
                vdt = self.get_value_dummy_table_river(actor, action)
            else:
                vdt = self.vdt
        if action == 0:
            action_name = 'check'
        elif sum(self.game_driver.betting) == action:
            action_name = 'bet'
        elif is_only_max(self.game_driver.betting, actor):
            action_name = 'raise'
        else:
            action_name = 'call'
        max_change = 0
        for n1,c1,n2,c2,p in nodes_of_tree(self.small_stats[actor], 4):
            total_value = 0 
            for action_name2 in vdt:
                total_value += max(0, vdt[action_name2][n1][c1][n2][c2])
            for action_name2 in vdt:
                if action_name2 == 'call' and total_value < 0.5:
                    vdt[action_name2][n1][c1][n2][c2] += 0.2
                    total_value += 0.2
                if action_name2 == 'raise' and total_value < 1.5:
                    total_value += min([0.8, 1.5-total_value])
            try:
                stats_change[n1][c1][n2][c2] = vdt[action_name][n1][c1][n2][c2] / total_value
            except:
                print n1, c1, n2, c2
                print vdt[action_name]
            if stats_change[n1][c1][n2][c2] < 0:
                stats_change[n1][c1][n2][c2] = 0
            stats_change[n1][c1][n2][c2] = pow(stats_change[n1][c1][n2][c2], 3)
            max_change = max(max_change, stats_change[n1][c1][n2][c2])
        for n1,c1,n2,c2,p in nodes_of_tree(self.small_stats[actor], 4):
            stats_change[n1][c1][n2][c2] /= max_change
        for n1,c1,n2,c2,p in nodes_of_tree(self.stats[actor], 4):
            the_color = color_make_different(self.game_driver.cards[2:self.game_driver.stage+4]\
                    +[[n1, c1], [n2, c2]])
            if not c1 in the_color:
                cc1 = 0
            else:
                cc1 = c1
            if not c2 in the_color:
                cc2 = 0
            else:
                cc2 = c2
            try:
                self.stats[actor][n1][c1][n2][c2] *= stats_change[n1][cc1][n2][cc2]
            except:
                print stats_change
                print n1, cc1, n2, cc2
        self.compress_stats()
        if self.source != 'ps':
            show_stats(self.small_stats, stats_change, actor)
#}}}

    def update_wct(self):
        if self.game_driver.stage == 1:#{{{
            self.get_win_chance_table_flop()
        if self.game_driver.stage == 2:
            self.get_win_chance_table_turn()
        if self.game_driver.stage == 3:
            self.get_win_chance_table_river()
        self.get_win_chance_against()#}}}

    def compress_stats(self):
        self.small_stats = tree()#{{{
        for player in xrange(6):
            if not self.game_driver.active[player]:
                continue
            for n1, c1, n2, c2, prob in nodes_of_tree(self.stats[player], 4):
                the_color = color_make_different(self.game_driver.cards[2:]+[[n1, c1], [n2, c2]])
                if not c1 in the_color:
                    cc1 = 0
                else:
                    cc1 = c1
                if not c2 in the_color:
                    cc2 = 0
                else:
                    cc2 = c2
                if self.small_stats[player][n1][cc1][n2][cc2]:
                    self.small_stats[player][n1][cc1][n2][cc2] += prob
                else:
                    self.small_stats[player][n1][cc1][n2][cc2] = prob#}}}

    def clean_stats(self):#{{{
        cards = self.game_driver.cards
        if self.game_driver.stage == 1:
            for i in xrange(6):
                if self.game_driver.active[i] != 1:
                    continue
                try:
                    del self.stats[i][cards[2][0]][cards[2][1]]
                except:
                    pass
                try:
                    del self.stats[i][cards[3][0]][cards[3][1]]
                except:
                    pass
                try:
                    del self.stats[i][cards[4][0]][cards[4][1]]
                except:
                    pass
                for n1, c1, t in nodes_of_tree(self.stats[i], 2):
                    try:
                        del t[cards[2][0]][cards[2][1]]
                    except:
                        pass
                    try:
                        del t[cards[3][0]][cards[3][1]]
                    except:
                        pass
                    try:
                        del t[cards[4][0]][cards[4][1]]
                    except:
                        pass
        if self.game_driver.stage == 2:
            for i in xrange(6):
                if self.game_driver.active[i] != 1:
                    continue
                try:
                    del self.stats[i][cards[5][0]][cards[5][1]]
                except:
                    pass
                for n1, c1, t in nodes_of_tree(self.stats[i], 2):
                    try:
                        del t[cards[5][0]][cards[5][1]]
                    except:
                        pass
        if self.game_driver.stage == 3:
            for i in xrange(6):
                if self.game_driver.active[i] != 1:
                    continue
                try:
                    del self.stats[i][cards[6][0]][cards[6][1]]
                except:
                    pass
                for n1, c1, t in nodes_of_tree(self.stats[i], 2):
                    try:
                        del t[cards[6][0]][cards[6][1]]
                    except:
                        pass#}}}

    def get_avg_stats(self):
        players = list()#{{{
        for i in xrange(6):
            if self.game_driver.active[i] == 1:
                players.append(i)
        self.players = players
        l = len(players)
        self.stats.append(list())
        self.stats[6] = copy.deepcopy(self.stats[players[0]])
        self.small_stats[6] = copy.deepcopy(self.small_stats[players[0]])
        for i in players[1:]:
            for n1, c1, n2, c2, prob in nodes_of_tree(self.stats[i], 4):
                self.stats[6][n1][c1][n2][c2] += prob
        for i in players[1:]:
            for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[i], 4):
                self.small_stats[6][n1][c1][n2][c2] += prob
        for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[6], 4):
            self.small_stats[6][n1][c1][n2][c2] /= l
        for n1, c1, n2, c2, prob in nodes_of_tree(self.stats[6], 4):
            self.stats[6][n1][c1][n2][c2] /= l#}}}

    def get_opponent(self):
        self.opponent = [0, 0, 0, 0, 0, 0]#{{{
        for i in xrange(6):
            if not self.game_driver.active[i] == 1:
                continue
            if i != self.game_driver.last_better:
                self.opponent[i] = self.game_driver.last_better
            else:
                for j in xrange(6):
                    if self.game_driver.active[j] == 1 and j != self.game_driver.last_better:
                        self.opponent[i] = j#}}}
                            
    def get_win_chance_table_flop(self): # Win chance table of two specific hands
        board = copy.deepcopy(self.game_driver.cards[2:])#{{{
        # Get fo_cache{{{
        fo_cache = tree()
        for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[0], 4):
            fo_cache[n1][c1][n2][c2][0] = find_out(board+[[n1, c1], [n2, c2]])
            for num3, col3 in enum_cards(1):
                fo_cache[n1][c1][n2][c2][num3][col3]\
                        = find_out(board+[[n1, c1], [n2, c2]]+[[num3, col3]])#}}}
        #Get win_chance_table_small{{{
        wcts = tree()
        wctaa100 = tree()
        for n1, c1, n2, c2, prob1 in nodes_of_tree(self.small_stats[6], 4):
            prob_accumulation = 0
            win_chance_accumulation = 0
            if [n1, c1] in board or [n2, c2] in board:
                continue
            for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[6], 4):
                if [n3, c3] in board or [n4, c4] in board:
                    continue
                comb1 = [[n1, c1], [n2, c2]] 
                comb2 = [[n3, c3], [n4, c4]]
                if comb1[0][1] == 0:
                    for col in xrange(1, 5):
                        if [comb1[0][0], col] not in comb1+comb2+board:
                            comb1[0] = [comb1[0][0], col]
                            break
                if comb1[1][1] == 0:
                    for col in xrange(1, 5):
                        if [comb1[1][0], col] not in comb1+comb2+board:
                            comb1[1] = [comb1[1][0], col]
                            break
                if comb2[0][1] == 0:
                    for col in xrange(1, 5):
                        if [comb2[0][0], col] not in board+comb1+comb2:
                            comb2[0] = [comb2[0][0], col]
                            break
                if comb2[1][1] == 0:
                    for col in xrange(1, 5):
                        if [comb2[1][0], col] not in board+comb1+comb2:
                            comb2[1] = [comb2[1][0], col]
                            break
                if has_same(comb1+comb2):
                    continue
                if comb1[0][1] == 0 or comb1[1][1] == 0 or comb2[0][1] == 0 or comb2[1][1] == 0:
                    continue
                fo0 = fo_cache[n1][c1][n2][c2][0]
                fo1 = fo_cache[n3][c3][n4][c4][0]
                axis = list()
                if fo0 < fo1:
                    zero = [fo1, 'o']
                    stronger = 1
                elif fo0 == fo1:
                    zero = [fo0, 'o']
                    stronger = -1
                else:
                    zero = [fo0, 'o']
                    stronger = 0
                axis.append(zero)
                total_possibility = 0
                for num3, col3 in enum_cards(1):
                    if [num3, col3] in board+comb1+comb2:
                        continue
                    total_possibility += 1
                    if fo_cache[n3][c3][n4][c4][num3][col3] > fo_cache[n1][c1][n2][c2][num3][col3]:
                        axis.append([[0], 0])
                        axis.append([fo_cache[n3][c3][n4][c4][num3][col3], 1])
                    elif fo_cache[n1][c1][n2][c2][num3][col3] == fo_cache[n3][c3][n4][c4][num3][col3]:
                        axis.append([[0], 0])
                        axis.append([[0], 1])
                    else:
                        axis.append([fo_cache[n1][c1][n2][c2][num3][col3], 0])
                        axis.append([[0], 1])
                axis = sorted(axis, key=lambda x:x[0])
                zero_index = axis.index(zero)
                bb_count = 0
                bb_count0 = 0
                bb_count1 = 0
                anti_bb_count = 0
                for some_fo, belong_to in axis[zero_index+1:]:
                    if stronger != belong_to and stronger != -1:
                        bb_count += 1
                    if stronger == -1:
                        if belong_to == 0:
                            bb_count0 += 1
                        else:
                            bb_count1 += 1
                    if stronger == belong_to:
                        anti_bb_count += bb_count
                if stronger == 1:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                            = 1 - pow((1 - 1.0*bb_count/total_possibility), 2)
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                            = pow((1 - 1.0*bb_count/total_possibility), 2)
                    if bb_count > 0:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][1]\
                                = 1.0 * anti_bb_count/total_possibility/bb_count
                    else:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][1] = 0
                elif stronger == 0:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                            = pow((1 - 1.0*bb_count/total_possibility), 2)
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                            = 1 - pow((1 - 1.0*bb_count/total_possibility), 2)
                    if bb_count > 0:
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][1]\
                                = 1.0 * anti_bb_count / total_possibility / bb_count
                    else:
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][1] = 0
                else:
                    if bb_count0 > 0:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                                = 0.5 + 0.5 * (1 - pow((1 - 1.0*bb_count0/total_possibility), 2))
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                                = 0.5 - 0.5 * (1 - pow((1 - 1.0*bb_count0/total_possibility), 2))
                    elif bb_count1 > 0:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                                = 0.5 - 0.5 * (1 - pow((1 - 1.0*bb_count1/total_possibility), 2))
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                                = 0.5 + 0.5 * (1 - pow((1 - 1.0*bb_count1/total_possibility), 2))
                    else:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 0.5
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 0.5
            
#                a = [0, 0, 0] 
#                for num3, col3 in enum_cards(1):
#                    if [num3, col3] in board+comb1+comb2:
#                        continue
#                    fo10 = fo_cache[n1][c1][n2][c2][num3][col3] 
#                    fo11 = fo_cache[n3][c3][n4][c4][num3][col3] 
#                    if fo10 < fo11:
#                        a[2] += 1
#                    elif fo10 == fo11:
#                        a[1] += 1
#                    else:
#                        a[0] += 1
#                a = [1.0*hh/sum(a) for hh in a]
#                if stronger == 1:
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = 1 - (1 - a[0]) * (1 - a[0])
#                    wcts[n3][c3][n4][c4][n1][c1][n2][c2] = (1 - a[0]) * (1 - a[0])
#                elif stronger == 0:
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = (1 - a[2]) * (1 - a[2])
#                    wcts[n3][c3][n4][c4][n1][c1][n2][c2] = 1 - (1 - a[2]) * (1 - a[2])
#                else:
#                    tmp1 = 1 - (1 - a[0]) * (1 - a[0])
#                    tmp2 = 1 - (1 - a[2]) * (1 - a[2])
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = tmp1 + (1-tmp1-tmp2) / 2
#                    wcts[n3][c3][n4][c4][c1][c1][c2][c2] = tmp2 + (1-tmp1-tmp2) / 2
                win_chance_accumulation += wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] * prob2
                prob_accumulation += prob2
            wctaa100[n1][c1][n2][c2] = win_chance_accumulation / prob_accumulation#}}}
        self.flop_fo_cache = fo_cache
        self.wcts = wcts
        self.wctaa100 = wctaa100#}}}

    def get_win_chance_table_turn(self): # Win chance table of two specific hands
        board = copy.deepcopy(self.game_driver.cards[2:])#{{{
        # Get fo_cache{{{
        fo_cache = tree()
        for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[0], 4):
            fo_cache[n1][c1][n2][c2][0] = find_out(board+[[n1, c1], [n2, c2]])
            for num3, col3 in enum_cards(1):
                fo_cache[n1][c1][n2][c2][num3][col3]\
                        = find_out(board+[[n1, c1], [n2, c2]]+[[num3, col3]])#}}}
        #Get win_chance_table_small{{{
        wcts = tree()
        wctaa100 = tree()
        for n1, c1, n2, c2, prob1 in nodes_of_tree(self.small_stats[6], 4):
            prob_accumulation = 0
            win_chance_accumulation = 0
            if [n1, c1] in board or [n2, c2] in board:
                continue
            for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[6], 4):
                if [n3, c3] in board or [n4, c4] in board:
                    continue
                comb1 = [[n1, c1], [n2, c2]] 
                comb2 = [[n3, c3], [n4, c4]]
                if comb1[0][1] == 0:
                    for col in xrange(1, 5):
                        if [comb1[0][0], col] not in comb1+comb2+board:
                            comb1[0] = [comb1[0][0], col]
                            break
                if comb1[1][1] == 0:
                    for col in xrange(1, 5):
                        if [comb1[1][0], col] not in comb1+comb2+board:
                            comb1[1] = [comb1[1][0], col]
                            break
                if comb2[0][1] == 0:
                    for col in xrange(1, 5):
                        if [comb2[0][0], col] not in board+comb1+comb2:
                            comb2[0] = [comb2[0][0], col]
                            break
                if comb2[1][1] == 0:
                    for col in xrange(1, 5):
                        if [comb2[1][0], col] not in board+comb1+comb2:
                            comb2[1] = [comb2[1][0], col]
                            break
                if has_same(comb1+comb2):
                    continue
                if comb1[0][1] == 0 or comb1[1][1] == 0 or comb2[0][1] == 0 or comb2[1][1] == 0:
                    continue
                fo0 = fo_cache[n1][c1][n2][c2][0]
                fo1 = fo_cache[n3][c3][n4][c4][0]
                axis = list()
                if fo0 < fo1:
                    zero = [fo1, 'o']
                    stronger = 1
                elif fo0 == fo1:
                    zero = [fo0, 'o']
                    stronger = -1
                else:
                    zero = [fo0, 'o']
                    stronger = 0
                axis.append(zero)
                total_possibility = 0
                for num3, col3 in enum_cards(1):
                    if [num3, col3] in board+comb1+comb2:
                        continue
                    total_possibility += 1
                    if fo_cache[n3][c3][n4][c4][num3][col3] > fo_cache[n1][c1][n2][c2][num3][col3]:
                        axis.append([[0], 0])
                        axis.append([fo_cache[n3][c3][n4][c4][num3][col3], 1])
                    elif fo_cache[n1][c1][n2][c2][num3][col3] == fo_cache[n3][c3][n4][c4][num3][col3]:
                        axis.append([[0], 0])
                        axis.append([[0], 1])
                    else:
                        axis.append([fo_cache[n1][c1][n2][c2][num3][col3], 0])
                        axis.append([[0], 1])
                axis = sorted(axis, key=lambda x:x[0])
                zero_index = axis.index(zero)
                bb_count = 0
                bb_count0 = 0
                bb_count1 = 0
                anti_bb_count = 0
                for some_fo, belong_to in axis[zero_index+1:]:
                    if stronger != belong_to and stronger != -1:
                        bb_count += 1
                    if stronger == -1:
                        if belong_to == 0:
                            bb_count0 += 1
                        else:
                            bb_count1 += 1
                    if stronger == belong_to:
                        anti_bb_count += bb_count
                if stronger == 1:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                            = 1.0*bb_count/total_possibility
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                            = 1 - 1.0*bb_count/total_possibility
                    if bb_count > 0:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][1]\
                                = 1.0 * anti_bb_count/total_possibility/bb_count
                    else:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][1] = 0
                elif stronger == 0:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                            = 1 - 1.0*bb_count/total_possibility
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                            = 1.0*bb_count/total_possibility
                    if bb_count > 0:
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][1]\
                                = 1.0 * anti_bb_count / total_possibility / bb_count
                    else:
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][1] = 0
                else:
                    if bb_count0 > 0:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                                = 0.5 + 0.5 * 1.0*bb_count0/total_possibility
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                                = 0.5 - 0.5 * 1.0*bb_count0/total_possibility
                    elif bb_count1 > 0:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]\
                                = 0.5 - 0.5 * 1.0*bb_count1/total_possibility
                        wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]\
                                = 0.5 + 0.5 * 1.0*bb_count1/total_possibility
                    else:
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 0.5
                        wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 0.5
            
#                a = [0, 0, 0] 
#                for num3, col3 in enum_cards(1):
#                    if [num3, col3] in board+comb1+comb2:
#                        continue
#                    fo10 = fo_cache[n1][c1][n2][c2][num3][col3] 
#                    fo11 = fo_cache[n3][c3][n4][c4][num3][col3] 
#                    if fo10 < fo11:
#                        a[2] += 1
#                    elif fo10 == fo11:
#                        a[1] += 1
#                    else:
#                        a[0] += 1
#                a = [1.0*hh/sum(a) for hh in a]
#                if stronger == 1:
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = 1 - (1 - a[0]) * (1 - a[0])
#                    wcts[n3][c3][n4][c4][n1][c1][n2][c2] = (1 - a[0]) * (1 - a[0])
#                elif stronger == 0:
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = (1 - a[2]) * (1 - a[2])
#                    wcts[n3][c3][n4][c4][n1][c1][n2][c2] = 1 - (1 - a[2]) * (1 - a[2])
#                else:
#                    tmp1 = 1 - (1 - a[0]) * (1 - a[0])
#                    tmp2 = 1 - (1 - a[2]) * (1 - a[2])
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = tmp1 + (1-tmp1-tmp2) / 2
#                    wcts[n3][c3][n4][c4][c1][c1][c2][c2] = tmp2 + (1-tmp1-tmp2) / 2
                win_chance_accumulation += wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] * prob2
                prob_accumulation += prob2
            wctaa100[n1][c1][n2][c2] = win_chance_accumulation / prob_accumulation#}}}
        self.turn_fo_cache = fo_cache
        self.wcts = wcts
        self.wctaa100 = wctaa100#}}}

    def get_win_chance_table_river(self): # Win chance table of two specific hands
        board = copy.deepcopy(self.game_driver.cards[2:])#{{{
        # Get fo_cache{{{
        fo_cache = tree()
        for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[0], 4):
            fo_cache[n1][c1][n2][c2][0] = find_out(board+[[n1, c1], [n2, c2]])#}}}
        #Get win_chance_table_small{{{
        wcts = tree()
        wctaa100 = tree()
        for n1, c1, n2, c2, prob1 in nodes_of_tree(self.small_stats[6], 4):
            prob_accumulation = 0
            win_chance_accumulation = 0
            if [n1, c1] in board or [n2, c2] in board:
                continue
            for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[6], 4):
                if [n3, c3] in board or [n4, c4] in board:
                    continue
                comb1 = [[n1, c1], [n2, c2]] 
                comb2 = [[n3, c3], [n4, c4]]
                if comb1[0][1] == 0:
                    for col in xrange(1, 5):
                        if [comb1[0][0], col] not in comb1+comb2+board:
                            comb1[0] = [comb1[0][0], col]
                            break
                if comb1[1][1] == 0:
                    for col in xrange(1, 5):
                        if [comb1[1][0], col] not in comb1+comb2+board:
                            comb1[1] = [comb1[1][0], col]
                            break
                if comb2[0][1] == 0:
                    for col in xrange(1, 5):
                        if [comb2[0][0], col] not in board+comb1+comb2:
                            comb2[0] = [comb2[0][0], col]
                            break
                if comb2[1][1] == 0:
                    for col in xrange(1, 5):
                        if [comb2[1][0], col] not in board+comb1+comb2:
                            comb2[1] = [comb2[1][0], col]
                            break
                if has_same(comb1+comb2):
                    continue
                if comb1[0][1] == 0 or comb1[1][1] == 0 or comb2[0][1] == 0 or comb2[1][1] == 0:
                    continue
                fo0 = fo_cache[n1][c1][n2][c2][0]
                fo1 = fo_cache[n3][c3][n4][c4][0]
                if fo0 > fo1:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 1.0
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0] = 0.0
                elif fo0 < fo1:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 0.0 
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0] = 1.0
                else:
                    wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] = 0.5 
                    wcts[n3][c3][n4][c4][n1][c1][n2][c2][0] = 0.5
            
#                a = [0, 0, 0] 
#                for num3, col3 in enum_cards(1):
#                    if [num3, col3] in board+comb1+comb2:
#                        continue
#                    fo10 = fo_cache[n1][c1][n2][c2][num3][col3] 
#                    fo11 = fo_cache[n3][c3][n4][c4][num3][col3] 
#                    if fo10 < fo11:
#                        a[2] += 1
#                    elif fo10 == fo11:
#                        a[1] += 1
#                    else:
#                        a[0] += 1
#                a = [1.0*hh/sum(a) for hh in a]
#                if stronger == 1:
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = 1 - (1 - a[0]) * (1 - a[0])
#                    wcts[n3][c3][n4][c4][n1][c1][n2][c2] = (1 - a[0]) * (1 - a[0])
#                elif stronger == 0:
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = (1 - a[2]) * (1 - a[2])
#                    wcts[n3][c3][n4][c4][n1][c1][n2][c2] = 1 - (1 - a[2]) * (1 - a[2])
#                else:
#                    tmp1 = 1 - (1 - a[0]) * (1 - a[0])
#                    tmp2 = 1 - (1 - a[2]) * (1 - a[2])
#                    wcts[n1][c1][n2][c2][n3][c3][n4][c4] = tmp1 + (1-tmp1-tmp2) / 2
#                    wcts[n3][c3][n4][c4][c1][c1][c2][c2] = tmp2 + (1-tmp1-tmp2) / 2
                win_chance_accumulation += wcts[n1][c1][n2][c2][n3][c3][n4][c4][0] * prob2
                prob_accumulation += prob2
            wctaa100[n1][c1][n2][c2] = win_chance_accumulation / prob_accumulation#}}}
        self.flop_fo_cache = fo_cache
        self.wcts = wcts
        self.wctaa100 = wctaa100#}}}

    def get_win_chance_against(self):# Get win chance against top25%/50% cards. (use avg stats as opponent)#{{{
        l = sorted([[wc, n1, c1, n2, c2] for n1, c1, n2, c2, wc in nodes_of_tree(self.wctaa100, 4)],\
                key=lambda x:x[0], reverse=True)
        wctaa25 = tree()
        wctaa50 = tree()
        total_prob = 0
        for comb in l:
            total_prob += self.small_stats[6][comb[1]][comb[2]][comb[3]][comb[4]]
        for n1, c1, n2, c2, wc in nodes_of_tree(self.wctaa100, 4):
            current_prob50 = 0
            current_prob25 = 0
            wctaa50[n1][c1][n2][c2] = 0
            wctaa25[n1][c1][n2][c2] = 0
            for comb in l:
                n3, c3, n4, c4 = comb[1:]
                current_prob50 += self.small_stats[6][n3][c3][n4][c4]
                if current_prob50 > 0.5 * total_prob:
                    wctaa50[n1][c1][n2][c2] /= current_prob50
                    wctaa25[n1][c1][n2][c2] /= current_prob25
                    break
                if current_prob50 < 0.25 * total_prob:
                    try:
                        wctaa25[n1][c1][n2][c2] += self.small_stats[6][n3][c3][n4][c4]\
                                * self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]
                    except:
                        pass
                try:
                    wctaa50[n1][c1][n2][c2] += self.small_stats[6][n3][c3][n4][c4]\
                            * self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]
                except:
                    current_prob50 -= self.small_stats[6][n3][c3][n4][c4]
                if current_prob25 == 0 and current_prob50 > 0.25 * total_prob:
                    current_prob25 = current_prob50
        self.wctaa25 = wctaa25
        self.wctaa50 = wctaa50#}}}

    def get_dummy_action(self):#{{{
        if self.game_driver.stage == 1:
            self.get_dummy_action_flop()
        if self.game_driver.stage == 2:
            self.get_dummy_action_turn()
        if self.game_driver.stage == 3:
            self.get_dummy_action_river()#}}}
            
    def get_dummy_action_flop(self):# Set some naive strategy decided by win chance against avg stats.
        dummy_action_ep = tree()#{{{
        dummy_action_lp = tree()
        player_number = sum([self.game_driver.active[i] != 0 for i in xrange(6)])
        for n1, c1, n2, c2, wc in nodes_of_tree(self.wctaa100, 4):
            w100 = self.wctaa100[n1][c1][n2][c2]
            w50 = self.wctaa50[n1][c1][n2][c2]
            w25 = self.wctaa25[n1][c1][n2][c2]
            if w50 > 0.6 and w25 > 0.4:
                dummy_action_ep[n1][c1][n2][c2]['raise'] = 1
                dummy_action_lp[n1][c1][n2][c2]['raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check raise'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w50 > 0.5:
                dummy_action_lp[n1][c1][n2][c2]['call raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['call raise'] = 1
            if w100 > 0.7 or w50 > 0.4 or w25 > 0.25:
                dummy_action_ep[n1][c1][n2][c2]['bet'] = 1
            if w100 > 0.5 or w50 > 0.3 or w25 > 0.2:
                dummy_action_lp[n1][c1][n2][c2]['bet'] = 1
            if w50 > 0.25 or w100 > 0.5 or w25 > 0.15:
                dummy_action_lp[n1][c1][n2][c2]['call bet'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check call'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w50 > 0.35 or w100 > 0.5 or w25 > 0.2:
                dummy_action_ep[n1][c1][n2][c2]['check call'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_ep[n1][c1][n2][c2]['call bet'] = 1
            if w100 <= 0.6 and w50 <= 0.3 and w25 <= 0.25:
                dummy_action_lp[n1][c1][n2][c2]['fold'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w100 <= 0.6 and w50 <= 0.4:
                dummy_action_ep[n1][c1][n2][c2]['check fold'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_ep[n1][c1][n2][c2]['fold'] = 1
        self.dummy_action_ep = dummy_action_ep
        self.dummy_action_lp = dummy_action_lp#}}}
        if self.source != 'ps':
            self.show_dummy_action()

    def get_dummy_action_turn(self):# Set some naive strategy decided by win chance against avg stats.
        dummy_action_ep = tree()#{{{
        dummy_action_lp = tree()
        player_number = sum([self.game_driver.active[i] != 0 for i in xrange(6)])
        for n1, c1, n2, c2, wc in nodes_of_tree(self.wctaa100, 4):
            w100 = self.wctaa100[n1][c1][n2][c2]
            w50 = self.wctaa50[n1][c1][n2][c2]
            w25 = self.wctaa25[n1][c1][n2][c2]
            if w50 > 0.5 and w25 > 0.2:
                dummy_action_ep[n1][c1][n2][c2]['raise'] = 1
                dummy_action_lp[n1][c1][n2][c2]['raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check raise'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w50 > 0.2 or w100 > 0.5:
                dummy_action_lp[n1][c1][n2][c2]['call raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['call raise'] = 1
            if w100 > 0.7 or w50 > 0.5 or w25 > 0.3:
                dummy_action_ep[n1][c1][n2][c2]['bet'] = 1
                dummy_action_lp[n1][c1][n2][c2]['bet'] = 1
            if w50 > 0.3 or w100 > 0.45 or w25 > 0.2:
                dummy_action_ep[n1][c1][n2][c2]['call bet'] = 1
                dummy_action_lp[n1][c1][n2][c2]['call bet'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check call'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check call'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w100 <= 0.5 and w50 <= 0.3 and w25 <= 0.25:
                dummy_action_lp[n1][c1][n2][c2]['fold'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w100 <= 0.5 and w50 <= 0.3:
                dummy_action_ep[n1][c1][n2][c2]['check fold'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_ep[n1][c1][n2][c2]['fold'] = 1
        self.dummy_action_ep = dummy_action_ep
        self.dummy_action_lp = dummy_action_lp#}}}
        if self.source != 'ps':
            self.show_dummy_action()

    def get_dummy_action_river(self):# Set some naive strategy decided by win chance against avg stats.
        dummy_action_ep = tree()#{{{
        dummy_action_lp = tree()
        player_number = sum([self.game_driver.active[i] != 0 for i in xrange(6)])
        for n1, c1, n2, c2, wc in nodes_of_tree(self.wctaa100, 4):
            w100 = self.wctaa100[n1][c1][n2][c2]
            w50 = self.wctaa50[n1][c1][n2][c2]
            w25 = self.wctaa25[n1][c1][n2][c2]
            if w100 > 0.75:
                dummy_action_ep[n1][c1][n2][c2]['raise'] = 1
                dummy_action_lp[n1][c1][n2][c2]['raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check raise'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w100 > 0.7:
                dummy_action_lp[n1][c1][n2][c2]['call raise'] = 1
                dummy_action_ep[n1][c1][n2][c2]['call raise'] = 1
            if w100 > 0.6:
                dummy_action_ep[n1][c1][n2][c2]['bet'] = 1
                dummy_action_lp[n1][c1][n2][c2]['bet'] = 1
            if w100 > 0.5:
                dummy_action_ep[n1][c1][n2][c2]['call bet'] = 1
                dummy_action_lp[n1][c1][n2][c2]['call bet'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check call'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check call'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w100 <= 0.5:
                dummy_action_lp[n1][c1][n2][c2]['fold'] = 1
                dummy_action_lp[n1][c1][n2][c2]['check'] = 1
            if w100 <= 0.5:
                dummy_action_ep[n1][c1][n2][c2]['check fold'] = 1
                dummy_action_ep[n1][c1][n2][c2]['check'] = 1
                dummy_action_ep[n1][c1][n2][c2]['fold'] = 1
        self.dummy_action_ep = dummy_action_ep
        self.dummy_action_lp = dummy_action_lp#}}}
        if self.source != 'ps':
            self.show_dummy_action()

    def get_value_dummy_table_flop(self, actor, action):# Suppose there are only two players left.
        bet = 0.8#{{{
        vdt = tree()
        the_color = color_make_different(self.game_driver.cards)
        mn1, mc1 = min(self.game_driver.cards[:2])
        mn2, mc2 = max(self.game_driver.cards[:2])
        if mc1 not in the_color:
            mc1 = 0
        if mc2 not in the_color:
            mc2 = 0
        if self.game_driver.last_mover == actor:
            if max(self.betting) == self.betting[actor]:#{{{
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['bet'][n1][c1][n2][c2] = 0
                    vdt['check'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        if 'fold' in self.dummy_action_ep[n3][c3][n4][c4]:
                            numerator = 1
                            denominator = 1
                        else:
                            numerator = 0
                            denominator = 0
                        if 'call bet' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        if 'raise' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            fold_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_ep[n3][c3][n4][c4]
                            raise Exception
                        if 'bet' in self.dummy_action_ep[n3][c3][n4][c4]:
                            numerator = self.dummy_action_ep[n3][c3][n4][c4]['bet']
                            denominator = self.dummy_action_ep[n3][c3][n4][c4]['bet']
                        else:
                            numerator = 0
                            denominator = 0
                        if 'check' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            bet_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_ep[n3][c3][n4][c4]
                            raise Exception
                        try:
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, rais=0)
                            vdt['bet'][n1][c1][n2][c2] += prob2 * (fold_chance\
                                    + (1 - fold_chance) * v) 
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'bet  \t', round(prob2, 2), '\t', \
                                        n3, c3, n4, c4, '\t',\
                                        round(fold_chance, 2), round(v, 2),\
                                        round(fold_chance + (1 - fold_chance)*v, 2)
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, bet=0, rais=0)
                            if v < 0:
                                v = 0
                            vdt['check'][n1][c1][n2][c2] += prob2 * v
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'check\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except:
                            continue
                    vdt['bet'][n1][c1][n2][c2] /= prob_accumulation
                    vdt['check'][n1][c1][n2][c2] /= prob_accumulation
                    if self.source != 'ps' and actor != 0:
                        print n1, c1, n2, c2, '\t',\
                                round(vdt['bet'][n1][c1][n2][c2], 2), '\t',\
                                round(vdt['check'][n1][c1][n2][c2], 2)
                    vdt['check'][n1][c1][n2][c2] = max(0.4, vdt['check'][n1][c1][n2][c2])
                try:
                    del vdt['check1']
                    del vdt['check2']
                except:
                    pass
                return vdt#}}}
            else:#{{{
                to_call = max(self.betting) - self.betting[actor]
                to_call /= (self.game_driver.pot - action - sum(self.betting))
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['call'][n1][c1][n2][c2] = 0
                    vdt['raise'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    value_from_fold = 0
                    value_from_call = 0
                    fold_prob = 0
                    call_prob = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        try:
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call)
                            if 'call raise' in self.dummy_action_ep[n3][c3][n4][c4]\
                                    or 'raise' in self.dummy_action_ep[n3][c3][n4][c4]:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * v
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                                value_from_call += prob2 * v 
                                call_prob += prob2 
                            else:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round((to_call+1), 2)
                                value_from_fold += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                fold_prob += prob2
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call, rais=0)
                            vdt['call'][n1][c1][n2][c2] += prob2 * v
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'call \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except Exception as e:
                            continue
                    try:
                        value_from_fold /= (fold_prob+call_prob)
                        value_from_call /= (fold_prob+call_prob)
                        fold_prob, call_prob = fold_prob / (fold_prob+call_prob),\
                                call_prob / (fold_prob+call_prob)
                        vdt['raise'][n1][c1][n2][c2] /= prob_accumulation
                        vdt['call'][n1][c1][n2][c2] /= prob_accumulation
                        if self.source != 'ps' and actor != 0:
                            print n1, c1, n2, c2, '\t', round(self.wctaa50[n1][c1][n2][c2], 2), '\t',\
                                    round(fold_prob, 2), round(call_prob, 2), '\t',\
                                    round(vdt['raise'][n1][c1][n2][c2], 2), '\t',\
                                    round(vdt['call'][n1][c1][n2][c2], 2), '\t',\
                                    round(value_from_fold, 2), round(value_from_call, 2)
                    except Exception as e:
                        print e
                        print n1, c1, n2, c2
                        if self.source != 'ps':
                            raw_input()
                return vdt#}}}
        else:
            if max(self.betting) == self.betting[actor]:#{{{
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['check1'][n1][c1][n2][c2] = 0
                    vdt['check2'][n1][c1][n2][c2] = 0
                    vdt['bet'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        if 'fold' in self.dummy_action_lp[n3][c3][n4][c4]:
                            numerator = 1
                            denominator = 1
                        else:
                            numerator = 0
                            denominator = 0
                        if 'call bet' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        if 'raise' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            fold_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_lp[n3][c3][n4][c4]
                            raise Exception
                        if 'bet' in self.dummy_action_lp[n3][c3][n4][c4]:
                            numerator = self.dummy_action_lp[n3][c3][n4][c4]['bet'] 
                            denominator = self.dummy_action_lp[n3][c3][n4][c4]['bet']
                        else:
                            numerator = 0
                            denominator = 0
                        if 'check' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            bet_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_lp[n3][c3][n4][c4]
                            raise Exception
                        try:
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, rais=0)
                            vdt['bet'][n1][c1][n2][c2] += prob2 * (fold_chance\
                                    + (1 - fold_chance) * v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'bet       \t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(fold_chance, 2), round(v, 2),\
                                        round(fold_chance + (1-fold_chance)*v, 2)
                            v2 = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, bet=0, rais=0)
                            if v2 < 0:
                                v2 = 0
                            vdt['check1'][n1][c1][n2][c2] += prob2 * ((1-bet_chance) * v2)
                            vdt['check2'][n1][c1][n2][c2] += prob2 * ((1-bet_chance)*v2 + bet_chance*v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'check fold\t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(bet_chance, 2), round(v2, 2),\
                                        round((1-bet_chance) * v2, 2)
                                print 'check call\t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(bet_chance, 2), round(v, 2),\
                                        round((1-bet_chance)*v2 + bet_chance*v, 2)
                            prob_accumulation += prob2
                        except:
                            continue
                    vdt['bet'][n1][c1][n2][c2] /= prob_accumulation
                    vdt['check'][n1][c1][n2][c2] = max(vdt['check1'][n1][c1][n2][c2],\
                            vdt['check2'][n1][c1][n2][c2]) / prob_accumulation
                    if self.source != 'ps' and actor != 0:
                        print n1, c1, n2, c2, '\t',\
                                round(vdt['bet'][n1][c1][n2][c2], 2), '\t',\
                                round(vdt['check'][n1][c1][n2][c2], 2)
                    vdt['check'][n1][c1][n2][c2] = max(0.4, vdt['check'][n1][c1][n2][c2])
                try:
                    del vdt['check1']
                    del vdt['check2']
                except:
                    pass
                return vdt#}}}
            else:#{{{
                to_call = max(self.betting) - self.betting[actor]
                to_call /= (self.game_driver.pot - action - sum(self.betting))
                rais = 1 + to_call
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['call'][n1][c1][n2][c2] = 0
                    vdt['raise'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    value_from_fold = 0
                    value_from_call = 0
                    fold_prob = 0
                    call_prob = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        try:
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call)
                            if 'call raise' in self.dummy_action_lp[n3][c3][n4][c4]\
                                    or 'raise' in self.dummy_action_lp[n3][c3][n4][c4]:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * v
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                                value_from_call += prob2 * v 
                                call_prob += prob2 
                            else:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round((to_call+1), 2)
                                value_from_fold += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                fold_prob += prob2
                            v = self.simulate_value_flop(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call, rais=0)
                            vdt['call'][n1][c1][n2][c2] += prob2 * v 
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'call \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except Exception as e:
                            continue
                    try:
                        value_from_fold /= (fold_prob+call_prob)
                        value_from_call /= (call_prob+fold_prob)
                        fold_prob, call_prob = fold_prob / (fold_prob+call_prob),\
                                call_prob / (fold_prob+call_prob)
                        vdt['raise'][n1][c1][n2][c2] /= prob_accumulation
                        vdt['call'][n1][c1][n2][c2] /= prob_accumulation
                        if self.source != 'ps' and actor != 0:
                            print n1, c1, n2, c2, '\t', round(self.wctaa50[n1][c1][n2][c2], 2), '\t',\
                                    round(fold_prob, 2), round(call_prob, 2), '\t',\
                                    round(vdt['raise'][n1][c1][n2][c2], 2), '\t',\
                                    round(vdt['call'][n1][c1][n2][c2], 2), '\t',\
                                    round(value_from_fold, 2), round(value_from_call, 2)
                    except Exception as e:
                        print e
                        print n1, c1, n2, c2
                        if self.source != 'ps':
                            raw_input()
                return vdt#}}}
#}}}

    def get_value_dummy_table_turn(self, actor, action):# Suppose there are only two players left.
        bet = 0.8#{{{
        vdt = tree()
        the_color = color_make_different(self.game_driver.cards)
        mn1, mc1 = min(self.game_driver.cards[:2])
        mn2, mc2 = max(self.game_driver.cards[:2])
        if mc1 not in the_color:
            mc1 = 0
        if mc2 not in the_color:
            mc2 = 0
        if self.game_driver.last_mover == actor:
            if max(self.betting) == self.betting[actor]:#{{{
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['bet'][n1][c1][n2][c2] = 0
                    vdt['check'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        if 'fold' in self.dummy_action_ep[n3][c3][n4][c4]:
                            numerator = 1
                            denominator = 1
                        else:
                            numerator = 0
                            denominator = 0
                        if 'call bet' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        if 'raise' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            fold_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_ep[n3][c3][n4][c4]
                            raise Exception
                        if 'bet' in self.dummy_action_ep[n3][c3][n4][c4]:
                            numerator = self.dummy_action_ep[n3][c3][n4][c4]['bet']
                            denominator = self.dummy_action_ep[n3][c3][n4][c4]['bet']
                        else:
                            numerator = 0
                            denominator = 0
                        if 'check' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            bet_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_ep[n3][c3][n4][c4]
                            raise Exception
                        try:
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, rais=0)
                            vdt['bet'][n1][c1][n2][c2] += prob2 * (0.8*fold_chance\
                                    + 0.2*fold_chance*min([v, 1])\
                                    + (1 - fold_chance) * v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'bet  \t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(fold_chance, 2), round(v, 2),\
                                        round(fold_chance + (1 - fold_chance)*v, 2)
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, bet=0, rais=0)
                            if v < 0:
                                v = 0
                            vdt['check'][n1][c1][n2][c2] += prob2 * v
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'check\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except:
                            continue
                    vdt['bet'][n1][c1][n2][c2] /= prob_accumulation
                    vdt['check'][n1][c1][n2][c2] /= prob_accumulation
                    if self.source != 'ps' and actor != 0:
                        print n1, c1, n2, c2, '\t',\
                                round(vdt['bet'][n1][c1][n2][c2], 2), '\t',\
                                round(vdt['check'][n1][c1][n2][c2], 2)
                    vdt['check'][n1][c1][n2][c2] = max(0.4, vdt['check'][n1][c1][n2][c2])
                try:
                    del vdt['check1']
                    del vdt['check2']
                except:
                    pass
                return vdt#}}}
            else:#{{{
                to_call = max(self.betting) - self.betting[actor]
                to_call /= (self.game_driver.pot - action - sum(self.betting))
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['call'][n1][c1][n2][c2] = 0
                    vdt['raise'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    value_from_fold = 0
                    value_from_call = 0
                    fold_prob = 0
                    call_prob = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        try:
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call)
                            if 'call raise' in self.dummy_action_ep[n3][c3][n4][c4]\
                                    or 'raise' in self.dummy_action_ep[n3][c3][n4][c4]:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * v
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                                value_from_call += prob2 * v 
                                call_prob += prob2 
                            else:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round((to_call+1), 2)
                                value_from_fold += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                fold_prob += prob2
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call, rais=0)
                            vdt['call'][n1][c1][n2][c2] += prob2 * v
                            if actor == 0 and self.source != 'ps'\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'call \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except Exception as e:
                            continue
                    try:
                        value_from_fold /= (fold_prob+call_prob)
                        value_from_call /= (fold_prob+call_prob)
                        fold_prob, call_prob = fold_prob / (fold_prob+call_prob),\
                                call_prob / (fold_prob+call_prob)
                        vdt['raise'][n1][c1][n2][c2] /= prob_accumulation
                        vdt['call'][n1][c1][n2][c2] /= prob_accumulation
                        if self.source != 'ps' and actor != 0:
                            print n1, c1, n2, c2, '\t', round(self.wctaa50[n1][c1][n2][c2], 2), '\t',\
                                    round(fold_prob, 2), round(call_prob, 2), '\t',\
                                    round(vdt['raise'][n1][c1][n2][c2], 2), '\t',\
                                    round(vdt['call'][n1][c1][n2][c2], 2), '\t',\
                                    round(value_from_fold, 2), round(value_from_call, 2)
                    except Exception as e:
                        print e
                        print n1, c1, n2, c2
                        if self.source != 'ps':
                            raw_input()
                return vdt#}}}
        else:
            if max(self.betting) == self.betting[actor]:#{{{
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['check1'][n1][c1][n2][c2] = 0
                    vdt['check2'][n1][c1][n2][c2] = 0
                    vdt['bet'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        if 'fold' in self.dummy_action_lp[n3][c3][n4][c4]:
                            numerator = 1
                            denominator = 1
                        else:
                            numerator = 0
                            denominator = 0
                        if 'call bet' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        if 'raise' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            fold_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_lp[n3][c3][n4][c4]
                            raise Exception
                        if 'bet' in self.dummy_action_lp[n3][c3][n4][c4]:
                            numerator = self.dummy_action_lp[n3][c3][n4][c4]['bet'] 
                            denominator = self.dummy_action_lp[n3][c3][n4][c4]['bet']
                        else:
                            numerator = 0
                            denominator = 0
                        if 'check' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            bet_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_lp[n3][c3][n4][c4]
                            raise Exception
                        try:
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, rais=0)
                            vdt['bet'][n1][c1][n2][c2] += prob2 * (0.7*fold_chance\
                                    + 0.3*fold_chance*min([1, v])\
                                    + (1 - fold_chance) * v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'bet       \t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(fold_chance, 2), round(v, 2),\
                                        round(fold_chance + (1-fold_chance)*v, 2)
                            v2 = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, bet=0, rais=0)
                            if v2 < 0:
                                v2 = 0
                            vdt['check1'][n1][c1][n2][c2] += prob2 * ((1-bet_chance) * v2)
                            vdt['check2'][n1][c1][n2][c2] += prob2 * ((1-bet_chance)*v2 + bet_chance*v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'check fold\t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(bet_chance, 2), round(v2, 2),\
                                        round((1-bet_chance) * v2, 2)
                                print 'check call\t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(bet_chance, 2), round(v2, 2),\
                                        round((1-bet_chance)*v2 + bet_chance*v, 2)
                            prob_accumulation += prob2
                        except:
                            continue
                    vdt['bet'][n1][c1][n2][c2] /= prob_accumulation
                    vdt['check'][n1][c1][n2][c2] = max(vdt['check1'][n1][c1][n2][c2],\
                            vdt['check2'][n1][c1][n2][c2]) / prob_accumulation
                    if self.source != 'ps' and actor != 0:
                        print n1, c1, n2, c2, '\t',\
                                round(vdt['bet'][n1][c1][n2][c2], 2), '\t',\
                                round(vdt['check'][n1][c1][n2][c2], 2)
                    vdt['check'][n1][c1][n2][c2] = max(0.4, vdt['check'][n1][c1][n2][c2])
                try:
                    del vdt['check1']
                    del vdt['check2']
                except:
                    pass
                return vdt#}}}
            else:#{{{
                to_call = max(self.betting) - self.betting[actor]
                to_call /= (self.game_driver.pot - action - sum(self.betting))
                rais = 1 + to_call
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['call'][n1][c1][n2][c2] = 0
                    vdt['raise'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    value_from_fold = 0
                    value_from_call = 0
                    fold_prob = 0
                    call_prob = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        try:
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call)
                            if 'call raise' in self.dummy_action_lp[n3][c3][n4][c4]\
                                    or 'raise' in self.dummy_action_lp[n3][c3][n4][c4]:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * v
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                                value_from_call += prob2 * v 
                                call_prob += prob2 
                            else:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round((to_call+1), 2)
                                value_from_fold += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                fold_prob += prob2
                            v = self.simulate_value_turn(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call, rais=0)
                            vdt['call'][n1][c1][n2][c2] += prob2 * v 
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'call \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except Exception as e:
                            continue
                    try:
                        value_from_fold /= (fold_prob+call_prob)
                        value_from_call /= (call_prob+fold_prob)
                        fold_prob, call_prob = fold_prob / (fold_prob+call_prob),\
                                call_prob / (fold_prob+call_prob)
                        vdt['raise'][n1][c1][n2][c2] /= prob_accumulation
                        vdt['call'][n1][c1][n2][c2] /= prob_accumulation
                        if self.source != 'ps' and actor != 0:
                            print n1, c1, n2, c2, '\t', round(self.wctaa50[n1][c1][n2][c2], 2), '\t',\
                                    round(fold_prob, 2), round(call_prob, 2), '\t',\
                                    round(vdt['raise'][n1][c1][n2][c2], 2), '\t',\
                                    round(vdt['call'][n1][c1][n2][c2], 2), '\t',\
                                    round(value_from_fold, 2), round(value_from_call, 2)
                    except Exception as e:
                        print e
                        print n1, c1, n2, c2
                        if self.source != 'ps':
                            raw_input()
                return vdt#}}}
#}}}

    def get_value_dummy_table_river(self, actor, action):# Suppose there are only two players left.
        bet = 0.8#{{{
        vdt = tree()
        the_color = color_make_different(self.game_driver.cards)
        mn1, mc1 = min(self.game_driver.cards[:2])
        mn2, mc2 = max(self.game_driver.cards[:2])
        if mc1 not in the_color:
            mc1 = 0
        if mc2 not in the_color:
            mc2 = 0
        if self.game_driver.last_mover == actor:
            if max(self.betting) == self.betting[actor]:#{{{
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['bet'][n1][c1][n2][c2] = 0
                    vdt['check'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        if 'fold' in self.dummy_action_ep[n3][c3][n4][c4]:
                            numerator = 1
                            denominator = 1
                        else:
                            numerator = 0
                            denominator = 0
                        if 'call bet' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        if 'raise' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            fold_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_ep[n3][c3][n4][c4]
                            raise Exception
                        if 'bet' in self.dummy_action_ep[n3][c3][n4][c4]:
                            numerator = self.dummy_action_ep[n3][c3][n4][c4]['bet']
                            denominator = self.dummy_action_ep[n3][c3][n4][c4]['bet']
                        else:
                            numerator = 0
                            denominator = 0
                        if 'check' in self.dummy_action_ep[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            bet_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_ep[n3][c3][n4][c4]
                            raise Exception
                        try:
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, rais=0)
                            vdt['bet'][n1][c1][n2][c2] += prob2 * (0.7*fold_chance\
                                    + 0.3*fold_chance*min([1, v])\
                                    + (1 - fold_chance) * v) 
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'bet  \t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(fold_chance, 2), round(v, 2),\
                                        round(fold_chance + (1 - fold_chance)*v, 2)
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, bet=0, rais=0)
                            if v < 0:
                                v = 0
                            vdt['check'][n1][c1][n2][c2] += prob2 * v
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'check \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except:
                            continue
                    vdt['bet'][n1][c1][n2][c2] /= prob_accumulation
                    vdt['check'][n1][c1][n2][c2] /= prob_accumulation
                    if self.source != 'ps' and actor != 0:
                        print n1, c1, n2, c2, '\t',\
                                round(vdt['bet'][n1][c1][n2][c2], 2), '\t',\
                                round(vdt['check'][n1][c1][n2][c2], 2)
                    vdt['check'][n1][c1][n2][c2] = max(0.4, vdt['check'][n1][c1][n2][c2])
                try:
                    del vdt['check1']
                    del vdt['check2']
                except:
                    pass
                return vdt#}}}
            else:#{{{
                to_call = max(self.betting) - self.betting[actor]
                to_call /= (self.game_driver.pot - action - sum(self.betting))
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['call'][n1][c1][n2][c2] = 0
                    vdt['raise'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    value_from_fold = 0
                    value_from_call = 0
                    fold_prob = 0
                    call_prob = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        try:
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call)
                            if 'call raise' in self.dummy_action_ep[n3][c3][n4][c4]\
                                    or 'raise' in self.dummy_action_ep[n3][c3][n4][c4]:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * v
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                                value_from_call += prob2 * v 
                                call_prob += prob2 
                            else:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round((to_call+1), 2)
                                value_from_fold += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                fold_prob += prob2
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call, rais=0)
                            vdt['call'][n1][c1][n2][c2] += prob2 * v
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'call \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except Exception as e:
                            continue
                    try:
                        value_from_fold /= (fold_prob+call_prob)
                        value_from_call /= (fold_prob+call_prob)
                        fold_prob, call_prob = fold_prob / (fold_prob+call_prob),\
                                call_prob / (fold_prob+call_prob)
                        vdt['raise'][n1][c1][n2][c2] /= prob_accumulation
                        vdt['call'][n1][c1][n2][c2] /= prob_accumulation
                        if self.source != 'ps' and actor != 0:
                            print n1, c1, n2, c2, '\t', round(self.wctaa50[n1][c1][n2][c2], 2), '\t',\
                                    round(fold_prob, 2), round(call_prob, 2), '\t',\
                                    round(vdt['raise'][n1][c1][n2][c2], 2), '\t',\
                                    round(vdt['call'][n1][c1][n2][c2], 2), '\t',\
                                    round(value_from_fold, 2), round(value_from_call, 2)
                    except Exception as e:
                        print e
                        print n1, c1, n2, c2
                        if self.source != 'ps':
                            raw_input()
                return vdt#}}}
        else:
            if max(self.betting) == self.betting[actor]:#{{{
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['check1'][n1][c1][n2][c2] = 0
                    vdt['check2'][n1][c1][n2][c2] = 0
                    vdt['bet'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        if 'fold' in self.dummy_action_lp[n3][c3][n4][c4]:
                            numerator = 1
                            denominator = 1
                        else:
                            numerator = 0
                            denominator = 0
                        if 'call bet' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        if 'raise' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            fold_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_lp[n3][c3][n4][c4]
                            raise Exception
                        if 'bet' in self.dummy_action_lp[n3][c3][n4][c4]:
                            numerator = self.dummy_action_lp[n3][c3][n4][c4]['bet'] 
                            denominator = self.dummy_action_lp[n3][c3][n4][c4]['bet']
                        else:
                            numerator = 0
                            denominator = 0
                        if 'check' in self.dummy_action_lp[n3][c3][n4][c4]:
                            denominator += 1
                        try:
                            bet_chance = 1.0 * numerator / denominator
                        except:
                            print numerator, denominator
                            print self.dummy_action_lp[n3][c3][n4][c4]
                            raise Exception
                        try:
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, rais=0)
                            vdt['bet'][n1][c1][n2][c2] += prob2 * (fold_chance*0.8\
                                    + fold_chance*0.2*min([1,v])\
                                    + (1 - fold_chance) * v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'bet       \t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(fold_chance, 2), round(v, 2),\
                                        round(fold_chance + (1-fold_chance)*v, 2)
                            v2 = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, bet=0, rais=0)
                            if v2 < 0:
                                v2 = 0
                            vdt['check1'][n1][c1][n2][c2] += prob2 * ((1-bet_chance) * v2)
                            vdt['check2'][n1][c1][n2][c2] += prob2 * ((1-bet_chance)*v2 + bet_chance*v)
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'check fold\t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(bet_chance, 2), round(v2, 2),\
                                        round((1-bet_chance) * v2, 2)
                                print 'check call\t', round(prob2, 2), '\t',\
                                        n3, c3, n4, c4, '\t',\
                                        round(bet_chance, 2), round(v2, 2),\
                                        round((1-bet_chance)*v2 + bet_chance*v, 2)
                            prob_accumulation += prob2
                        except:
                            continue
                    vdt['bet'][n1][c1][n2][c2] /= prob_accumulation
                    vdt['check'][n1][c1][n2][c2] = max(vdt['check1'][n1][c1][n2][c2],\
                            vdt['check2'][n1][c1][n2][c2]) / prob_accumulation
                    if self.source != 'ps' and actor != 0:
                        print n1, c1, n2, c2, '\t',\
                                round(vdt['bet'][n1][c1][n2][c2], 2), '\t',\
                                round(vdt['check'][n1][c1][n2][c2], 2)
                    vdt['check'][n1][c1][n2][c2] = max(0.4, vdt['check'][n1][c1][n2][c2])
                try:
                    del vdt['check1']
                    del vdt['check2']
                except:
                    pass
                return vdt#}}}
            else:#{{{
                to_call = max(self.betting) - self.betting[actor]
                to_call /= (self.game_driver.pot - action - sum(self.betting))
                rais = 1 + to_call
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                    vdt['call'][n1][c1][n2][c2] = 0
                    vdt['raise'][n1][c1][n2][c2] = 0
                    prob_accumulation = 0
                    value_from_fold = 0
                    value_from_call = 0
                    fold_prob = 0
                    call_prob = 0
                    for n3, c3, n4, c4, prob2 in nodes_of_tree(self.small_stats[self.opponent[actor]], 4):
                        try:
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call)
                            if 'call raise' in self.dummy_action_lp[n3][c3][n4][c4]\
                                    or 'raise' in self.dummy_action_lp[n3][c3][n4][c4]:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * v
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                                value_from_call += prob2 * v 
                                call_prob += prob2 
                            else:
                                vdt['raise'][n1][c1][n2][c2] += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                        and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                    print 'raise\t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round((to_call+1), 2)
                                value_from_fold += prob2 * (min([(to_call+1), (to_call+1)*0.5+v*0.5]))
                                fold_prob += prob2
                            v = self.simulate_value_river(n1,c1,n2,c2,n3,c3,n4,c4, bet=to_call, rais=0)
                            vdt['call'][n1][c1][n2][c2] += prob2 * v 
                            if actor == 0 and self.source != 'ps' and prob2 > 0.1\
                                    and mn1 == n1 and mc1 == c1 and mn2 == n2 and mc2 == c2:
                                print 'call \t', round(prob2, 2), '\t', n3, c3, n4, c4, '\t', round(v, 2)
                            prob_accumulation += prob2
                        except Exception as e:
                            continue
                    try:
                        value_from_fold /= (fold_prob+call_prob)
                        value_from_call /= (call_prob+fold_prob)
                        fold_prob, call_prob = fold_prob / (fold_prob+call_prob),\
                                call_prob / (fold_prob+call_prob)
                        vdt['raise'][n1][c1][n2][c2] /= prob_accumulation
                        vdt['call'][n1][c1][n2][c2] /= prob_accumulation
                        if self.source != 'ps' and actor != 0:
                            print n1, c1, n2, c2, '\t', round(self.wctaa50[n1][c1][n2][c2], 2), '\t',\
                                    round(fold_prob, 2), round(call_prob, 2), '\t',\
                                    round(vdt['raise'][n1][c1][n2][c2], 2), '\t',\
                                    round(vdt['call'][n1][c1][n2][c2], 2), '\t',\
                                    round(value_from_fold, 2), round(value_from_call, 2)
                    except Exception as e:
                        print e
                        print n1, c1, n2, c2
                        if self.source != 'ps':
                            raw_input()
                return vdt#}}}
#}}}

    def simulate_value_flop(self, n1, c1, n2, c2, n3, c3, n4, c4, bet=0.8111, rais=2):#{{{
        if self.flop_fo_cache[n1][c1][n2][c2][0]\
                > self.flop_fo_cache[n3][c3][n4][c4][0]:
            w = self.wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]
            ww = self.wcts[n3][c3][n4][c4][n1][c1][n2][c2][1]
        else:
            w = self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]
            ww = self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][1]
        if type(ww) != float:
            ww = 0
        v = 0
        v -= bet + rais
        v += w/2 * (1-ww) * ((1+2*bet+2*rais) * 7.0/3)
        v -= w/2 * ww * (1+2*bet+2*rais) * 4.0/3
        v -= w/2 * ww * (1+2*bet+2*rais) * 7.0/3 * 4.0/3
        if w/2 * 7.0/3 * 4.0/3 > 2.0/3: 
            v -= (1 - w/2) * (1+2*bet+2*rais) * 2.0/3
            v += (1 - w/2) * w/2 * (1+2*bet+2*rais) * 7.0/3 * 7.0/3
        if self.flop_fo_cache[n1][c1][n2][c2][0]\
                > self.flop_fo_cache[n3][c3][n4][c4][0]:
            if bet != 0 and bet != 0.8111:
                return 1+bet-v
            else:
                return 1 - v
        else:
            return v#}}}
    
    def simulate_value_turn(self, n1, c1, n2, c2, n3, c3, n4, c4, bet=0.8111, rais=2):#{{{
        if self.turn_fo_cache[n1][c1][n2][c2][0]\
                > self.turn_fo_cache[n3][c3][n4][c4][0]:
            w = self.wcts[n3][c3][n4][c4][n1][c1][n2][c2][0]
            ww = self.wcts[n3][c3][n4][c4][n1][c1][n2][c2][1]
        else:
            w = self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]
            ww = self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][1]
        if type(ww) != float:
            ww = 0
        v = 0
        v -= bet + rais
        v += w * ((1+2*bet+2*rais) * 5.0/3)
        if self.turn_fo_cache[n1][c1][n2][c2][0]\
                > self.turn_fo_cache[n3][c3][n4][c4][0]:
            if bet != 0 and bet != 0.8111:
                return 1+bet-v
            else:
                return 1 - v
        else:
            return v#}}}
    
    def simulate_value_river(self, n1, c1, n2, c2, n3, c3, n4, c4, bet=0.8111, rais=2):#{{{
        w = self.wcts[n1][c1][n2][c2][n3][c3][n4][c4][0]
        v = 0
        v -= bet + rais
        v += w*(1+2*bet+2*rais)
        return v#}}}
    
    @staticmethod
    def show_value_dummy_table(vdt):
        for item in vdt:#{{{
            to_print = list()
            for n1, c1, n2, c2, value in nodes_of_tree(vdt[item], 4):
                to_print.append([n1, c1, n2, c2, round(value, 2)])
            to_print = sorted(to_print, key=lambda x:x[4], reverse=True)
            print item
            for tup1, tup2 in zip(to_print[:35], to_print[-35:]):
                print tup1, '\t\t', tup2
            if self.source != 'ps':
                raw_input()
            del_stdout_line(len(to_print)+1)#}}}

    def show_dummy_action(self):
        for n1, c1, n2, c2, actions in nodes_of_tree(self.dummy_action_ep, 4):
            print n1, c1, n2, c2, '\t',
            print '%0.2f %0.2f %0.2f' % (\
                    round(self.wctaa100[n1][c1][n2][c2], 2),\
                    round(self.wctaa50[n1][c1][n2][c2], 2),\
                    round(self.wctaa25[n1][c1][n2][c2], 2)),\
                    '  \t:',
            for action in actions:
                print action, '/',
            print
        raw_input('press any key')
        for n1, c1, n2, c2, actions in nodes_of_tree(self.dummy_action_lp, 4):
            print n1, c1, n2, c2, '\t',
            print '%0.2f %0.2f %0.2f' % (\
                    round(self.wctaa100[n1][c1][n2][c2], 2),\
                    round(self.wctaa50[n1][c1][n2][c2], 2),\
                    round(self.wctaa25[n1][c1][n2][c2], 2)),\
                    '  \t:',
            for action in actions:
                print action, '/',
            print
        raw_input('press any key')

    def show_dummy_fold_chance(self, dummy_action_table):
        f = 0#{{{
        nf = 0
        for n1, c1, n2, c2, actions in nodes_of_tree(dummy_action_table, 4):
            n = 0
            d = 0
            if 'fold' in actions:
                n += 1
                d += 1
            if 'call bet' in actions:
                d += 1
            if 'raise' in actions:
                d += 1
            f += self.small_stats[6][n1][c1][n2][c2] * (1.0*n/d)
            nf += self.small_stats[6][n1][c1][n2][c2]
        print f/nf
        if self.source != 'ps':
            raw_input()
        del_stdout_line(2)#}}}

    def make_decision(self):#{{{
       if self.game_driver.stage == 1:
           self.flop_strategy()
       if self.game_driver.stage == 2:
           self.turn_strategy()
       if self.game_driver.stage == 3:
           self.river_strategy()#}}}

    def flop_strategy(self):#{{{
        vdt = self.get_value_dummy_table_flop(0, 0)
        self.vdt = vdt
        n1, c1 = min(self.game_driver.cards[0], self.game_driver.cards[1])
        n2, c2 = max(self.game_driver.cards[0], self.game_driver.cards[1])
        the_color = color_make_different(self.game_driver.cards)
        if not c1 in the_color:
            c1 = 0
        if not c2 in the_color:
            c2 = 0
        value = 0.3
        best_action = 'fold'
        for action in vdt:
            if vdt[action][n1][c1][n2][c2] * pow(0.75, action == 'call') > value:
                value = vdt[action][n1][c1][n2][c2] * pow(0.75, action == 'call')
                best_action = action
            if best_action == 'fold' and action == 'check':
                best_action = 'check'
        change_terminal_color('red')
        if self.source == 'ps':
            if best_action == 'fold':
                self.controller.fold()
            if best_action == 'check':
                self.controller.call()
            if best_action == 'call':
                self.controller.call()
            if best_action == 'bet':
                self.controller.rais(0.75*self.game_driver.pot)
            if best_action == 'raise':
                self.controller.rais(0.65*(sum(self.game_driver.betting)+self.game_driver.pot)+0.55*max(self.game_driver.betting))
        print 'My Decision:', best_action
        print 'Value:', value
        change_terminal_color()#}}}

    def turn_strategy(self):#{{{
        vdt = self.get_value_dummy_table_turn(0, 0)
        self.vdt = vdt
        n1, c1 = min(self.game_driver.cards[0], self.game_driver.cards[1])
        n2, c2 = max(self.game_driver.cards[0], self.game_driver.cards[1])
        the_color = color_make_different(self.game_driver.cards)
        if not c1 in the_color:
            c1 = 0
        if not c2 in the_color:
            c2 = 0
        value = 0.4
        best_action = 'fold'
        for action in vdt:
            if vdt[action][n1][c1][n2][c2] * pow(0.75, action == 'call') > value:
                value = vdt[action][n1][c1][n2][c2] * pow(0.75, action == 'call')
                best_action = action
            if best_action == 'fold' and action == 'check':
                best_action = 'check'
        change_terminal_color('red')
        if self.source == 'ps':
            if best_action == 'fold':
                self.controller.fold()
            if best_action == 'check':
                self.controller.call()
            if best_action == 'call':
                self.controller.call()
            if best_action == 'bet':
                self.controller.rais(0.75*self.game_driver.pot)
            if best_action == 'raise':
                self.controller.rais(0.65*(sum(self.game_driver.betting)+self.game_driver.pot)+0.55*max(self.game_driver.betting))
        print 'My Decision:', best_action
        print 'Value:', value
        change_terminal_color()#}}}

    def river_strategy(self):#{{{
        vdt = self.get_value_dummy_table_river(0, 0)
        self.vdt = vdt
        n1, c1 = min(self.game_driver.cards[0], self.game_driver.cards[1])
        n2, c2 = max(self.game_driver.cards[0], self.game_driver.cards[1])
        the_color = color_make_different(self.game_driver.cards)
        if not c1 in the_color:
            c1 = 0
        if not c2 in the_color:
            c2 = 0
        value = 0.2
        best_action = 'fold'
        for action in vdt:
            if vdt[action][n1][c1][n2][c2] * pow(0.75, action == 'call') > value:
                value = vdt[action][n1][c1][n2][c2] * pow(0.75, action == 'call')
                best_action = action
            if best_action == 'fold' and action == 'check':
                best_action = 'check'
        change_terminal_color('red')
        if self.source == 'ps':
            if best_action == 'fold':
                self.controller.fold()
            if best_action == 'check':
                self.controller.call()
            if best_action == 'call':
                self.controller.call()
            if best_action == 'bet':
                self.controller.rais(0.75*self.game_driver.pot)
            if best_action == 'raise':
                self.controller.rais(0.65*(sum(self.game_driver.betting)+self.game_driver.pot)+0.55*max(self.game_driver.betting))
        print 'My Decision:', best_action
        print 'Value:', value
        change_terminal_color()#}}}

    def fast_fold(self):
        pass

    def update_betting(self):
        for i in xrange(6):
            self.betting[i] = self.game_driver.betting[i]

