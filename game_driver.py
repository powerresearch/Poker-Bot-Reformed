#coding: utf-8

import json
import re
from const import *
from pokerstars.screen_scraper import ScreenScraper
from pokerstars.move_catcher import MoveCatcher
from pokerstars.controller import Controller
from database.data_manager import DataManager
from stats.stats_handler import StatsHandler
from strategy.decision_maker import DecisionMaker

class GameDriver():

    def __init__(self):
        self.screen_scraper = ScreenScraper()#{{{
        init_values = screen_scraper.get_init_values()
        self.stack          = init_values['stack'] 
        self.game_number    = init_values['game_number']
        self.cards          = init_values['cards'] + ['', '', '', '']
        self.button         = init_values['button']
        self.player_name    = init_values['player_name']
        self.steal_position = self.button == 0 or self.button == 1
        self.active         = [1, 1, 1, 1, 1, 1]
        self.stats_handler  = StatsHandler()
        self.data_manager   = DataManager(player_names)
        self.decision_maker = DecisionMaker()
        self.pot            = 0
        self.last_better    = -1
        self.all_limper     = -1#}}}

    @classmethod
    def count_game(cls):
        try:#{{{
            cls.game_count += 1
        else:
            cls.game_count = 1#}}}

    def game_stream(self):
        next_game = pre_flop(self)#{{{
        if next_game:
            return self.game_number
        for stage in xrange(1, 4):
            next_game = post_flop(self, stage)
            if next_game:
                return self.game_number#}}}

    def pre_flop(self):
        to_act = (button+3) % 6#{{{
        betting = [0, 0, 0, 0, 0, 0]
        betting[(button+1)%6] = SB
        betting[(button+1)%6] = BB
        bet_round = 1
        people_play = 1
        last_mover = (button+2) % 6
        move_catcher = MoveCatcher(to_act, self.stack, self.game_number)#}}}
        
        while True:
            actions = move_catcher.get_action()#{{{
            for action in actions:
                if action[0] == 'new game':
                    return True
                if action[0] == 'new stage':
                    return False
                if action[0] == 'my move':
                    decision_maker.make_decision(self)
                    break
                actor, value = action
                if value == 'fold':
                    self.active[actor] = 0
                    continue
                if value == self.stack[actor]:
                    self.active[actor] = 0.5
                self.stats_handler.pre_flop_update(action, betting, bet_round, last_better)
                self.pot += value
                self.stack[actor] -= value
                if value+betting[actor] > max(betting):
                    self.last_better = actor
                    last_mover = (actor-1) % 6
                    while True:
                        if active[last_mover] != 1:
                            last_mover = (last_mover-1) % 6
                        else:
                            break
                betting[actor] += value#}}}


    def post_flop(self, stage):
        pass
