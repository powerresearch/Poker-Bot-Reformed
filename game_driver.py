#coding: utf-8

import json
import re
import time
from public import is_only_max
from public import get_power_rank
from public import get_can_beat_table
from public import show_stats
from public import get_board_wetness
from public import show_can_beat_table
from pokerstars.config import BB, SB
from pokerstars.screen_scraper import ScreenScraper
from pokerstars.move_catcher import MoveCatcher
from pokerstars.controller import Controller
from database.data_manager import DataManager
from stats.stats_handler import StatsHandler
from strategy.decision_maker import DecisionMaker

class GameDriver():

    def __init__(self, game_record='ps'):
        self.screen_scraper = ScreenScraper(game_driver=self, source=game_record)#{{{
        self.source         = game_record
        self.controller     = Controller(self)
        init_values = self.screen_scraper.get_init_values()
        while init_values == 'get back':
            self.controller.get_back()
            init_values = self.screen_scraper.get_init_values()
        self.stack          = init_values['stack'] 
        self.game_number    = init_values['game_number']
        self.cards          = init_values['cards'] + ['', '', '', '', '']
        self.button         = init_values['button']
        self.player_name = init_values['player_name']
        if self.source != 'ps':
            self.seat       = init_values['seat']
        self.steal_position = self.button == 0 or self.button == 1
        self.active         = [1, 1, 1, 1, 1, 1]
        self.data_manager   = DataManager(self.button)
        self.data_manager.load_data(self.player_name, self.button)
        self.stats_handler  = StatsHandler(self)
        self.decision_maker = DecisionMaker(self)
        self.betting        = [0, 0, 0, 0, 0, 0]
        self.pot            = SB+BB 
        self.last_better    = -1
        self.all_limper     = -1
        self.stage          = 0
        self.bet_round      = 1
        self.people_play    = 1
        self.move_catcher   = MoveCatcher(0, self)
        self.postflop_status = ['', '', '', '', '', '']
        self.power_rank     = [0, 0, 0, 0]
        self.can_beat_table = [0, 0, 0, 0]
        self.board_wetness  = [0, 0, 0, 0]
        self.fold           = 0
        self.outs           = [0, 0, 0, 0]#}}}

    @classmethod
    def count_game(cls):
        try:#{{{
            cls.game_count += 1 
        except:
            cls.game_count = 1#}}}

    def game_stream(self, last_game):
        if self.game_number == last_game:
            return last_game
        print 'Stack:', self.stack#{{{
        print 'Game Number:', self.game_number
        print 'Button:', self.button
        print 'Cards:', self.cards[:2]
        print 'Names:', self.player_name
        for i in xrange(1, 6):
            if type(self.player_name[i]) == unicode:
                print '%s, Hands: %d, PFR: %0.2f, F3B: %0.2f, BSA: %0.2f' %\
                        (self.player_name[i], self.data_manager.get_item(i, u'HANDS'),\
                        self.data_manager.get_item(i, u'pfr'), self.data_manager.get_item(i, u'F3B'),\
                        self.data_manager.get_item(i, u'BSA'))
        if self.stack[0] > 3 and self.decision_maker.get_preflop_move(self.cards) == 0:
            self.controller.sit_out()
            return self.game_number
        if self.source == 'ps' and self.decision_maker.get_preflop_move(self.cards) == 0 and self.button != 4 and self.button != 0:
            print 'Fold because my preflop move is 0'
            self.controller.fold()
            return self.game_number
        print#}}}
        indicator = self.preflop()#{{{
        stages = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
        self.stage = 1 
        if indicator == 'new game':
            return self.game_number
        for self.stage in xrange(1, 4):
            with open('stats_snapshot.json', 'w') as f:
                json.dump(self.stats_handler.stats, f)
            print '*** '+stages[self.stage]+' ***'
            print 'Pot: ', self.pot
            if self.stage == 1:
                print 'Cards: ', self.cards[2:5]
            elif self.stage == 2:
                print 'Cards: ', self.cards[2:5], self.cards[5]
            elif self.stage == 3:
                print 'Cards: ', self.cards[2:5], self.cards[5], self.cards[6]
            indicator = self.post_flop(self.stage)
            if indicator == 'new game':
                return self.game_number#}}}
    
    def handle_preflop_action(self, action):
        if action[0] == 'new game':#{{{
#           print 'new game'
            return 'new game'
        if action[0] == 'new stage':
