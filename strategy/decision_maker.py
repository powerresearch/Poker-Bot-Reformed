import json
import time
from pokerstars.config import BB
from pokerstars.controller import Controller
from strategy.config import preflop_move
from strategy.config import prob_factor
from pokerstars.controller import Controller


class DecisionMaker():
    def __init__(self, game_driver):
        self.data_manager = game_driver.data_manager#{{{
        self.controller = Controller()
        self.stats_handler = game_driver.stats_handler#}}}

    def get_preflop_move(self):
        cards = self.cards#{{{
        big_card = max(cards[0][0], cards[1][0])
        small_card = min(cards[0][0], cards[1][0])
        if cards[0][1] == cards[1][1]:
            suited = 1
        else:
            suited = 0
        if suited:
            my_move = preflop_move[small_card][big_card]
        else:
            my_move = preflop_move[big_card][small_card]
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
        self.update(game_driver)
        if game_driver.stage == 0:
            self.preflop_strategy()

    def preflop_strategy(self):
        my_move = self.get_preflop_move()
        betting = self.betting
        people_bet = self.bet_round
        button = self.button 
        people_play = self.people_play
        dm = self.data_manager
        if my_move == 0 or my_move == 1:
            if (button == 0 or button == 1) and people_bet == 1 and people_play == 1:#{{{
                fold_chance = 1.0
                fold_chance *= dm.get_item((button+1)%6, u'SFBS')
                fold_chance *= dm.get_item((button+2)%6, u'BFBS') 
                if fold_chance > 0.7:
                    print 'Fold To Button Steal: '+str(fold_chance)
                    self.controller.rais(3*BB)
                    return
            if button == 5 and people_bet == 1 and people_play == 1:
                fold_chance = 1.0
                fold_chance *= dm.get_item((button+2)%6, u'BFBS')
                if fold_chance > 0.7:
                    print 'Fold To Button Steal: '+str(fold_chance)
                    self.controller.rais(3*BB)
                    return 
            if people_bet == 2 and people_play == 1 and button >= 4:
                for i in xrange(1, 6):
                    if betting[i] == max(betting):
                        better = i
                if better == button:
                    if dm.get_item(better, u'BSA') > 0.7:
                        print 'BSA: ', dm.get_item(better, u'BSA')
                        self.controller.rais(3*max(betting))
                        return
            if people_bet == 2:
                fold_chance = 1.0
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        fold_chance *= dm.get_item(i, u'F3B')
                if fold_chance > 0.7:
                    print 'Fold To 3 Bet: '+str(fold_chance)
                    self.controller.rais((people_play*0.8+1.8)*max(betting))
                    return
            if people_bet == 2 and people_play == 1:
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        if dm.get_item(i, 'pfr') > 0.5:
                            self.controller.rais(max(betting)*3)
                            print i, player_data[i]['pfr']
                            return
            if people_bet == 3:
                fold_chance = 1.0
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        print i, dm.get_item(i, u'F4B') 
                        fold_chance *= dm.get_item(i, u'F4B') 
                if fold_chance > 0.7:
                    print 'Fold To 4 Bet: '+str(fold_chance)
                    self.controller.rais((people_play*0.8+1.8)*max(betting))
                    return 
            if people_bet == 1 and people_play == 1 and button == 1:
                fold_chance = 1.0
                fold_chance *= (1-dm.get_item(1, 'vpip'))
                fold_chance *= (1-dm.get_item(2, 'vpip'))
                fold_chance *= (1-dm.get_item(3, 'vpip'))
                if fold_chance > 0.8:
                    print 'Low VPIP, Steal'
                    self.controller.rais(BB*3)
                    return
            if people_bet == 1 and people_play == 1 and button == 0:
                fold_chance = 1.0
                fold_chance *= (1-dm.get_item(1, 'vpip'))
                fold_chance *= (1-dm.get_item(2, 'vpip'))
                if fold_chance > 0.8:
                    print 'Low VPIP, Steal'
                    self.controller.rais(BB*3)
                    return
            if people_bet == 1 and people_play == 1 and button == 5:
                fold_chance = 1.0
                fold_chance *= (1-dm.get_item(1, 'vpip'))
                if fold_chance > 0.9:
                    print 'Low VPIP, Steal'
                    self.controller.rais(BB*3)
                    return
                
            if people_bet == 1 and my_move == 1:
                self.controller.rais(BB*(2+people_play))
                return

            if betting[0] == max(betting):
                self.controller.fold()
                return
            else:
                self.controller.fold()
                return#}}}
        if my_move == 2:
            if people_bet == 1:#{{{
                self.controller.rais(BB*(people_play+2))
                print 'My Move Is 2'
                return
            if people_bet == 2: 
                fold_chance = 1.0
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        fold_chance *= dm.get_item(i, u'F3B')
                        print i, 'F3B', dm.get_item(i, u'F3B') 
                if fold_chance > 0.7:
                    print 'Fold To 3 Bet: '+str(fold_chance)
                    self.controller.rais((people_play*0.8+1.8)*max(betting))
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
                        if dm.get_item(i, 'pfr') > 0.5:
                            self.controller.rais(max(betting)*3)
                            print i, 'pfr', dm.get_item(i, 'pfr') 
                            return 
            if people_bet == 3:
                fold_chance = 1.0
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        fold_chance *= dm.get_item(i, u'F4B') 
                        print i, 'F4B', dm.get_item(i, u'F4B') 
                if fold_chance > 0.7:
                    print 'Fold To 4 Bet: '+str(fold_chance)
                    self.controller.rais((people_play*0.8+1.8)*max(betting))
                    return 
            if people_bet == 2:
                self.controller.call()
                return 
            if betting[0] == max(betting):
                self.controller.fold()
                return
            else:
                self.controller.fold()
                return#}}}
        if my_move == 3:
            if people_bet == 1:#{{{
                self.controller.rais((people_play+2)*BB)
                print 'My Move Is 3'
                return
            if people_bet == 2:
                self.controller.rais(max(betting)*(1.8+people_play*0.8))
                print 'My Move Is 3'
                return
            if people_bet == 2:
                fold_chance = 1.0
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        fold_chance *= dm.get_item(i, u'F3B') 
                        print i, 'F3B', dm.get_item(i, u'F3B')
                if fold_chance > 0.7:
                    print 'Fold To 3 Bet: '+str(fold_chance)
                    self.controller.rais((people_play*0.8+1.8)*max(betting))
                    return
            if people_bet == 3:
                fold_chance = 1.0
                for i in xrange(1,6):
                    if betting[i] == max(betting):
                        fold_chance *= dm.get_item(i, u'F4B')
                        print i, 'F4B', dm.get_item(i, u'F4B')
                if fold_chance > 0.8:
                    print 'Fold To 4 Bet: '+str(fold_chance)
                    self.controller.rais((people_play*0.8+1.8)*max(betting))
                    return 
            if people_bet == 2:
                self.controller.call()
                return
            self.controller.fold()
            return#}}}
        if my_move == 4:
            self.controller.rais(max(betting)*(people_play+2))#{{{
            print 'My Move Is 4'
            return#}}}
