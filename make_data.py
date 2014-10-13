#coding: utf-8

import json
import re
import time
from public import is_only_max
from public import get_power_rank
from public import get_board_texture
from public import what_do_i_have
from pokerstars.config import BB, SB
from pokerstars.screen_scraper import ScreenScraper
from pokerstars.move_catcher import MoveCatcher
from stats.stats_handler import StatsHandler
from database.data_manager import DataManager

class GameDriver():
    
    def __init__(self, game_record, save_as):
        self.screen_scraper = ScreenScraper(game_driver=self, source=game_record)#{{{
        self.save_as        = save_as
        self.flop_actions   = list()
        self.turn_actions   = list()
        self.river_actions  = list()
        self.flop_texture   = list()
        self.turn_texture   = list()
        self.river_texture  = list()
        self.flop_stack_status = list()
        self.turn_stack_status = list()
        self.river_stack_status = list()
        self.flop_i_have    = list()
        self.turn_i_have    = list()
        self.river_i_have   = list()
        self.position       = list()
        self.rel_pos        = [0]
        self.is_last_better = [0]
        self.pf_bet_round   = [0, 0, 0, 0, 0]
        self.X              = list()
        self.source         = game_record
        init_values = self.screen_scraper.get_init_values()
        self.stack          = init_values['stack'] 
        self.game_number    = init_values['game_number']
#        print self.game_number
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
#       self.decision_maker = DecisionMaker(self)
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
#        print 'Stack:', self.stack#{{{
#        print 'Game Number:', self.game_number
#        print 'Button:', self.button
#        print 'Cards:', self.cards[:2]
#        print 'Names:', self.player_name
#        if self.stack[0] > 3 and self.decision_maker.get_preflop_move(self.cards) == 0:
#            self.controller.sit_out()
#            return self.game_number
#        if self.source == 'ps' and self.decision_maker.get_preflop_move(self.cards) == 0 and self.button != 4:
#            self.controller.fold()
#            return self.game_number
#        print#}}}
        indicator = self.preflop()#{{{
        stages = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
        self.stage = 1 
        if indicator == 'new game':
            return self.game_number
        for i in xrange(1, 6):
            oppo_pos = i
            break
        my_pos = (0-self.button-1) % 6
        oppo_pos = (oppo_pos-self.button-1) % 6
        self.position = [1.0*my_pos / 5, 1.0*oppo_pos / 5]
        if my_pos > oppo_pos:
            self.rel_pos = [1]
        else:
            self.rel_pos = [0]
        if self.bet_round > 4:
            self.pf_bet_round[4] = 1
        else:
            self.pf_bet_round[self.bet_round] = 1 
        for self.stage in xrange(1, 4):
            if sum(self.active) != 2:
                return self.game_number
            if not self.active[0]:
                return self.game_number
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
#           self.decision_maker.make_decision(self)
#           time.sleep(0.5)
            return []
        actor, value = action
        if value == 'fold':
            self.active[actor] = 0
            return []
        if value == 'check':
            return []
#       self.betting[actor] = round(self.betting[actor]+value, 2)
        if is_only_max(self.betting, actor):
            self.last_better = actor
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
#           self.decision_maker.make_decision(self)
#           time.sleep(0.5)
            return []
        actor, value = action
        if value == 'fold':
            self.active[actor] = 0
            if actor == 0: 
                Y = -1
                if self.stage == 1:
                    self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                if self.stage == 2:
                    self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                if self.stage == 3:
                    self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
#                print 'position', self.position
#                print 'rel position', self.rel_pos
#                print 'bet round', self.pf_bet_round
#                print 'last better', self.is_last_better
#                print 'action', self.flop_actions
#                print 'texture', self.flop_texture
#                print 'i have', self.flop_i_have
#                print 'stack feature', self.flop_stack_status
                self.X = self.position+self.rel_pos\
                        +self.pf_bet_round+self.is_last_better\
                        +self.flop_actions+self.turn_actions+self.river_actions\
                        +self.flop_texture+self.turn_texture+self.river_texture\
                        +self.flop_stack_status+self.turn_stack_status+self.river_stack_status
                with open('learning/'+self.save_as+'.txt'+str(len(self.X)), 'a') as f:
                    for feature in self.X:
                        f.write(str(feature)+',')
                    f.write(str(Y)+'\n')
                if self.stage == 1:
                    self.flop_actions.append(-1)
                elif self.stage == 2:
                    self.turn_actions.append(-1)
                elif self.stage == 3:
                    self.river_actions.append(-1)
            else:
                if self.stage == 1:
                    self.flop_actions.append(-1)
                    self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                elif self.stage == 2:
                    self.turn_actions.append(-1)
                    self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                else:
                    self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
                    self.river_actions.append(-1)
            return []
        if value == 'check':
            self.postflop_status[actor] = 'check'
            value = 0
            if actor == 0: 
                if self.stage == 1:
                    self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                if self.stage == 2:
                    self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                if self.stage == 3:
                    self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
                Y = 0
