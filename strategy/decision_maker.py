import json
import time
from pokerstars.config import BB
from pokerstars.controller import Controller
from strategy.config import preflop_move_ep
from strategy.config import preflop_move_lp
from pokerstars.controller import Controller
from public import * 

class DecisionMaker():
    def __init__(self, game_driver):
        self.data_manager = game_driver.data_manager#{{{
        self.controller = Controller(game_driver)
        self.game_driver = game_driver
        self.button = game_driver.button
        self.stats_handler = game_driver.stats_handler#}}}

    def get_preflop_move(self, cards):
        big_card = max([cards[0][0], cards[1][0]])#{{{
        small_card = min([cards[0][0], cards[1][0]])
        if cards[0][1] == cards[1][1]:
            suited = 1
        else:
            suited = 0
        if self.button == 0 or self.button == 1:
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
            self.preflop_strategy()
        else:
            self.postflop_strategy()#}}}

    def postflop_strategy(self):
        gd = self.game_driver
        stats = self.stats_handler.stats
        if self.game_driver.source == 'ps':#{{{
            beat_chance = 1
            for i in xrange(1, 6):
                if gd.active[i]:
                    beat_chance = min([how_much_can_beat(stats, gd.cards[:2], gd.cards[2:], i), beat_chance])
            my_outs = how_many_outs(gd.cards[2:], gd.cards[:2])
            print
            print 'Pot: ', self.game_driver.pot
            print 'My Combo: ', find_out(self.game_driver.cards[:self.game_driver.stage+4])
            print 'My Win Chance: ', beat_chance
            print 'My Outs', my_outs
            if max(self.betting) < self.pot * 0.3:
                if beat_chance > 0.6\
                        - move_last(self.game_driver.active, self.game_driver.button)*0.1\
                        + self.game_driver.stage*0.1:
                    self.controller.rais(self.pot*0.6+max(self.betting))
                else:
                    self.controller.call()#check
            else:
                to_call = max(self.betting) - self.betting[0]
                ratio = to_call / (self.pot+to_call)
                if beat_chance > 0.85:
                    self.controller.rais(self.pot*0.6+max(self.betting))
                elif beat_chance+my_outs*0.02*(3-self.stage) > 2*ratio\
                        or beat_chance > 0.6\
                        or my_outs*0.02*(3-self.stage) > 1.5*ratio:
                    self.controller.call()
                else:
                    self.controller.fold()#}}}
        else:#{{{
            beat_chance = 1
            for i in xrange(1, 6):
                if gd.active[i]:
                    beat_chance *= how_much_can_beat(stats, gd.cards[:2], gd.cards[2:], i)
            my_outs = how_many_outs(gd.cards[2:], gd.cards[:2])
            print
            print 'Pot: ', self.game_driver.pot
            print 'My Combo: ', find_out(self.game_driver.cards[:self.game_driver.stage+4])
            print 'My Win Chance: ', beat_chance
            print 'My Outs', my_outs
            print 'My Decision: ', 
            if max(self.betting) == 0:
                if beat_chance > 0.6\
                        - move_last(self.game_driver.active, self.game_driver.button)*0.1\
                        + self.game_driver.stage*0.1:
                    print 'Bet', round(self.pot*0.8, 2)
                else:
                    print 'Check'
            else:
                to_call = max(self.betting) - self.betting[0]
                ratio = to_call / (self.pot+to_call)
                print 'Ratio: ', ratio,
                if beat_chance > 0.85:
                    print 'Raise', round(self.pot*0.6+max(self.betting), 2)
                elif beat_chance+my_outs*0.02*(3-self.stage) > 2*ratio\
                        or beat_chance > 0.6\
                        or my_outs*0.02*(3-self.stage) > 1.5*ratio:
                    print 'Call'
                else:
                    print 'Fold'
            if self.game_driver.source != 'ps':
                raw_input('---press any key---')
                del_stdout_line(1)
            #}}}

    def preflop_strategy(self):
        my_move = self.get_preflop_move(self.cards)#{{{
        betting = self.betting
        people_bet = self.bet_round
        button = self.button 
        people_play = self.people_play
        dm = self.data_manager
        if self.game_driver.source == 'ps':
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
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
                        return
                if people_bet == 2 and people_play == 1:
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            if dm.get_item(i, 'pfr') > 0.5:
                                self.controller.rais(max(betting)*3)
                                print i, dm.get_item(i, 'pfr') 
                                return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            print i, dm.get_item(i, u'F4B') 
                            fold_chance *= dm.get_item(i, u'F4B') 
                    if fold_chance > 0.7:
                        print 'Fold To 4 Bet: '+str(fold_chance)
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
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
                    self.controller.call()
                    return
                if people_bet == 2 and my_move == 1 and max(betting)-betting[0] <= 0.08:
                    self.controller.call()
                    return
                if people_bet == 1 and button == 4:
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
                            print i, 'F3B', dm.get_item(i, u'F3B') 
                    if fold_chance > 0.7:
                        print 'Fold To 3 Bet: '+str(fold_chance)
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
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
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
                    return
                if people_bet == 2:
                    self.controller.rais(max(betting)*(1.8+people_play*0.8)+2*BB)
                    return
                if people_bet == 2:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B') 
                            print i, 'F3B', dm.get_item(i, u'F3B')
                    if fold_chance > 0.7:
                        print 'Fold To 3 Bet: '+str(fold_chance)
                        self.controller.rais((people_play*0.8+1.8)*max(betting)+2*BB)
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
                if people_bet == 2:
                    self.controller.call()
                    return
                self.controller.fold()
                return#}}}
            if my_move == 4:
                self.controller.rais(max(betting)*(people_play+2))#{{{
                return#}}}