#           print 'new stage'
            self.cards = action[1]
            return 'new stage'
        if action[0] == 'my move':
#           print 'making decision'
            self.decision_maker.make_decision(self)
            time.sleep(0.5)
            return []
        actor, value = action
        if value == 'fold':
            print 'Player '+str(actor)+': Fold'+' '*12+'\t <-- '+str(self.betting)
            self.active[actor] = 0
            return []
        if value == 'check':
            print 'Player '+str(actor)+': Check'+' '*11+'\t <-- '+str(self.betting)
            return []
#       self.betting[actor] = round(self.betting[actor]+value, 2)
        if is_only_max(self.betting, actor):
            print 'Player '+str(actor)+': Raise --> '+str(self.betting[actor])+'  \t <-- '+str(self.betting)
        else:
            print 'Player '+str(actor)+': Call'+' '*12+'\t <-- '+str(self.betting)
        if is_only_max(self.betting, actor):
            self.last_better = actor
            self.bet_round += 1
            if self.bet_round == 2:
                if self.betting[actor] / BB > 5 + self.people_play:
                    self.bet_round += 1
            if self.bet_round == 3:
                if self.betting[actor] > 3.5 * self.pot:
                    self.bet_round += 1
            self.people_play = 1
        else:
            self.people_play += 1
        self.stats_handler.preflop_update(action, self.betting, self.bet_round,\
                self.people_play, self.last_better)
#        if self.source != 'ps':
#            show_stats(self.stats_handler.stats, actor)
        self.pot += value
        self.pot = round(self.pot, 2)
        self.stack[actor] -= value
        self.stack[actor] = round(self.stack[actor], 2)
        if self.stack[actor] == 0:
            self.active[actor] = 0.5
        return []#}}}

    def handle_postflop_action(self, action):
        if action[0] == 'new game':#{{{
#           print 'new game'
            return 'new game'
        if action[0] == 'new stage':
#           print 'new stage'
            self.cards = action[1]
            return 'new stage'
        if action[0] == 'my move':
            if self.stage == 3:
                a = self.betting[0]
                not_even = 0
                for i in xrange(6):
                    if self.active[i] == 1 and self.betting[i] != a:
                        not_even = 1
            if self.stage != 3 or not_even or a == 0:
                self.decision_maker.make_decision(self)
                time.sleep(0.5)
            return []
        actor, value = action
        if value == 'fold':
            print 'Player '+str(actor)+': Fold'+' '*12+'\t <-- '+str(self.betting)
            self.active[actor] = 0
            return []
        if value == 'check':
            print 'Player '+str(actor)+': Check'+' '*11+'\t <-- '+str(self.betting)
            self.postflop_status[actor] = 'check'
            value = 0
        else:
#           self.betting[actor] = round(self.betting[actor]+value, 2)
            if is_only_max(self.betting, actor):
                print 'Player '+str(actor)+': Raise --> '+str(self.betting[actor])+'  \t <-- '+str(self.betting)
            else:
                print 'Player '+str(actor)+': Call'+' '*12+'\t <-- '+str(self.betting)
            self.stack[actor] -= value
            self.stack[actor] = round(self.stack[actor], 2)
            if self.stack[actor] == 0:
                self.active[actor] = 0.5
            if is_only_max(self.betting, actor):
                if max(self.betting) == sum(self.betting): 
                    if max(self.betting) < self.pot*0.2 and self.stage != 3:
                        self.postflop_status[actor] = 'check'
                    elif self.last_better == actor:
                        self.postflop_status[actor] = 'cb'
                    else:
                        self.postflop_status[actor] = 'dk'
                else:
                    if self.postflop_status[actor] == 'check':
                        self.postflop_status[actor] = 'cr'
                    else:
                        self.postflop_status[actor] = 'raise'
                self.last_better = actor
                self.bet_round += 1
                self.people_play = 1
            else:
                self.people_play += 1
                if self.postflop_status[actor] == 'check':
                    self.postflop_status[actor] = 'checkcall'+\
                            self.postflop_status[self.last_better]
                else:
                    self.postflop_status[actor] = 'call'+\
                            self.postflop_status[self.last_better]
            self.pot += value
            self.pot = round(self.pot, 2)
        self.stats_handler.postflop_update(actor, self.postflop_status,\
                self.cards, self.stage)
        self.can_beat_table[self.stage], self.outs[self.stage]\
                = get_can_beat_table(self.stage, self.power_rank[self.stage],\
                self.stats_handler.stats, self.last_better, self.active)
        if self.source != 'ps':
            show_can_beat_table(self.can_beat_table[self.stage])
        if self.source != 'ps':
            show_stats(self.stats_handler.stats, actor)
        return []#}}}

    def preflop(self):
        to_act = (self.button+3) % 6#{{{
        self.betting = [0, 0, 0, 0, 0, 0]
        self.betting[(self.button+1)%6] = SB
        self.betting[(self.button+2)%6] = BB
        self.people_play = 1
        self.last_mover = (self.button+2) % 6
        self.move_catcher.to_act = to_act