#                print 'position', self.position
#                print 'rel position', self.rel_pos
#                print 'bet round', self.pf_bet_round
#                print 'last better', self.is_last_better
#                print 'action', self.flop_actions
#                print 'texture', self.flop_texture
#                print 'i have', self.flop_i_have
#                print 'stack feature', self.flop_stack_status
                self.X = self.position+self.rel_pos\
                        +self.pf_bet_round+self.is_last_better\
                        +self.flop_actions+self.turn_actions+self.river_actions\
                        +self.flop_texture+self.turn_texture+self.river_texture\
                        +self.flop_stack_status+self.turn_stack_status+self.river_stack_status
                with open('learning/'+self.save_as+'.txt'+str(len(self.X)), 'a') as f:
                    for feature in self.X:
                        f.write(str(feature)+',')
                    f.write(str(Y)+'\n')
                if self.stage == 1:
                    self.flop_actions.append(0)
                elif self.stage == 2:
                    self.turn_actions.append(0)
                elif self.stage == 3:
                    self.river_actions.append(0)
            else:
                if self.stage == 1:
                    self.flop_actions.append(0)
                    self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                elif self.stage == 2:
                    self.turn_actions.append(0)
                    self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                else:
                    self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
                    self.river_actions.append(0)
        else:
            if is_only_max(self.betting, actor):
                Y = (self.betting[actor]*2-sum(self.betting)) / self.pot
                if actor == 0: 
                    if self.stage == 1:
                        self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                    if self.stage == 2:
                        self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                    if self.stage == 3:
                        self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
#                    print 'position', self.position
#                    print 'rel position', self.rel_pos
#                    print 'bet round', self.pf_bet_round
#                    print 'last better', self.is_last_better
#                    print 'action', self.flop_actions
#                    print 'texture', self.flop_texture
#                    print 'i have', self.flop_i_have
#                    print 'stack feature', self.flop_stack_status
                    self.X = self.position+self.rel_pos\
                            +self.pf_bet_round+self.is_last_better\
                            +self.flop_actions+self.turn_actions+self.river_actions\
                            +self.flop_texture+self.turn_texture+self.river_texture\
                            +self.flop_stack_status+self.turn_stack_status+self.river_stack_status
                    with open('learning/'+self.save_as+'.txt'+str(len(self.X)), 'a') as f:
                        for feature in self.X:
                            f.write(str(feature)+',')
                        f.write(str(Y)+'\n')
                    if self.stage == 1:
                        self.flop_actions.append(Y)
                    elif self.stage == 2:
                        self.turn_actions.append(Y)
                    elif self.stage == 3:
                        self.river_actions.append(Y)
                else:
                    if self.stage == 1:
                        self.flop_actions.append(Y)
                        self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                    elif self.stage == 2:
                        self.turn_actions.append(Y)
                        self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                    else:
                        self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
                        self.river_actions.append(Y)
                self.last_better = actor
                self.bet_round += 1
                self.people_play = 1
            else:
                if actor == 0: 
                    if self.stage == 1:
                        self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                    if self.stage == 2:
                        self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                    if self.stage == 3:
                        self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
                    Y = 0
#                    print 'position', self.position
#                    print 'rel position', self.rel_pos
#                    print 'bet round', self.pf_bet_round
#                    print 'last better', self.is_last_better
#                    print 'action', self.flop_actions
#                    print 'texture', self.flop_texture
#                    print 'i have', self.flop_i_have
#                    print 'stack feature', self.flop_stack_status
                    self.X = self.position+self.rel_pos\
                            +self.pf_bet_round+self.is_last_better\
                            +self.flop_actions+self.turn_actions+self.river_actions\
                            +self.flop_texture+self.turn_texture+self.river_texture\
                            +self.flop_stack_status+self.turn_stack_status+self.river_stack_status
                    with open('learning/'+self.save_as+'.txt'+str(len(self.X)), 'a') as f:
                        for feature in self.X:
                            f.write(str(feature)+',')
                        f.write(str(Y)+'\n')
                else:
                    if self.stage == 1:
                        self.flop_actions.append(0)
                        self.flop_stack_status.append(1.0*self.stack[actor]/self.pot)
                    elif self.stage == 2:
                        self.turn_actions.append(0)
                        self.turn_stack_status.append(1.0*self.stack[actor]/self.pot)
                    else:
                        self.river_stack_status.append(1.0*self.stack[actor]/self.pot)
                        self.river_actions.append(0)
                self.people_play += 1
                if self.postflop_status[actor] == 'check':
                    self.postflop_status[actor] = 'checkcall'+\
                            self.postflop_status[self.last_better]
                else:
                    self.postflop_status[actor] = 'call'+\
                            self.postflop_status[self.last_better]
            self.stack[actor] -= value
            self.stack[actor] = round(self.stack[actor], 2)
            if self.stack[actor] == 0:
                self.active[actor] = 0.5
            self.pot += value
            self.pot = round(self.pot, 2)
