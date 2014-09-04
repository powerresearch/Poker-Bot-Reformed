from pokerstars.screen_scraper import ScreenScraper
from public import map_card_string_to_tuple
import re
import time
import json
import copy

class MoveCatcher():
    def __init__(self, to_act, game_driver): 
        self.to_act         = to_act#{{{
        self.game_driver    = game_driver
        self.old_stack      = game_driver.stack
        self.game_number    = game_driver.game_number
        self.cards          = game_driver.cards  
        self.active         = game_driver.active
        self.betting        = game_driver.betting
        self.old_betting    = copy.deepcopy(game_driver.betting)
        self.old_stage      = copy.deepcopy(game_driver.stage)
        if game_driver.source == 'ps': 
            self.source = 'ps'
        else:
            self.source = game_driver.source.splitlines()[12:]
            self.seat = game_driver.seat
        self.screen_scraper = game_driver.screen_scraper#}}}
    
    def next_stage(self):
        if self.cards[6]:#{{{
            return False
        elif self.cards[5]:
            self.cards[6] = self.screen_scraper.get_card(6)
            if self.cards[6]:
                return self.cards
            else:
                return False
        elif self.cards[4]:
            self.cards[5] = self.screen_scraper.get_card(5)
            if self.cards[5]:
                return self.cards
            else:
                return False
        else:
            self.cards[2] = self.screen_scraper.get_card(2)
            self.cards[3] = self.screen_scraper.get_card(3)
            self.cards[4] = self.screen_scraper.get_card(4)
            if self.cards[2] and self.cards[3] and self.cards[4]:
                return self.cards
            else:
                return False#}}}

    def next_game(self):
        new_game_number = self.screen_scraper.get_game_number()#{{{
        if new_game_number != self.game_number:
            return new_game_number
        else:
            return False#}}}

    def all_even(self):
        amount = max(self.betting)#{{{
        for i in xrange(6):
            if self.active[i] == 1:
                if self.betting[i] != amount:
                    return False
        return True#}}}

    def make_even(self):
        amount = max(self.betting)#{{{
        actions = list()
        for i in xrange(6):
            player = (self.to_act+i) % 6
            if self.active[player] < 1:
                continue
            if self.screen_scraper.has_fold(player):
                actions.append([player, 'fold'])
            elif self.betting[player] < max(self.betting):
                actions.append([player, \
                        max(self.betting)-self.betting[player]])
                self.betting[player] = max(self.betting)
            else:
                continue
        return actions#}}}

    def round_search(self):
        actions = list()#{{{
        shining_player = self.screen_scraper.shining()
        while type(shining_player) != int:
            self.screen_scraper.update()
            shining_player = self.screen_scraper.shining()
        for i in xrange(6):
            player = (self.to_act+i) % 6
            if player == shining_player:
                break
            if self.active[player] != 1:
                continue
            elif self.screen_scraper.has_fold(player):
                self.active[player] = 0
                actions.append([player, 'fold'])
            elif self.stack[player] != self.old_stack[player]:
                if self.stack[player] == 0:
                    self.active[player] = 0.5
                if self.stack[player] == 'sitting out':
                    self.active[player] = 0
                    actions.append([player, 'fold'])
                else:
                    self.betting[player] += self.old_stack[player] - self.stack[player]
                    self.betting[player] = round(self.betting[player], 2)
                    actions.append([player, self.old_stack[player]-self.stack[player]])
            else:
                if self.betting[player] != max(self.betting):
                    actions.append([player, 'fold'])
                else:
                    actions.append([player, 'check'])
        self.to_act = player
        return actions#}}}

    def get_action(self):
        self.betting = self.game_driver.betting
        if self.source == 'ps':
            actions = list()#{{{
            self.screen_scraper.update()
            self.stack = [self.screen_scraper.get_stack(i) for i in xrange(6)]
            next_game_result = self.next_game()
            if next_game_result:
                actions = [['new game', next_game_result]]
            actions += self.round_search()
            next_stage_result = self.next_stage()
            if next_stage_result:
                if not self.all_even():
                    actions += self.make_even()
                actions.append(['new stage', next_stage_result])
            if self.screen_scraper.shining(0):
                print self.old_betting, self.betting
                print self.old_stage, self.game_driver.stage
                if self.old_betting[1:] != self.betting[1:]\
                        or self.game_driver.stage != self.old_stage:
                    actions.append(['my move', 0])
                    self.old_betting = copy.deepcopy(self.betting)
                    self.old_stage = copy.deepcopy(self.game_driver.stage)
            for action in actions:
                if type(action[1]) == float:
                    action[1] = round(action[1], 2)#}}}
        else:
            instr = self.source[0]#{{{
            cards = self.cards
            self.source = self.source[1:]
            if ':' in instr:
                player = self.seat[instr.split(':')[0]]
                action_str = instr.split(': ')[1].strip()
                action_str = re.sub(' and is all-in', '', action_str)
                if action_str == 'folds':
                    actions = [[player, 'fold']]
                if action_str == 'checks':
                    actions = [[player, 'check']]
                if action_str.startswith('bets'):
                    actions = [[player, float(action_str.split('$')[1])]]
                    self.betting[player] += float(action_str.split('$')[1])
                if action_str.startswith('calls'):
                    actions = [[player, float(action_str.split('$')[1])]]
                    self.betting[player] += float(action_str.split('$')[1])
                if action_str.startswith('raises'):
                    amount = re.findall(r'raises \$(.*?) to', action_str)[0]
                    actions = [[player, max(self.betting) + float(amount)\
                            - self.betting[player]]]
                    self.betting[player] = max(self.betting) + float(amount)
                if type(actions[0][1]) == float:
                    actions[0][1] = round(actions[0][1], 2)
                if player == 0:
                    actions = [['my move', 0]] + actions
                else:
                    self.betting[player] = round(self.betting[player], 2)
                return actions
            else:
                if instr.startswith('Uncalled bet'):
                    return [['new game', 1]]
                if instr.startswith('*** SHOW DOWN ***'):
                    return [['new game', 1]]
                if instr.startswith('*** FLOP ***'):
                    cards234 = re.findall('\[(.*?)\]', instr)[0]
                    cards[2] = map_card_string_to_tuple(cards234[:2])
                    cards[3] = map_card_string_to_tuple(cards234[3:5])
                    cards[4] = map_card_string_to_tuple(cards234[6:])
                    return [['new stage', cards]]
                if instr.startswith('*** TURN ***'):
                    cards5 = re.findall('\[(.{2})\]', instr)[0]
                    cards[5] = map_card_string_to_tuple(cards5)
                    return [['new stage', cards]]
                if instr.startswith('*** RIVER ***'):
                    cards6 = re.findall('\[(.{2})\]', instr)[0]
                    cards[6] = map_card_string_to_tuple(cards6)
                    return [['new stage', cards]]#}}}
        return actions
