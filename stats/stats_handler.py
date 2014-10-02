import json
import copy
from public import most_probable
from public import has_same
from public import show_stats

with open('stats/prob_factor_close.json') as f:
    prob_factor_close = json.load(f)

with open('stats/prob_factor_open.json') as f:
    prob_factor_open = json.load(f)

STAGE = [u'PF', u'FL', u'TU', u'RV']

class StatsHandler():
    def __init__(self, game_driver):
        self.data_manager = game_driver.data_manager#{{{
        self.game_driver = game_driver
        self.power_rank = [0, 0, 0, 0]
        self.can_beat_table = [0, 0, 0, 0]
        self.outs = [0, 0, 0, 0]
        self.button = game_driver.button
        self.stats = [StatsHandler.trans_prob(StatsHandler.get_preflop_prob(100, 'open'))] * 6
        self.stats_stable = []#}}}

    def preflop_update(self, action, betting, bet_round, people_play, last_better):
        player, value = action#{{{
        if bet_round == 1:
            para = 'close'
            top_n = self.data_manager.get_item(player, u'vpip')
        elif bet_round == 2:
            if last_better == player:
                para = 'open'
                if self.button == player or self.button == (player-1)%6 or self.button == (player+1)%6:
                    top_n = self.data_manager.get_item(player, u'BSA')
                else:
                    top_n = self.data_manager.get_item(player, u'pfr')
            else:
                para = 'close'
                top_n = (self.data_manager.get_item(player, u'vpip')\
                        + self.data_manager.get_item(player, u'pfr')) / 2
        elif bet_round == 3:
            if last_better == player:
                para = 'open'
                top_n = self.data_manager.get_item(player, u'3B')
            else:
                para = 'close'
                top_n = self.data_manager.get_item(player, u'3B')
        elif bet_round >= 4:
            if last_better == player:
                top_n = self.data_manager.get_item(player, u'4B')
                para = 'open'
            else:
                top_n = self.data_manager.get_item(player, u'4B')
                para = 'close'
        small_table = self.get_preflop_prob(top_n*100, para)
        self.stats[player] = self.trans_prob(small_table)
        return self.stats#}}}
    
    @staticmethod
    def map_power_to_prob(can_beat, left_vertex, right_vertex, slope=1.5, min_prob=0.2):
        if can_beat < left_vertex:#{{{
            prob = 1 - (left_vertex-can_beat)*slope
        elif can_beat > right_vertex:
            prob = 1 - (can_beat-right_vertex)*slope
        else:
            prob = 1
        if prob < 0.1:
            prob = 0.1
        return prob#}}}

    def postflop_update(self, actor, postflop_status_list, cards, stage):
        if not self.power_rank[stage]:#{{{
            self.power_rank[stage] = self.game_driver.power_rank[stage]
        if not self.can_beat_table[stage]:
            self.can_beat_table[stage], self.outs[stage] = \
                    self.game_driver.can_beat_table[stage], \
                    self.game_driver.outs[stage] 
        postflop_status = postflop_status_list[actor]
        if self.game_driver.source != 'ps':
            raw_input()
        to_print = list()
        if postflop_status == 'check':#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            if self.game_driver.last_better == actor:
                                cb_prob = self.data_manager.get_item(STAGE[stage]+u'CB', actor)
                                check_prob = 1-cb_prob
                            else:
                                dk_prob = self.data_manager.get_item(STAGE[stage]+u'DK', actor)
                                check_prob = 1-dk_prob
                            vertex_l = 0
                            vertex_r = check_prob - 0.1
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status == 'cb':#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            cb_prob = self.data_manager.get_item(STAGE[stage]+u'CB', actor)
                            check_prob = 1-cb_prob
                            cr_prob = self.data_manager.get_item(STAGE[stage]+u'CR', actor)
                            vertex_l = check_prob + 0.15
                            vertex_r = 1
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status == 'dk':#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            dk_prob = self.data_manager.get_item(STAGE[stage]+u'DK', actor)
                            cr_prob = self.data_manager.get_item(STAGE[stage]+u'CR', actor)
                            check_prob = 1-dk_prob
                            vertex_l = check_prob + 0.15
                            vertex_r = 1
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status == 'cr':#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            cb_prob = self.data_manager.get_item(STAGE[stage]+u'CB', actor)
                            vertex_l = cb_prob + 0.15
                            vertex_r = 1
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status == 'raise':#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            cb_prob = self.data_manager.get_item(STAGE[stage]+u'CB', actor)
                            raise_prob = self.data_manager.get_item(STAGE[stage]+u'R', actor)
                            vertex_l = 1-raise_prob + 0.15
                            vertex_r = 1
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob
                                    #}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status in ['callcb', 'calldk']:#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            fold_prob = 1 - (self.data_manager.get_item(STAGE[stage]+u'FCB', actor)\
                                    +self.data_manager.get_item(STAGE[stage]+u'FDK', actor)) / 2.0
                            raise_prob = self.data_manager.get_item(STAGE[stage]+u'R', actor)
                            vertex_l = fold_prob + 0.15
                            vertex_r = (1-raise_prob)
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status in ['callraise', 'callcr', 'checkcallraise', 'checkcallcr']:#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            fold_prob = 1 - self.data_manager.get_item(STAGE[stage]+u'FR', actor)
                            vertex_l = fold_prob + 0.15
                            vertex_r = 1
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        if postflop_status in ['checkcallcb', 'checkcalldk']:#{{{
            for num1 in xrange(2, 15):
                for col1 in xrange(1, 5):
                    for num2 in xrange(2, 15):
                        for col2 in xrange(1, 5):
                            big_card = max([num1, col1], [num2, col2])
                            small_card = min([num1, col1], [num2, col2])
                            if big_card == small_card:
                                continue
                            if has_same([big_card, small_card]+cards):
                                self.stats[actor][num1][col1][num2][col2] = 0
                                continue
                            can_beat = self.can_beat_table[stage][small_card[0]][small_card[1]]\
                                    [big_card[0]][big_card[1]] 
                            fold_prob = 1 - (self.data_manager.get_item(STAGE[stage]+u'FCB', actor)\
                                    +self.data_manager.get_item(STAGE[stage]+u'FDK', actor)) / 2.0
                            raise_prob = self.data_manager.get_item(STAGE[stage]+u'CR', actor)
                            vertex_l = fold_prob + 0.15
                            vertex_r = 1 - raise_prob
                            prob = self.map_power_to_prob(can_beat, vertex_l, vertex_r, slope=3)