#        self.stats_handler.postflop_update(actor, self.postflop_status,\
#                self.cards, self.stage)
#        self.can_beat_table[self.stage] = get_can_beat_table(self.power_rank[self.stage],\
#                self.stats_handler.stats, self.last_better, self.active)
#        if self.source != 'ps':
#            show_stats(self.stats_handler.stats, actor)
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
                for action in actions:
                    if action[0] in [1,2,3,4,5] and self.betting[0] < max(self.betting):
                        self.decision_maker.fast_fold(self)
                    indicator = self.handle_preflop_action(action)
                    if indicator:
                        return indicator
                to_act = self.move_catcher.to_act#}}}
            else:#{{{
                if len(actions) == 1:
                    action = actions[0]
                    indicator = self.handle_preflop_action(action)
                    if indicator:
                        return indicator
                else:
                    action = actions[1]
                    if type(action[1]) == float:
                        self.betting[0] -= action[1]
                        self.betting[0] = round(self.betting[0], 2)
                    action = actions[0]
                    indicator = self.handle_preflop_action(action)
                    action = actions[1]
                    self.handle_preflop_action(action)
                    if type(action[1]) == float:
                        self.betting[0] += action[1]
                        self.betting[0] = round(self.betting[0], 2)
                to_act = self.move_catcher.to_act#}}}
            
    def post_flop(self, stage):
        self.postflop_status = ['', '', '', '', '', '']#{{{
#        self.stats_handler.postflop_big_update()
        self.power_rank[stage] = get_power_rank(self.cards[2:stage+4])
        to_act = (self.button+1) % 6
        self.betting = [0, 0, 0, 0, 0, 0]
        self.last_mover = self.button
        while self.last_mover != 1:
            self.last_mover = (self.last_mover-1) % 6
        self.move_catcher.to_act = to_act
        if stage == 1:
            self.flop_texture = get_board_texture(self.stats_handler.stats, self.power_rank[stage],\
                    self.active, self.cards)
            self.flop_i_have = what_do_i_have(self.cards)
        if stage == 2:
            self.turn_texture = get_board_texture(self.stats_handler.stats, self.power_rank[stage],\
                    self.active, self.cards)
            self.turn_i_have = what_do_i_have(self.cards)
        if stage == 3:
            self.river_texture = get_board_texture(self.stats_handler.stats, self.power_rank[stage],\
                    self.active, self.cards)
            self.river_i_have = what_do_i_have(self.cards)
#       move_catcher = MoveCatcher(to_act, self)#}}}
        while True:
            actions = self.move_catcher.get_action()
            if self.source == 'ps':#{{{
                for action in actions:
                    if action[0] == 'new game':
                        return 'new game' 
                for action in actions:
#                    if action[0] in [1,2,3,4,5] and self.betting[0] < max(self.betting):
#                        self.decision_maker.fast_fold(self)
#                    self.can_beat_table[stage] ,self.outs[stage] =\
#                            get_can_beat_table(self.power_rank[self.stage],\
#                            self.stats_handler.stats, self.last_better, self.active)
                    indicator = self.handle_postflop_action(action)
                    if indicator:
                        return indicator
                to_act = self.move_catcher.to_act#}}}
            else:#{{{
                if len(actions) == 1:
                    action = actions[0]
#                    self.can_beat_table[stage] ,self.outs[stage] =\
#                            get_can_beat_table(self.power_rank[self.stage],\
#                            self.stats_handler.stats, self.last_better, self.active)
                    indicator = self.handle_postflop_action(action)
                    if indicator:
                        return indicator
                else:
#                    self.can_beat_table[stage] ,self.outs[stage] =\
#                            get_can_beat_table(self.power_rank[self.stage],\
#                            self.stats_handler.stats, self.last_better, self.active)
                    action = actions[1]
                    if type(action[1]) == float:
                        self.betting[0] -= action[1]
                        self.betting[0] = round(self.betting[0], 2)
                    action = actions[0]
                    indicator = self.handle_postflop_action(action)
                    action = actions[1]
                    self.handle_postflop_action(action)
                    if type(action[1]) == float:
                        self.betting[0] += action[1]
                        self.betting[0] = round(self.betting[0], 2)
                to_act = self.move_catcher.to_act#}}}
