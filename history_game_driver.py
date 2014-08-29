#coding: utf-8

import json
import re
import time
from public import is_only_max
from public import get_power_rank
from public import get_can_beat_table
from pokerstars.config import BB, SB
from pokerstars.screen_scraper import ScreenScraper
from pokerstars.move_catcher import MoveCatcher
from pokerstars.controller import Controller
from database.data_manager import DataManager
from stats.stats_handler import StatsHandler
from strategy.decision_maker import DecisionMaker

class GameDriver():

    def __init__(self):
        self.screen_scraper = ScreenScraper(source='file')#{{{
        init_values = self.screen_scraper.get_init_values()
        self.stack          = init_values['stack'] 
        self.game_number    = init_values['game_number']
        self.cards          = init_values['cards'] + ['', '', '', '', '']
        self.button         = init_values['button']
        self.player_name    = init_values['player_name']
        self.steal_position = self.button == 0 or self.button == 1
        self.active         = [1, 1, 1, 1, 1, 1]
        self.data_manager   = DataManager()
        self.data_manager.load_data(self.player_name, self.button)
        self.stats_handler  = StatsHandler(self)
        self.decision_maker = DecisionMaker(self)
        self.pot            = 0
        self.last_better    = -1
        self.all_limper     = -1
        self.stage          = 0
        self.bet_round      = 1
        self.people_play    = 1
        self.postflop_status = ['', '', '', '', '', '']
        self.power_rank     = [0, 0, 0, 0]
        self.can_beat_table = [0, 0, 0, 0]
        self.outs           = [0, 0, 0, 0]#}}}

    @classmethod
    def count_game(cls):
        try:#{{{
            cls.game_count += 1
        except:
            cls.game_count = 1#}}}

    def game_stream(self):
        print 'Stack:', self.stack#{{{
        print 'Game Number:', self.game_number
        print 'Button:', self.button
        print 'Cards:', self.cards
        print 'Names:', self.player_name
        print
        print#}}}
        indicator = self.preflop()#{{{
        self.stage = 1 
        if indicator == 'new game':
            return self.game_number
        for self.stage in xrange(1, 4):
            with open('stats_snapshot.json', 'w') as f:
                json.dump(self.stats_handler.stats, f)
            print 'Cards: ', self.cards
            indicator = self.post_flop(self.stage)
            if indicator == 'new game':
                return self.game_number#}}}
    
    def handle_preflop_action(self, action):
        if action[0] == 'new game':#{{{
            print 'new game'
            self.game_number = action[1]
            return 'new game'
        if action[0] == 'new stage':
            print 'new stage'
            self.cards = action[1]
            return 'new stage'
        if action[0] == 'my move':
            print 'making decision'
            self.decision_maker.make_decision(self)
#           time.sleep(1)
            return []
        actor, value = action
        if value == 'fold':
            print actor, 'fold'
            self.active[actor] = 0
            return []
        if value == 'check':
            print actor, 'check'
            return []
        print actor, value
        self.stats_handler.preflop_update(action, self.betting, self.bet_round,\
                self.people_play, self.last_better)
        self.pot += value
        self.pot = round(self.pot, 2)
        self.stack[actor] -= value
        self.stack[actor] = round(self.stack[actor], 2)
        if self.stack[actor] == 0:
            self.active[actor] = 0.5
        if is_only_max(self.betting, actor):
            self.last_better = actor
            self.bet_round += 1
        else:
            self.people_play += 1
        return []#}}}

    def handle_postflop_action(self, action):
        if action[0] == 'new game':#{{{
            print 'new game'
            self.game_number = action[1]
            return 'new game'
        if action[0] == 'new stage':
            print 'new stage'
            self.cards = action[1]
            return 'new stage'
        if action[0] == 'my move':
            self.decision_maker.make_decision(self)
            return []
        actor, value = action
        print actor, value
        if value == 'fold':
            print actor, 'fold'
            self.active[actor] = 0
            return []
        if value == 'check':
            print actor, 'check'
            self.postflop_status[actor] = 'check'
            value = 0
        else:
            self.stack[actor] -= value
            self.stack[actor] = round(self.stack[actor], 2)
            if self.stack[actor] == 0:
                self.active[actor] = 0.5
            if round(value+self.betting[actor], 2) > max(self.betting):
                if self.pot == 0: 
                    if self.last_better == actor:
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
        return []#}}}

    def preflop(self):
        to_act = (self.button+3) % 6#{{{
        self.betting = [0, 0, 0, 0, 0, 0]
        self.betting[(self.button+1)%6] = SB
        self.betting[(self.button+2)%6] = BB
        self.people_play = 1
        self.last_mover = (self.button+2) % 6
        move_catcher = MoveCatcher(to_act, self.betting, self.active,\
                self.stack, self.cards, self.game_number, source='file')#}}}
        while True:#{{{
            actions = move_catcher.get_action()
            for action in actions:
                print action
                print self.betting
                indicator = self.handle_preflop_action(action)
                if indicator:
                    return indicator
            to_act = move_catcher.to_act#}}}
            
    def post_flop(self, stage):
        self.postflop_status = ['', '', '', '', '', '']#{{{
        self.stats_handler.postflop_big_update()
        self.power_rank[stage] = get_power_rank(self.cards[2:stage+4])
        to_act = (self.button+1) % 6
        self.betting = [0, 0, 0, 0, 0, 0]
        self.last_mover = self.button
        while self.last_mover != 1:
            self.last_mover = (self.last_mover-1) % 6
        move_catcher = MoveCatcher(to_act, self.betting, self.active,\
                self.stack, self.cards, self.game_number, source='file')#}}}
        while True:#{{{
            actions = move_catcher.get_action()
            for action in actions:
                self.can_beat_table[stage] ,self.outs[stage] =\
                        get_can_beat_table(self.power_rank[self.stage],\
                        self.stats_handler.stats, self.last_better)
                print action
                print self.betting
                indicator = self.handle_postflop_action(action)
                if indicator:
                    return indicator
            to_act = move_catcher.to_act#}}}