#       move_catcher = MoveCatcher(to_act, self)#}}}
        while True:
            actions = self.move_catcher.get_action()
            if self.source == 'ps':#{{{
                for action in actions:
                    if action[0] == 'new game':
                        return 'new game' 
                if not actions:
                    if self.button == 0 and\
                            (type(self.player_name[1]) != unicode\
                            or type(self.player_name[2]) != unicode):
                        print 'Wait, Because: ', self.player_name[1:3]
                    elif self.button == 4 and\
                            (self.data_manager.get_item(4, u'BSA') > 0.7):
                        pass
                    else:
                        self.decision_maker.fast_fold(self)
                for action in actions:
                    if action[0] in [1,2,3,4,5] and self.betting[0] < max(self.betting):
                        if self.button == 0 and\
                                (type(self.player_name[1]) != unicode\
                                or type(self.player_name[2]) != unicode):
                            print 'Wait, Because: ', self.player_name[1:3]
                        elif self.button == 4 and\
                                (self.data_manager.get_item(4, u'BSA') > 0.7):
                            pass
                        else:
                            self.decision_maker.fast_fold(self)
                    indicator = self.handle_preflop_action(action)
                    if indicator:
                        return indicator
                to_act = self.move_catcher.to_act#}}}
            else:#{{{
                action = actions[0]
                indicator = self.handle_preflop_action(action)
                if indicator:
                    return indicator
                to_act = self.move_catcher.to_act#}}}
            
    def post_flop(self, stage):
        self.postflop_status = ['', '', '', '', '', '']#{{{
        self.stats_handler.postflop_big_update()
        self.power_rank[stage] = get_power_rank(self.cards[2:stage+4])
        self.board_wetness[stage] = get_board_wetness(self.stats_handler.stats,\
                self.power_rank[stage], self.active, self.cards)[0]
        to_act = (self.button+1) % 6
        self.betting = [0, 0, 0, 0, 0, 0]
        self.last_mover = self.button
        while self.last_mover != 1:
            self.last_mover = (self.last_mover-1) % 6
        self.move_catcher.to_act = to_act
#       move_catcher = MoveCatcher(to_act, self)#}}}
        while True:
            actions = self.move_catcher.get_action()
            if self.source == 'ps':#{{{
                for action in actions:
                    if action[0] == 'new game':
                        return 'new game' 
                for action in actions:
                    if action[0] in [1,2,3,4,5] and self.betting[0] < max(self.betting):
                        self.decision_maker.fast_fold(self)
                    self.can_beat_table[stage] ,self.outs[stage] =\
                            get_can_beat_table(self.stage, self.power_rank[self.stage],\
                            self.stats_handler.stats, self.last_better, self.active)
                    indicator = self.handle_postflop_action(action)
                    if indicator:
                        return indicator
                to_act = self.move_catcher.to_act#}}}
            else:#{{{
                if len(actions) == 1:
                    action = actions[0]
                    self.can_beat_table[stage] ,self.outs[stage] =\
                            get_can_beat_table(self.stage, self.power_rank[self.stage],\
                            self.stats_handler.stats, self.last_better, self.active)
                    indicator = self.handle_postflop_action(action)
                    if indicator:
                        return indicator
                else:
                    self.can_beat_table[stage] ,self.outs[stage] =\
                            get_can_beat_table(self.stage, self.power_rank[self.stage],\
                            self.stats_handler.stats, self.last_better, self.active)
                    action = actions[1]
                    if type(action[1]) == float:
                        self.betting[0] -= action[1]
                        self.betting[0] = round(self.betting[0], 2)
                    action = actions[0]
                    indicator = self.handle_postflop_action(action)
                    action = actions[1]
                    self.handle_preflop_action(action)
                    if type(action[1]) == float:
                        self.betting[0] += action[1]
                        self.betting[0] = round(self.betting[0], 2)
                to_act = self.move_catcher.to_act#}}}