#                           print big_card, small_card, can_beat, vertex_l, vertex_r, prob
                            self.stats[actor][num1][col1][num2][col2] = \
                                    self.stats_stable[actor][num1][col1][num2][col2] * prob#}}}
                            to_print.append([[num1, col1], [num2, col2],\
                                    self.stats[actor][num1][col1][num2][col2], can_beat, vertex_l, vertex_r])
        to_print = sorted(to_print, key=lambda x:x[2])
#        for tup in to_print:
#            print tup
#}}}

    def postflop_big_update(self):
        self.stats_stable = copy.deepcopy(self.stats)

    @staticmethod
    def trans_prob(small_table):
        big_table = {}#{{{
        for num1 in xrange(2, 15):
            big_table[num1] = {}
            for col1 in xrange(1, 5):
                big_table[num1][col1] = {}
                for num2 in xrange(2, 15):
                    big_table[num1][col1][num2] = {}
                    for col2 in xrange(1, 5):
                        if num1 == num2 and col1 == col2:
                            continue
                        if col1 == col2:
                            big_table[num1][col1][num2][col2] = small_table[min(num1, num2)][max(num1, num2)]
                        else:
                            big_table[num1][col1][num2][col2] = small_table[max(num1, num2)][min(num1, num2)]
        return big_table#}}}

    @staticmethod
    def get_preflop_prob(top_n, arg):
        if arg == 'close':#{{{
            n1 = top_n * 0.85
            n2 = top_n
            n3 = top_n * 1.15
            n = [n1, n2, n3]
        else:
            n = range(0, int(top_n)+1, 1)
        r = [StatsHandler.get_preflop_prob_pointy(n1, 'close') for n1 in n]
        prob = {}
        for c1 in r[0]:
            prob[c1] = {}
            for c2 in r[0]:
                rr = [rrr[c1][c2] for rrr in r]
                prob[c1][c2] = max(rr)
        for c1 in prob:
            for c2 in prob[c1]:
                prob[c1][c2] = 0.2 + prob[c1][c2] * 0.8
        return prob#}}}

    @staticmethod
    def get_preflop_prob_pointy(top_n, arg):
        if arg == 'open':#{{{
            prob_factor = prob_factor_open
        else:
            prob_factor = prob_factor_close
        cut_points = [0.5, 1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 45, 50, 100]
        coef = [0] * len(cut_points)
        for point_index in xrange(len(cut_points)-1, -1, -1):
            coef[point_index] = 1.0 / (200+pow(abs(cut_points[point_index]-top_n), 2))
#           if cut_points[point_index] < top_n:
#               break
        prob = {}
        for c1 in xrange(2, 15): 
            prob[c1] = {}
            for c2 in xrange(2, 15):
                s = 0
                for (c, p) in zip(coef, cut_points):
                    s += c * prob_factor[unicode(p)][unicode(c1)][unicode(c2)]
                prob[c1][c2] = s
        max_prob = 0
        for c1 in xrange(2, 15):
            for c2 in xrange(2, 15):
                if prob[c1][c2] > max_prob:
                    max_prob = prob[c1][c2]
        for c1 in xrange(2, 15):
            for c2 in xrange(2, 15):
                prob[c1][c2] = prob[c1][c2] / max_prob
        return prob#}}}
    
    @staticmethod
    def pick_top(top_n, arg):
        big_table = StatsHandler.trans_prob(StatsHandler.get_preflop_prob(top_n, arg))#{{{
        all_combo = list()
        for num1 in big_table:
            for col1 in big_table[num1]:
                for num2 in big_table[num1][col1]:
                    for col2 in big_table[num1][col1][num2]:
                        all_combo.append([big_table[num1][col1][num2][col2], \
                                [num1, col1], [num2, col2]])
        sorted_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
        result = list()
        for combo in sorted_combo:
            if combo[1][1] == combo[2][1]:
                n1 = min(combo[1][0], combo[2][0])
                n2 = max(combo[1][0], combo[2][0])
            else:
                n1 = max(combo[1][0], combo[2][0])
                n2 = min(combo[1][0], combo[2][0])
            if not [combo[0], n1, n2] in result:
                result.append([combo[0], n1, n2])
        return result#}}}
