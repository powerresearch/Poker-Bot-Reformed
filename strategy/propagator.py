import copy
from strategy.decision_maker_simple import PostflopDecisionMaker
from public import nodes_of_tree
from public import find_out
from public import color_make_different
from public import enum_cards
from public import has_same

class Propagator(PostflopDecisionMaker):
    
    def __init__(self, status_package):
        self.value          =   0
        self.hero           =   status_package['hero']
        self.betting        =   copy.deepcopy(status_package['betting']) 
        self.stack          =   copy.deepcopy(status_package['stack'])
        self.pot            =   status_package['pot']
        self.active         =   copy.deepcopy(status_package['active'])
        self.actor          =   status_package['actor'] 
        self.stats          =   copy.deepcopy(status_package['stats'])
        self.stage          =   status_package['stage']
        self.cards          =   copy.deepcopy(status_package['cards'])
        self.cards[:2]      =   self.trans_cards(self.cards[:2])
        self.button         =   status_package['button']
        self.last_better    =   status_package['last_better']
        self.status_package =   copy.deepcopy(status_package)
        self.source         =   ''
        self.small_stats    =   self.compress_stats()
        self.get_avg_stats()
        last_mover = self.button
        self.total_prob     = 0
        for n1,c1,n2,c2,prob in nodes_of_tree(self.stats[actor], 4):
            self.total_prob += prob
        while self.active[last_mover] != 1:
            last_mover = (last_mover-1) % 6
        try:
            self.wcts       = status_package['wcts']
            self.dummy_action_ep = status_package['dummy_action_ep']
            self.dummy_action_lp = status_package['dummy_action_lp']
        except:
            self.wcts       = []
            self.dummy_action_ep = []
            self.dummy_action_lp = []

    def trans_cards(self, cards): 
        the_color = color_make_different(self.stage, self.cards)
        result = copy.deepcopy(cards)
        if cards[0][1] not in the_color:
            result[0][1] = 0
        if cards[1][1] not in the_color:
            result[1][1] = 0
        return result

    def next_stage(self):
        if sum(self.betting) == 0:
            if self.actor == last_mover:
                return True
        for i in xrange(6):
            if self.active[i] == 1:
                if self.betting[i] != max(self.betting):
                    return False
        return True

    def show_down(self):
        total_win_prob = 1
        if self.stage == 3:
            for i in xrange(1, 6):
                wp = 0
                lp = 0
                for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[i], 4):
                    fo0 = find_out(self.cards)
                    fo1 = find_out(self.cards[2:] + [[n1,c1],[n2,c2]])
                    if fo0 > fo1:
                        wp += prob
                    elif fo1 > fo0:
                        lp += prob
                    else:
                        wp += prob * 0.5
                        lp += prob * 0.5
                    total_win_prob *= wp / (wp+lp)
        if self.stage == 2:
            for nn1,cc1 in enum_cards(1):
                if has_same(self.cards+[[nn1, cc1]]):
                    continue
                tmp_total_win_prob = 1
                for i in xrange(1, 6):
                    wp = 0
                    lp = 0
                    for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[i], 4):
                        if has_same(self.cards+[[n1,c1], [n2,c2], [[nn1, cc1]]]):
                            continue
                        fo0 = find_out(self.cards+[[n1,c1]])
                        fo1 = find_out(self.cards[:2]+[[nn1, cc1]]+[[n1,c1],[n2,c2]])
                        if fo0 > fo1:
                            wp += prob
                        elif fo1 > fo0:
                            lp += prob
                        else:
                            wp += prob * 0.5
                            lp += prob * 0.5
                        tmp_total_win_prob *= wp / (wp+lp)
                total_win_prob += tmp_total_win_prob
            tmp_total_win_prob /= 46
        if self.stage == 1:
            count = 0
            for nn1,cc1,nn2,cc2 in enum_cards(2):
                if has_same(self.cards+[[nn1, cc1], [nn2, cc2]]):
                    continue
                count += 1
                tmp_total_win_prob = 1
                for i in xrange(1, 6):
                    wp = 0
                    lp = 0
                    for n1, c1, n2, c2, prob in nodes_of_tree(self.small_stats[i], 4):
                        if has_same(self.cards+[[n1,c1], [n2,c2], [[nn1, cc1]]]):
                            continue
                        fo0 = find_out(self.cards+[[n1,c1]])
                        fo1 = find_out(self.cards[:2]+[[nn1, cc1]]+[[n1,c1],[n2,c2]])
                        if fo0 > fo1:
                            wp += prob
                        elif fo1 > fo0:
                            lp += prob
                        else:
                            wp += prob * 0.5
                            lp += prob * 0.5
                        tmp_total_win_prob *= wp / (wp+lp)
                total_win_prob += tmp_total_win_prob
            tmp_total_win_prob /= count
        return total_win_prob

    def get_dummy_action(self, n1, c1, n2, c2):
        if max(self.betting) == 0:
            possible_action = ['check', 'bet']
        else:
            possible_action = ['call', 'raise', 'fold']
        if self.actor == self.last_mover:
            for action in self.dummy_actiono_lp[n1][c1][n2][c2]:
                if action in possible_action:
                    return action
            raise Exception
        else:
            for action in self.dummy_actiono_ep[n1][c1][n2][c2]:
                if action in possible_action:
                    return action
            raise Exception

    def next_propagation(self, action):
        if sum([i==1 for i in self.active]) == 1:
            for i in xrange(6):
                self.pot -= self.betting[i] - min(self.betting)
            self.value += self.betting[0] - min(self.betting)
            self.value += pot * self.show_down()
            return self.value
        for n1, c1, n2, c2, prob in nodes_of_tree(self.stats[actor], 4):
            [[n1, cc1], [n2, cc2]] = self.trans_cards([[n1, c1], [n2, c2]])
            if action == self.get_dummy_action(n1, cc1, n2, cc2):
                continue
            else:
                del self.stats_package['stats'][actor][n1][c1][n2][c2]
        self.status_package['pot'] = self.pot
        self.status_package['betting'] = self.betting
        self.status_package['stack'] = self.stack
        self.status_package['active'] = self.active
        if self.next_stage():
            if self.stage == 3:
                self.value += self.pot * self.show_down()
                return self.value 
            else:
                self.status_package['betting'] = [0, 0, 0, 0, 0, 0]
                actor = (self.button+1) % 6
                while self.active[actor] != 1:
                    actor = (actor+1) % 6
                self.status_package['actor'] = actor
                for n, c in enum_cards(1):
                    if has_same(self.cards+[[n, c]]):
                        continue
                    else:
                        self.status_package['cards'] = self.cards+[[n, c]]
                        for n1,c1,t in nodes_of_tree(self.status_package\
                                ['stats'][actor], 2):
                            if [n1,c1] == [n, c]:
                                del self.status_package['stats'][actor][n1][c1]
                                continue
                            for n2, c2, p in nodes_of_tree(t, 2):
                                if [n2,c2] == [n, c]:
                                    del self.status_package['stats'][actor][n1][c1][n2][c2]
                    self.status_package['cards'] += [[n, c]]
                    new_propagator = Propagator(self.status_package)
                    self.value += new_propagator.propagate() / 47
        else:
            new_propagator = Propagator(self.status_package)
            self.value += new_propagator.propagate()

    def propagate(self):
        if self.wcts == []:
            if self.stage == 1:
                self.get_win_chance_table_flop()
            if self.stage == 2:
                self.get_win_chance_table_turn()
            if self.stage == 3:
                self.get_win_chance_table_river()
            self.get_dummy_action_table()
        if self.actor == self.hero:
            action = self.get_dummy_action(self.cards[0][0], self.cards[0][1],\
                    self.cards[1][0], self.cards[1][1])
            if action == 'check':
                pass
            elif action == 'bet':
                if self.stack[actor] < 1.2 * self.pot * (0.5 + 0.3*(self.stage==1)):
                    self.betting[actor] += self.stack[actor]
                    self.pot += self.stack[actor]
                    self.value -= self.stack[actor]
                    self.stack[actor] = 0
                    self.active[actor] = 0.5
                else:
                    self.betting[actor] += self.pot * (0.5 + 0.3*(self.stage==1))
                    self.pot *= 1 + (0.5 + 0.3*(self.stage==1))
                    self.value -= self.pot * (0.5 + 0.3*(self.stage==1))
                    self.stack[actor] -= self.pot * (0.5 + 0.3*(self.stage==1))
            elif action == 'call':
                to_call = max(self.betting) - self.betting[actor]
                if to_call >= self.stack[actor] * 0.8:
                    self.betting[actor] += self.stack[actor]
                    self.pot += self.stack[actor]
                    self.value -= self.stack[actor]
                    self.stack[actor] = 0
                    self.active[actor] = 0.5
                else:
                    self.betting[actor] = max(self.betting)
                    self.pot += to_call
                    self.value -= to_call
                    self.stack[actor] -= to_call
            elif action == 'raise':
                to_call = max(self.betting) - self.betting[actor]
                ori_pot = self.pot - sum(self.betting)
                raise_amount = to_call + (ori_pot+2*to_call) * (0.3+0.2*(self.stage==1))
                if raise_amount >= self.stack[actor] * 0.8:
                    self.betting[actor] += self.stack[actor]
                    self.pot += self.stack[actor]
                    self.value -= self.stack[actor]
                    self.stack[actor] = 0
                    self.active[actor] = 0.5
                else:
                    self.betting[actor] += raise_amount
                    self.pot += raise_amount
                    self.value -= raise_amount
                    self.stack[actor] -= raise_amount
            else:
                return self.value
            value += self.next_propagation(action)
        else:
            if max(self.betting) == 0:
                possible_action = ['check', 'bet']
            else:
                possible_action = ['call', 'raise', 'fold']
            for action in possible_action:
                if action == 'check':
                    pass
                elif action == 'bet':
                    if self.stack[actor] < 1.2 * self.pot * (0.5 + 0.3*(self.stage==1)):
                        self.betting[actor] += self.stack[actor]
                        self.pot += self.stack[actor]
                        self.value -= self.stack[actor]
                        self.stack[actor] = 0
                        self.active[actor] = 0.5
                    else:
                        self.betting[actor] += self.pot * (0.5 + 0.3*(self.stage==1))
                        self.pot *= 1 + (0.5 + 0.3*(self.stage==1))
                        self.value -= self.pot * (0.5 + 0.3*(self.stage==1))
                        self.stack[actor] -= self.pot * (0.5 + 0.3*(self.stage==1))
                elif action == 'call':
                    to_call = max(self.betting) - self.betting[actor]
                    if to_call >= self.stack[actor] * 0.8:
                        self.betting[actor] += self.stack[actor]
                        self.pot += self.stack[actor]
                        self.value -= self.stack[actor]
                        self.stack[actor] = 0
                        self.active[actor] = 0.5
                    else:
                        self.betting[actor] = max(self.betting)
                        self.pot += to_call
                        self.value -= to_call
                        self.stack[actor] -= to_call
                elif action == 'raise':
                    to_call = max(self.betting) - self.betting[actor]
                    ori_pot = self.pot - sum(self.betting)
                    raise_amount = to_call + (ori_pot+2*to_call) * (0.3+0.2*(self.stage==1))
                    if raise_amount >= self.stack[actor] * 0.8:
                        self.betting[actor] += self.stack[actor]
                        self.pot += self.stack[actor]
                        self.value -= self.stack[actor]
                        self.stack[actor] = 0
                        self.active[actor] = 0.5
                    else:
                        self.betting[actor] += raise_amount
                        self.pot += raise_amount
                        self.value -= raise_amount
                        self.stack[actor] -= raise_amount
                else:
                    self.active[actor] = 0
                self.value += self.next_propagation(action) 
        return self.value
