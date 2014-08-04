from pokerstars.screen_scraper import ScreenScraper

class MoveCatcher():
    def __init__(self, to_act, betting, \
            active, old_stack, cards, game_number):
        self.to_act         = to_act#{{{
        self.old_stack      = old_stack
        self.game_number    = game_number
        self.cards          = cards  
        self.active         = active
        self.betting        = betting
        self.screen_scraper = ScreenScraper()#}}}
    
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
            if self.active[i] < 1:
                continue
            elif self.betting[i] < max(self.betting):
                actions.append([player, \
                        max(self.betting)-self.betting[player]])
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
                self.betting[player] += self.old_stack[player] - self.stack[player]
                actions.append([player, self.old_stack[player]-self.stack[player]])
            else:
                actions.append([player, 'check'])
        self.to_act = player
        return actions#}}}

    def get_action(self):
        actions = list()#{{{
        self.screen_scraper.update()
        self.stack = [self.screen_scraper.get_stack(i) for i in xrange(6)]
        actions += self.round_search()
        next_game_result = self.next_game()
        next_stage_result = self.next_stage()
        if next_game_result:
            actions.append(['new game', next_game_result])
        if next_stage_result:
            if not self.all_even():
                self.make_even()
            actions.append(['new stage', next_stage_result])
        if self.screen_scraper.shining(0):
            actions.append(['my move', 0])
        for action in actions:
            if type(action[1]) == float:
                action[1] = round(action[1], 2)
        return actions#}}}
