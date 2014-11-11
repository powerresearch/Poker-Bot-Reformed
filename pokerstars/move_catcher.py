from pokerstars.screen_scraper import ScreenScraper
from public import map_card_string_to_tuple
from public import change_terminal_color
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
            self.made_my_move = 0
        self.screen_scraper = game_driver.screen_scraper#}}}
    
    def next_stage(self):
        if len(self.cards) == 7:#{{{
            return False
        elif len(self.cards) == 6:
            tmp_card = self.screen_scraper.get_card(6)
            if tmp_card:
                self.cards.append(tmp_card)
                return self.cards
            else:
                return False
        elif len(self.cards) == 5:
            tmp_card = self.screen_scraper.get_card(5)
            if tmp_card:
                self.cards.append(tmp_card)
                return self.cards
            else:
                return False
        else:
            tmp_card1, tmp_card2, tmp_card3 = \
                    [self.screen_scraper.get_card(i) for i in xrange(2, 5)]
            if tmp_card1 and tmp_card2 and tmp_card3:
                self.cards.append(tmp_card1)
                self.cards.append(tmp_card2)
                self.cards.append(tmp_card3)
                return self.cards
            else:
                return False#}}}

    def next_game(self):
        new_game_number = self.screen_scraper.get_game_number()#{{{
        all_fold = 1
        c1, c2 = self.screen_scraper.get_card(0), self.screen_scraper.get_card(1)
        c1, c2 = min([c1, c2]), max([c1, c2])
        if c1 != self.cards[0] or c2 != self.cards[1]:
            change_terminal_color('green')
            print 'game over because my cards are changed'
            print 'new card:', c1, c2
            print 'old card:', self.cards[0], self.cards[1]
            change_terminal_color()
            return new_game_number 
        for i in xrange(1, 6):
            if not self.screen_scraper.has_fold(i):
                all_fold = 0
        if new_game_number != self.game_number or all_fold:
            change_terminal_color('green')
            print 'game over because new game number is', new_game_number
            change_terminal_color()
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
#                    actions.append([player, max(self.betting)-self.betting[player]])
#                    self.betting[player] = max(self.betting)
                    return actions
                else:
                    actions.append([player, 'check'])
        self.to_act = player
        return actions#}}}

    def get_action(self):
        self.betting = self.game_driver.betting
        if self.source == 'ps':
            actions = list()#{{{
            self.screen_scraper.update()
            self.stack = [[]]*6
            for i in xrange(6):
                fail = 0
                while self.stack[i] == []:
                    self.stack[i] = self.screen_scraper.get_stack(i)
                    if self.game_driver.stack[i] == 2.0001:
                        self.game_driver.stack[i] = self.stack[i]
                        self.old_stack[i] = self.stack[i]
                    if self.next_game() != False:
                        next_game_result = self.next_game()
                        actions = [['new game', next_game_result]]
                        return actions
                    if fail == 1:
                        self.screen_scraper.update()
                    fail = 1
            next_game_result = self.next_game()
            if next_game_result:
                actions = [['new game', next_game_result]]
                return actions
            actions += self.round_search()
            next_stage_result = self.next_stage()
            if next_stage_result:
                if not self.all_even():
                    actions += self.make_even()
                actions.append(['new stage', next_stage_result])
            if self.screen_scraper.shining(0):
                if self.old_betting[1:] != self.betting[1:]\
                        or self.game_driver.stage != self.old_stage:
                    actions.append(['my move', 0])
                    self.old_betting = copy.deepcopy(self.betting)
                    self.old_stage = copy.deepcopy(self.game_driver.stage)
            for action in actions:
                if type(action[1]) == float:
                    action[1] = round(action[1], 2)#}}}
        else:#{{{
            while 'has timed out' in self.source[0]\
                    or 'from pot' in self.source[0]\
                    or 'said, "' in self.source[0]\
                    or 'show hand' in self.source[0]\
                    or 'posts big blind' in self.source[0]\
                    or 'posts small blind' in self.source[0]\
                    or 'is disconnect' in self.source[0]\
                    or 'is connect' in self.source[0]:
                self.source = self.source[1:]
            instr = self.source[0]
            cards = self.cards
            self.source = self.source[1:]
            if ': ' in instr:
                name = ':'.join(instr.split(':')[:-1])
                player = self.seat[name]
                if player == 0 and not self.made_my_move:
                    self.source.insert(0, instr)
                    self.made_my_move = 1
                    return [['my move', 0]]
                self.made_my_move = 0
                action_str = instr.split(': ')[-1].strip()
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
                try:
                    if type(actions[0][1]) == float:
                        actions[0][1] = round(actions[0][1], 2)
                except:
                    print instr
                    raise Exception
                self.betting[player] = round(self.betting[player], 2)
                return actions
            else:
                if instr.startswith('Uncalled bet'):
                    return [['new game', 1]]
                if '*** FIRST' in instr or '*** SECOND' in instr:
                    return [['new game', 1]]
                if '*** SUMMARY ***' in instr:
                    return [['new game', 1]]
                if instr.startswith('*** SHOW DOWN ***'):
                    return [['new game', 1]]
                if instr.startswith('*** FLOP ***'):
                    cards234 = re.findall('\[(.*?)\]', instr)[0]
                    cards.append(map_card_string_to_tuple(cards234[:2]))
                    cards.append(map_card_string_to_tuple(cards234[3:5]))
                    cards.append(map_card_string_to_tuple(cards234[6:]))
                    return [['new stage', cards]]
                if instr.startswith('*** TURN ***'):
                    cards5 = re.findall('\[(.{2})\]', instr)[0]
                    cards.append(map_card_string_to_tuple(cards5))
                    return [['new stage', cards]]
                if instr.startswith('*** RIVER ***'):
                    cards6 = re.findall('\[(.{2})\]', instr)[0]
                    cards.append(map_card_string_to_tuple(cards6))
                    return [['new stage', cards]]#}}}
        try:
            return actions
        except:
            print instr
            raise Exception