#}}}

    def fast_fold(self, game_driver):
        self.update(game_driver)#{{{
        if game_driver.stage == 0:
            self.fast_fold_preflop()
        else:
            self.fast_fold_postflop()#}}}

    def fast_fold_postflop(self):
        gd = self.game_driver
        stats = self.stats_handler.stats
        if self.game_driver.source == 'ps':#{{{
            beat_chance = 1
            for i in xrange(1, 6):
                if gd.active[i]:
                    beat_chance *= how_much_can_beat(stats, gd.cards[:2], gd.cards[2:], i)
            my_outs = how_many_outs(gd.cards[2:], gd.cards[:2])
            if max(self.betting) == 0:
                pass
            else:
                to_call = max(self.betting) - self.betting[0]
                ratio = to_call / (self.pot+to_call)
                if beat_chance > 0.85:
                    pass
                elif beat_chance+my_outs*0.02*(3-self.stage) > 2*ratio\
                        or beat_chance > 0.6\
                        or my_outs*0.02*(3-self.stage) > 1.5*ratio:
                            pass
                else:
                    self.controller.fold()#}}}
        else:#{{{
            beat_chance = 1
            for i in xrange(1, 6):
                if gd.active[i]:
                    beat_chance *= how_much_can_beat(stats, gd.cards[:2], gd.cards[2:], i)
            my_outs = how_many_outs(gd.cards[2:], gd.cards[:2])
            print
            print 'Pot: ', self.game_driver.pot
            print 'My Combo: ', find_out(self.game_driver.cards[:self.game_driver.stage+4])
            print 'My Win Chance: ', beat_chance
            print 'My Outs', my_outs
            print 'My Decision: ', 
            if max(self.betting) == 0:
                if beat_chance > 0.6\
                        - move_last(self.game_driver.active, self.game_driver.button)*0.1\
                        + self.game_driver.stage*0.1:
                    print 'Bet', round(self.pot*0.8, 2)
                else:
                    print 'Check'
            else:
                to_call = max(self.betting) - self.betting[0]
                ratio = to_call / (self.pot+to_call)
                print 'Ratio: ', ratio,
                if beat_chance > 0.85:
                    print 'Raise', round(self.pot*0.6+max(self.betting), 2)
                elif beat_chance+my_outs*0.02*(3-self.stage) > 2*ratio\
                        or beat_chance > 0.6\
                        or my_outs*0.02*(3-self.stage) > 1.5*ratio:
                    print 'Call'
                else:
                    print 'Fold'
            if self.game_driver.source != 'ps':
                raw_input('---press any key---')
                del_stdout_line(1)
            #}}}

    def fast_fold_preflop(self):
        my_move = self.get_preflop_move(self.cards)#{{{
        betting = self.betting
        people_bet = self.bet_round
        button = self.button 
        people_play = self.people_play
        if betting[0] == max(betting):
            if is_only_max(betting, 0):
                people_bet -= 1
                people_play = 1
            else:
                people_play -= 1
        dm = self.data_manager
        if self.game_driver.source == 'ps':
            if my_move == 0 or my_move == 1:
                if (button == 0 or button == 1) and people_bet == 1 and people_play == 1:#{{{
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+1)%6, u'SFBS')
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS') 
                    if fold_chance > 0.7:
                        return
                if button == 5 and people_bet == 1 and people_play == 1:
                    fold_chance = 1.0
                    fold_chance *= dm.get_item((button+2)%6, u'BFBS')
                    if fold_chance > 0.7:
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
                    self.controller.fold()
                    return
                if people_bet == 2 and my_move == 1 and max(betting)-betting[0] <= 0.08:
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
                    self.controller.fold()
                    return
                else:
                    self.controller.fold()
                    return#}}}
            if my_move == 3:
                if people_bet == 1:#{{{
                    return
                if people_bet == 2:
                    return
                if people_bet == 2:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F3B') 
                    if fold_chance > 0.7:
                        return
                if people_bet == 3:
                    fold_chance = 1.0
                    for i in xrange(1,6):
                        if betting[i] == max(betting):
                            fold_chance *= dm.get_item(i, u'F4B')
                    if fold_chance > 0.8:
                        return 
                if people_bet == 2:
                    return
                self.controller.fold()
                return#}}}
            if my_move == 4:
                return#}}}
#}}}
