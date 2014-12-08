import datetime
import copy
import time
import random
from collections import defaultdict
from copy import deepcopy
import random
import threading

def tree():
    return defaultdict(tree)

def nodes_of_tree(t, depth):
    if depth == 2:#{{{
        for l1 in t:
            for l2 in t[l1]:
                yield [l1, l2, t[l1][l2]]
    elif depth == 4:
        for l1 in t:
            for l2 in t[l1]:
                for l3 in t[l1][l2]:
                    for l4 in t[l1][l2][l3]:
                        yield [l1, l2, l3, l4, t[l1][l2][l3][l4]]#}}}

def not_possible(cards):
    if has_same(cards):
        return True 
    count = [0] * 15
    for c in cards:
        count[c[0]] += 1
    for i in xrange(2, 15):
        if count[i] > 4:
            return True 
    return False

def enum_cards(n):
    if n == 1:#{{{
        for num in xrange(2, 15):
            for col in xrange(1, 5):
                yield [num, col]
    elif n == 2:
        for num1 in xrange(2, 15):
            for col1 in xrange(1, 5):
                for num2 in xrange(2, 15):
                    for col2 in xrange(1, 5):
                        yield [num1, col1, num2, col2]#}}}

def is_recent_file(file_name):
    date = datetime.datetime.now().strftime('%Y,%m,%d,%H,%m,%s')#{{{
    date = date.split(',')
    date0 = date[0]+date[1]+date[2]
    date1 = str(int(date0)-1)
    valid_date = list()
    valid_date.append(date0)
    valid_date.append(date1)
    if date[2] == '01':
        valid_date += [str(int(date[0]+date[1])-1)+str(i) for i in xrange(28, 32)]
    if not file_name[2:10] in valid_date:
        return False
    else:
        return True#}}}

def is_only_max(l, index):
    for i in xrange(len(l)):#{{{
        if i == index:
            continue
        if l[i] >= l[index]:
            return False
    return True#}}}

# From here starts power analysis.
#
# 0. Highcard,   [0, 14, 13, ...]:   AK...
# 1. Pair,       [1, 14, 13, ...]:   AAK..
# 2. 2Pairs,     [2, 14, 13, 12]:    AAKKQ
# 3. Set,        [3, 14, 13, 12]:    AAAKQ
# 4. Straight    [4, 14]:            AKQJT
# 5. Flush       [5, 14, 13, ...]:   Flush, AK... 
# 6. Full House  [6, 14, 13]:        AAAKK
# 7. Four OAKind [7, 14, 13]:        AAAAK
# 8. Straight F  [8, 14]:            AKQJT

def find_out(list_of_cards):
    nums = list()#{{{
    nums2 = list()
    cols = [0,0,0,0,0]
    for card in list_of_cards:
        b_mark = 0
        if not card[0] in nums2:
            nums2.append(card[0])
        for num_pair in nums:
            if num_pair[1] == card[0]:
                num_pair[0] += 1
                b_mark = 1
                break
        if not b_mark:
            nums.append([1, card[0]])
        cols[card[1]] += 1
    col = 0
    for i in xrange(5):
        if cols[i] >= 5:
            col = i
    nums = sorted(nums, reverse=True)
    nums += [[1, 0]] * (5-len(nums))
    nums2 = sorted(nums2, reverse=True)
    if nums[0][0] == 4:
        return [7, nums[0][1], nums[1][1]]
    if nums[0][0] == 3 and nums[1][0] >= 2:
        return [6, nums[0][1], nums[1][1]]
    if col:
        tmp = list()
        for card in list_of_cards:
            if card[1] == col:
                tmp.append(card[0])
        tmp = sorted(tmp, reverse=True)
        return [5] + tmp[:5]
    interval = 1
    for i in xrange(len(nums2)-1):
        if nums2[i+1]-nums2[i] == -1:
            interval += 1
        else:
            interval = 1
        if interval == 5:
            return [4, nums2[i+1]]
    if 14 == nums2[0] and 2 == nums2[-1] and 3 == nums2[-2] and 4 == nums2[-3] and 5 == nums2[-4]:
        return [4, 1]
    if nums[0][0] == 3 and nums[1][0] < 2:
        return [3, nums[0][1], nums[1][1], nums[2][1]]
    if nums[0][0] == 2 and nums[1][0] == 2 and nums[2][0] == 2:
        return [2, nums[0][1], nums[1][1], max([nums[-1][1], nums[2][1]])]
    if nums[0][0] == 2 and nums[1][0] == 2:
        return [2, nums[0][1], nums[1][1], nums[2][1]]
    if nums[0][0] == 2:
        return [1, nums[0][1], nums[1][1], nums[2][1], nums[3][1]]
    return [0, nums[0][1], nums[1][1], nums[2][1], nums[3][1], nums[4][1]]#}}}
            
def get_win_chance_table(stats, board):
    if len(board) == 3:#{{{
        return get_win_chance_table_flop(stats, board)
    if len(board) == 4:
        return get_win_chance_table_turn(stats, board)
    if len(board) == 5:
        return get_win_chance_table_river(stats, board)#}}}

def get_win_chance_table_flop(stats, board):
    combination = list()#{{{
    histogram = list()
    for num1 in xrange(2, 15):#{{{
        for col1 in xrange(1, 5):
            if has_same(board+[[num1, col1]]):
                continue
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    if has_same(board+[[num1, col1], [num2, col2]]):
                        continue
                    if [num1, col1] > [num2, col2]:
                        continue
                    the_color = color_make_different(board+[[num1, col1], [num2, col2]])
                    prob = stats[num1][col1][num2][col2]
                    if the_color:
                        if col1 in the_color and col2 in the_color:
                            if [[num1, col1], [num2, col2]] in combination:
                                histogram[combination.index([[num1, col1], [num2, col2]])] += prob 
                                continue
                            else:
                                combination.append([[num1, col1], [num2, col2]])
                                histogram.append(prob)
                        elif col1 in the_color:
                            if [[num1, col1], [num2, 0]] in combination:
                                histogram[combination.index([[num1, col1], [num2, 0]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, col1], [num2, 0]])
                        elif col2 in the_color:
                            if [[num1, 0], [num2, col2]] in combination:
                                histogram[combination.index([[num1, 0], [num2, col2]])] += prob 
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, 0], [num2, col2]])
                        else:
                            if [[num1, 0], [num2, 0]] in combination:
                                histogram[combination.index([[num1, 0], [num2, 0]])] += prob 
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, 0], [num2, 0]])
                    else:
                        if [[num1, 0], [num2, 0]] in combination:
                            histogram[combination.index([[num1, 0], [num2, 0]])] += prob 
                            continue
                        else:
                            histogram.append(prob)
                            combination.append([[num1, 0], [num2, 0]])#}}}
    histogram = [c/sum(histogram) for c in histogram]
    l = len(combination)
    fo_cache = [{} for i in xrange(l)]
    for i in xrange(l):
        fo_cache[i][0] = find_out(board+combination[i])
        for num3 in xrange(2, 15):
            fo_cache[i][num3] = {}
            for col3 in xrange(1, 5):
                fo_cache[i][num3][col3] = find_out(board+combination[i]+[[num3, col3]])
    small_table = [range(l) for i in xrange(l)]#{{{
    for i in xrange(l):
        for j in xrange(i, l):
            comb1 = copy.deepcopy(combination[i]) 
            comb2 = copy.deepcopy(combination[j])
            if comb1[0][1] == 0:
                for col in xrange(1, 5):
                    if [comb1[0][0], col] not in comb1+comb2+board:
                        comb1[0] = [comb1[0][0], col]
                        break
            if comb1[1][1] == 0:
                for col in xrange(1, 5):
                    if [comb1[1][0], col] not in comb1+comb2+board:
                        comb1[1] = [comb1[1][0], col]
                        break
            if comb2[0][1] == 0:
                for col in xrange(1, 5):
                    if [comb2[0][0], col] not in board+comb1+comb2:
                        comb2[0] = [comb2[0][0], col]
                        break
            if comb2[1][1] == 0:
                for col in xrange(1, 5):
                    if [comb2[1][0], col] not in board+comb1+comb2:
                        comb2[1] = [comb2[1][0], col]
                        break
            if has_same(comb1+comb2):
                small_table[i][j] = -1
                small_table[j][i] = -1
                continue
            if comb1[0][1] == 0 or comb1[1][1] == 0 or comb2[0][1] == 0 or comb2[1][1] == 0:
                small_table[i][j] = -1
                small_table[j][i] = -1
                continue
            fo0 = fo_cache[i][0]
            fo1 = fo_cache[j][0] 
            if fo0 < fo1:
                stronger = 1
            elif fo0 == fo1:
                stronger = -1
            else:
                stronger = 0
            a = [0, 0, 0] 
            for num3 in xrange(2, 15):
                for col3 in xrange(1, 5):
                    if [num3, col3] in board+comb1+comb2:
                        continue
                    fo10 = fo_cache[i][num3][col3] 
                    fo11 = fo_cache[j][num3][col3] 
                    if fo10 < fo11:
                        a[2] += 1
                    elif fo10 == fo11:
                        a[1] += 1
                    else:
                        a[0] += 1
            a = [1.0*hh/sum(a) for hh in a]
            if stronger == 1:
                small_table[i][j] = 1 - (1 - a[0]) * (1 - a[0])
                small_table[j][i] = (1 - a[0]) * (1 - a[0])
            elif stronger == 0:
                small_table[i][j] = (1 - a[2]) * (1 - a[2])
                small_table[j][i] = 1 - (1 - a[2]) * (1 - a[2])
            else:
                tmp1 = 1 - (1 - a[0]) * (1 - a[0])
                tmp2 = 1 - (1 - a[2]) * (1 - a[2])
                small_table[i][j] = tmp1 + (1-tmp1-tmp2) / 2
                small_table[j][i] = tmp2 + (1-tmp1-tmp2) / 2#}}}
    less_big_table = tree()
    big_table = tree()
    super_big_table = tree()
    for num1 in xrange(2, 15):#{{{
        for col1 in xrange(1, 5):
            if has_same(board+[[num1, col1]]):
                continue
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    if has_same(board+[[num1, col1], [num2, col2]]):
                        continue
                    if [num1, col1] > [num2, col2]:
                        continue
                    the_color = color_make_different(board+[[num1, col1], [num2, col2]])
                    if the_color:
                        if col1 in the_color and col2 in the_color:
                            the_index = combination.index([[num1, col1], [num2, col2]])
                        elif col1 in the_color:
                            the_index = combination.index([[num1, col1], [num2, 0]]) 
                        elif col2 in the_color:
                            the_index = combination.index([[num1, 0], [num2, col2]]) 
                        else:
                            the_index = combination.index([[num1, 0], [num2, 0]]) 
                    else:
                        the_index = combination.index([[num1, 0], [num2, 0]])
                    wc = 0
                    s = 0
                    for i in xrange(l):
                        if small_table[the_index][i] == -1:
                            continue
                        card_i = combination[i]
                        super_big_table[num1][col1][num2][col2]\
                                [card_i[0][0]][card_i[0][1]][card_i[1][0]][card_i[1][1]]\
                                = small_table[the_index][i]
                        wc += histogram[i] * small_table[the_index][i]
                    less_big_table[combination[the_index][0][0]]\
                            [combination[the_index][0][1]]\
                            [combination[the_index][1][0]]\
                            [combination[the_index][1][1]]\
                            = wc
                    big_table[num1][col1][num2][col2] = wc#}}}
    return less_big_table, big_table, super_big_table#}}}

def get_win_chance_table_turn(stats, board):
    combination = list()#{{{
    histogram = list()
    for num1 in xrange(2, 15):#{{{
        for col1 in xrange(1, 5):
            if has_same(board+[[num1, col1]]):
                continue
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    if has_same(board+[[num1, col1], [num2, col2]]):
                        continue
                    if [num1, col1] > [num2, col2]:
                        continue
                    the_color = color_make_different(board+[[num1, col1], [num2, col2]])
                    prob = stats[num1][col1][num2][col2]
                    if the_color:
                        if col1 in the_color and col2 in the_color:
                            if [[num1, col1], [num2, col2]] in combination:
                                histogram[combination.index([[num1, col1], [num2, col2]])] += prob
                                continue
                            else:
                                combination.append([[num1, col1], [num2, col2]])
                                histogram.append(prob)
                        elif col1 in the_color:
                            if [[num1, col1], [num2, 0]] in combination:
                                histogram[combination.index([[num1, col1], [num2, 0]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, col1], [num2, 0]])
                        elif col2 in the_color:
                            if [[num1, 0], [num2, col2]] in combination:
                                histogram[combination.index([[num1, 0], [num2, col2]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, 0], [num2, col2]])
                        else:
                            if [[num1, 0], [num2, 0]] in combination:
                                histogram[combination.index([[num1, 0], [num2, 0]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, 0], [num2, 0]])
                    else:
                        if [[num1, 0], [num2, 0]] in combination:
                            histogram[combination.index([[num1, 0], [num2, 0]])] += prob
                            continue
                        else:
                            histogram.append(prob)
                            combination.append([[num1, 0], [num2, 0]])#}}}
    histogram = [c/sum(histogram) for c in histogram]
    l = len(combination)
    fo_cache = [{} for i in xrange(l)]
    for i in xrange(l):
        fo_cache[i][0] = find_out(board+combination[i])
        for num3 in xrange(2, 15):
            fo_cache[i][num3] = {}
            for col3 in xrange(1, 5):
                fo_cache[i][num3][col3] = find_out(board+combination[i]+[[num3, col3]])
    small_table = [range(l) for i in xrange(l)]#{{{
    for i in xrange(l):
        for j in xrange(i, l):
            comb1 = copy.deepcopy(combination[i]) 
            comb2 = copy.deepcopy(combination[j])
            if comb1[0][1] == 0:
                for col in xrange(1, 5):
                    if [comb1[0][0], col] not in comb1+comb2+board:
                        comb1[0] = [comb1[0][0], col]
                        break
            if comb1[1][1] == 0:
                for col in xrange(1, 5):
                    if [comb1[1][0], col] not in comb1+comb2+board:
                        comb1[1] = [comb1[1][0], col]
                        break
            if comb2[0][1] == 0:
                for col in xrange(1, 5):
                    if [comb2[0][0], col] not in board+comb1+comb2:
                        comb2[0] = [comb2[0][0], col]
                        break
            if comb2[1][1] == 0:
                for col in xrange(1, 5):
                    if [comb2[1][0], col] not in board+comb1+comb2:
                        comb2[1] = [comb2[1][0], col]
                        break
            if has_same(comb1+comb2):
                small_table[i][j] = -1
                small_table[j][i] = -1
                continue
            if comb1[0][1] == 0 or comb1[1][1] == 0 or comb2[0][1] == 0 or comb2[1][1] == 0:
                small_table[i][j] = -1
                small_table[j][i] = -1
                continue
            fo0 = fo_cache[i][0]
            fo1 = fo_cache[j][0] 
            if fo0 < fo1:
                stronger = 1
            elif fo0 == fo1:
                stronger = -1
            else:
                stronger = 0
            a = [0, 0, 0] 
            for num3 in xrange(2, 15):
                for col3 in xrange(1, 5):
                    if [num3, col3] in board+comb1+comb2:
                        continue
                    fo10 = fo_cache[i][num3][col3] 
                    fo11 = fo_cache[j][num3][col3] 
                    if fo10 < fo11:
                        a[2] += 1
                    elif fo10 == fo11:
                        a[1] += 1
                    else:
                        a[0] += 1
            a = [1.0*hh/sum(a) for hh in a]
            small_table[i][j] = a[0] + 0.5*a[1]
            small_table[j][i] = a[2] + 0.5*a[1]#}}}
    less_big_table = tree()
    big_table = tree()
    super_big_table = tree()
    for num1 in xrange(2, 15):#{{{
        for col1 in xrange(1, 5):
            if has_same(board+[[num1, col1]]):
                continue
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    if has_same(board+[[num1, col1], [num2, col2]]):
                        continue
                    if [num1, col1] > [num2, col2]:
                        continue
                    the_color = color_make_different(board+[[num1, col1], [num2, col2]])
                    if the_color:
                        if col1 in the_color and col2 in the_color:
                            the_index = combination.index([[num1, col1], [num2, col2]])
                        elif col1 in the_color:
                            the_index = combination.index([[num1, col1], [num2, 0]]) 
                        elif col2 in the_color:
                            the_index = combination.index([[num1, 0], [num2, col2]]) 
                        else:
                            the_index = combination.index([[num1, 0], [num2, 0]]) 
                    else:
                        the_index = combination.index([[num1, 0], [num2, 0]])
                    wc = 0
                    s = 0
                    for i in xrange(l):
                        if small_table[the_index][i] == -1:
                            continue
                        card_i = combination[i]
                        super_big_table[num1][col1][num2][col2]\
                                [card_i[0][0]][card_i[0][1]][card_i[1][0]][card_i[1][1]]\
                                = small_table[the_index][i]
                        wc += histogram[i] * small_table[the_index][i]
                    less_big_table[combination[the_index][0][0]]\
                            [combination[the_index][0][1]]\
                            [combination[the_index][1][0]]\
                            [combination[the_index][1][1]]\
                            = wc
                    big_table[num1][col1][num2][col2] = wc#}}}
    return less_big_table, big_table, super_big_table#}}}

def get_win_chance_table_river(stats, board):
    combination = list()#{{{
    histogram = list()
    for num1 in xrange(2, 15):#{{{
        for col1 in xrange(1, 5):
            if has_same(board+[[num1, col1]]):
                continue
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    if has_same(board+[[num1, col1], [num2, col2]]):
                        continue
                    if [num1, col1] > [num2, col2]:
                        continue
                    the_color = color_make_different(board+[[num1, col1], [num2, col2]])
                    prob = stats[num1][col1][num2][col2]
                    if the_color:
                        if col1 in the_color and col2 in the_color:
                            if [[num1, col1], [num2, col2]] in combination:
                                histogram[combination.index([[num1, col1], [num2, col2]])] += prob
                                continue
                            else:
                                combination.append([[num1, col1], [num2, col2]])
                                histogram.append(prob)
                        elif col1 in the_color:
                            if [[num1, col1], [num2, 0]] in combination:
                                histogram[combination.index([[num1, col1], [num2, 0]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, col1], [num2, 0]])
                        elif col2 in the_color:
                            if [[num1, 0], [num2, col2]] in combination:
                                histogram[combination.index([[num1, 0], [num2, col2]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, 0], [num2, col2]])
                        else:
                            if [[num1, 0], [num2, 0]] in combination:
                                histogram[combination.index([[num1, 0], [num2, 0]])] += prob
                                continue
                            else:
                                histogram.append(prob)
                                combination.append([[num1, 0], [num2, 0]])
                    else:
                        if [[num1, 0], [num2, 0]] in combination:
                            histogram[combination.index([[num1, 0], [num2, 0]])] += prob
                            continue
                        else:
                            histogram.append(prob)
                            combination.append([[num1, 0], [num2, 0]])#}}}
    histogram = [c/sum(histogram) for c in histogram]
    l = len(combination)
    fo_cache = [{} for i in xrange(l)]
    for i in xrange(l):
        fo_cache[i][0] = find_out(board+combination[i])
        for num3 in xrange(2, 15):
            fo_cache[i][num3] = {}
            for col3 in xrange(1, 5):
                fo_cache[i][num3][col3] = find_out(board+combination[i]+[[num3, col3]])
    small_table = [range(l) for i in xrange(l)]#{{{
    for i in xrange(l):
        for j in xrange(i, l):
            comb1 = copy.deepcopy(combination[i]) 
            comb2 = copy.deepcopy(combination[j])
            if comb1[0][1] == 0:
                for col in xrange(1, 5):
                    if [comb1[0][0], col] not in comb1+comb2+board:
                        comb1[0] = [comb1[0][0], col]
                        break
            if comb1[1][1] == 0:
                for col in xrange(1, 5):
                    if [comb1[1][0], col] not in comb1+comb2+board:
                        comb1[1] = [comb1[1][0], col]
                        break
            if comb2[0][1] == 0:
                for col in xrange(1, 5):
                    if [comb2[0][0], col] not in board+comb1+comb2:
                        comb2[0] = [comb2[0][0], col]
                        break
            if comb2[1][1] == 0:
                for col in xrange(1, 5):
                    if [comb2[1][0], col] not in board+comb1+comb2:
                        comb2[1] = [comb2[1][0], col]
                        break
            if has_same(comb1+comb2):
                small_table[i][j] = -1
                small_table[j][i] = -1
                continue
            if comb1[0][1] == 0 or comb1[1][1] == 0 or comb2[0][1] == 0 or comb2[1][1] == 0:
                small_table[i][j] = -1
                small_table[j][i] = -1
                continue
            fo0 = fo_cache[i][0]
            fo1 = fo_cache[j][0] 
            if fo0 < fo1:
                small_table[i][j] = 0
                small_table[j][i] = 1
            elif fo0 == fo1:
                small_table[i][j] = 0.5
                small_table[j][i] = 0.5
            else:
                small_table[i][j] = 1
                small_table[j][i] = 0#}}}
    less_big_table = tree()
    big_table = tree()
    super_big_table = tree()
    for num1 in xrange(2, 15):#{{{
        for col1 in xrange(1, 5):
            if has_same(board+[[num1, col1]]):
                continue
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    if has_same(board+[[num1, col1], [num2, col2]]):
                        continue
                    if [num1, col1] > [num2, col2]:
                        continue
                    the_color = color_make_different(board+[[num1, col1], [num2, col2]])
                    if the_color:
                        if col1 in the_color and col2 in the_color:
                            the_index = combination.index([[num1, col1], [num2, col2]])
                        elif col1 in the_color:
                            the_index = combination.index([[num1, col1], [num2, 0]]) 
                        elif col2 in the_color:
                            the_index = combination.index([[num1, 0], [num2, col2]]) 
                        else:
                            the_index = combination.index([[num1, 0], [num2, 0]]) 
                    else:
                        the_index = combination.index([[num1, 0], [num2, 0]])
                    wc = 0
                    s = 0
                    for i in xrange(l):
                        if small_table[the_index][i] == -1:
                            continue
                        card_i = combination[i]
                        super_big_table[num1][col1][num2][col2]\
                                [card_i[0][0]][card_i[0][1]][card_i[1][0]][card_i[1][1]]\
                                = small_table[the_index][i]
                        wc += histogram[i] * small_table[the_index][i]
                    less_big_table[combination[the_index][0][0]]\
                            [combination[the_index][0][1]]\
                            [combination[the_index][1][0]]\
                            [combination[the_index][1][1]]\
                            = wc
                    big_table[num1][col1][num2][col2] = wc#}}}
    return less_big_table, big_table, super_big_table#}}}

def color_make_different(stage, cards):
    cols = [0, 0, 0, 0, 0]#{{{
    result = list()
    for c in cards:
        cols[c[1]] += 1
    for i in xrange(1, 5):
        if cols[i] >= 4 + (stage==3):
            result.append(i)
    return result#}}}

def has_same(cards):
    for i in xrange(len(cards)):#{{{
        for j in xrange(i+1, len(cards)):
            if cards[i] == cards[j] and cards[i][1] != 0:
                return True
    return False#}}}

def most_probable(stats, stats_change, n=100):
    all_combo = list()#{{{
    for num1, col1, num2, col2, prob in nodes_of_tree(stats, 4):
        if prob < 0.05:
            continue
        sc = stats_change[num1][col1][num2][col2]
        if not sc:
            sc = 0
        b = 0
        for i in xrange(1, 5):
            for j in xrange(1, 5):
                if [round(prob, 2), round(sc, 2), num1, i, num2, j] in all_combo:
                    b = 1
                    break
            if b:
                break
        if not b:
            all_combo.append([round(prob, 2), round(sc, 2), num1, col1, num2, col2])
    sorted_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
    return sorted_combo#print_stats(sorted_combo, n)#}}}

def map_card_string_to_tuple(card):
    result = [0, 0]#{{{
    color_map = {'s':1, 'h':2, 'c':3, 'd':4}
    number_map = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8,\
            '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
    result[1] = color_map[card[-1]]
    result[0] = number_map[card[:-1]]
    return result#}}}

def print_stats(sorted_combo, n):
    appeared = tree()#{{{
    filtered_combo = list()
    for combo in sorted_combo:
        mi = min([combo[1][0], combo[2][0]])
        ma = max([combo[1][0], combo[2][0]])
        if combo[1][1] == combo[2][1]:
            c1 = mi
            c2 = ma
        else:
            c1 = ma
            c2 = mi
        if appeared[c1][c2]:
            appeared[c1][c2] = max([appeared[c1][c2], round(combo[0], 2)])
        else:
            appeared[c1][c2] = round(combo[0], 2) 
    for c1 in appeared:
        for c2 in appeared[c1]:
            filtered_combo.append((appeared[c1][c2], c1, c2))
    filtered_combo = sorted(filtered_combo, key=lambda x:x[0], reverse=True)
    return filtered_combo[:n]#}}}

def del_stdout_line(n):
    CURSOR_UP_ONE = '\x1b[1A'#{{{
    ERASE_LINE = '\x1b[2K'
    for i in xrange(n):
        print CURSOR_UP_ONE+ERASE_LINE+CURSOR_UP_ONE
        #}}}

def change_terminal_color(color=''):
    color_map = {'black':'30', 'red':'31;1', 'green':'32;1', 'yellow;1':'33',\
            'blue':'34;1', 'magenta':'35;1', 'cyan':'36;1', 'white':'37;1', '':'0'}
    print '\x1b['+color_map[color]+'m'

def show_win_chance_table(win_chance_table, stats):
    all_combo = list()#{{{
    for n1 in stats:
        for c1 in stats[n1]:
            for n2 in stats[n1][c1]:
                for c2 in stats[n1][c1][n2]:
                    try:
                        all_combo.append([round(win_chance_table[n1][c1][n2][c2], 2),\
                                round(stats[n1][c1][n2][c2], 2), n1, c1, n2, c2])
                    except:
                        pass
    all_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
    p = len(all_combo) / 90
    j = len(all_combo) % 90
    for i in xrange(p):
        count = 0
        for combo in all_combo[i*90:i*90+90]:
            count += 1
            print combo, '  \t',
            if count % 3 == 0:
                print
        raw_input('---press any key for next page---')
        del_stdout_line(31)
    count = 0
    for combo in all_combo[-j:]:
        count += 1
        print combo, '\t',
        if count % 3 == 0:
            print
    raw_input('---press any key---')
    del_stdout_line(count/3+1)
    #}}}
    
def show_win_chance_table_for_me(win_chance_table_specific, win_chance_table, cards, stats):
    all_combo = list()#{{{
    ma = max(cards[:2])
    mi = min(cards[:2])
    win_chance_table_s = win_chance_table_specific[mi[0]][mi[1]][ma[0]][ma[1]]
    for n1 in stats:
        for c1 in stats[n1]:
            for n2 in stats[n1][c1]:
                for c2 in stats[n1][c1][n2]:
                    the_color = color_make_different([[n1, c1], [n2, c2]]+cards[2:])
                    if c1 in the_color and c2 in the_color:
                        cc1, cc2 = c1, c2
                    if c1 in the_color and c2 not in the_color:
                        cc1, cc2 = c1, 0
                    if c1 not in the_color and c2 in the_color:
                        cc1, cc2 = 0, c2
                    if c1 not in the_color and c2 not in the_color:
                        cc1, cc2 = 0, 0
                    all_combo.append([round(1-win_chance_table_s[n1][cc1][n2][cc2], 2),\
                            round(win_chance_table[n1][cc1][n2][cc2], 2),\
                            round(stats[n1][c1][n2][c2], 2), n1, c1, n2, c2])
    all_combo = sorted(all_combo, key=lambda x:x[2], reverse=True)
    p = len(all_combo) / 90
    j = len(all_combo) % 90
    for i in xrange(p):
        count = 0
        for combo in all_combo[i*90:i*90+90]:
            count += 1
            print combo, '  \t',
            if count % 3 == 0:
                print
        raw_input('---press any key for next page---')
        del_stdout_line(31)
    count = 0
    for combo in all_combo[-j:]:
        count += 1
        print combo, '\t',
        if count % 3 == 0:
            print
    raw_input('---press any key---')
    del_stdout_line(count/3+2)
    #}}}
    
def show_stats(stats, stats_change, i):
    change_terminal_color('cyan')
    all_combo = most_probable(stats[i], stats_change, 1000)#{{{
    p = len(all_combo) / 90
    j = len(all_combo) % 90
    for ii in xrange(p):
        count = 0
        for combo in all_combo[ii*90:ii*90+90]:
            count += 1
            print combo, '  \t',
            if count % 3 == 0:
                print
        raw_input('---press any key for next page---')
        del_stdout_line(31)
    count = 0
    for combo in all_combo[-j:]:
        count += 1
        print combo, '\t',
        if count % 3 == 0:
            print
    print 'Player:', i
    raw_input('---press any key---')
    del_stdout_line(count/3+4)
    #}}}
    change_terminal_color()

def move_last(active, button):
    i = 1#{{{
    while i <= button:
        if active[i] > 0:
            return 0 
        i += 1
    return 1#}}}

def how_much_can_value(wct, wct_s, stats_oppo, stats_me, cards, bet, after_action):
    prob_sum_me = 0#{{{
    if wct[cards[0][0]][cards[0][1]][cards[1][0]][cards[1][1]] > 0.8:
        after_action = 1
    else:
        after_action = 0
    for n1 in stats_me:
        for c1 in stats_me[n1]:
            for n2 in stats_me[n1][c1]:
                for c2 in stats_me[n1][c1][n2]:
                    prob_sum_me += stats_me[n1][c1][n2][c2]
    comb_list = list()
    for n1 in stats_me:
        for c1 in stats_me[n1]:
            for n2 in stats_me[n1][c1]:
                for c2 in stats_me[n1][c1][n2]:
                    comb_list.append([wct[n1][c1][n2][c2], n1, c1, n2, c2])
    comb_list = sorted(comb_list, key=lambda x:x[0], reverse=True)
    top_quarter_comb = list()
    second_quarter_comb = list()
    accumulation = 0
    switch = 0
    for comb in comb_list:
        if accumulation > prob_sum_me / 4:
            switch = 1
        if accumulation > prob_sum_me / 2:
            break
        if switch:
            second_quarter_comb.append(comb[1:])
        else:
            top_quarter_comb.append(comb[1:])
        accumulation += stats_me[comb[1]][comb[2]][comb[3]][comb[4]]
    value_expectation = 0
    total_prob = 0
    value_come_from = list()
    for n1 in wct:
        for c1 in wct[n1]:
            for n2 in wct[n1][c1]:
                for c2 in wct[n1][c1][n2]:
                    the_color = color_make_different([[n1,c1],[n2,c2]]+cards[2:])
                    if c1 not in the_color:
                        cc1 = 0
                    else:
                        cc1 = c1
                    if c2 not in the_color:
                        cc2 = 0
                    else:
                        cc2 = c2
                    his_win_chance = wct[n1][c1][n2][c2]
                    prob = stats_oppo[n1][c1][n2][c2]
                    total_prob += prob
                    fold_prob, call_prob, raise_prob = action_prob_according_to_win_chance(his_win_chance)
                    value = 0
                    try:
                        value += prob * fold_prob * wct_s[n1][cc1][n2][cc2] * bet
                        value += prob * call_prob * (wct_s[n1][cc1][n2][cc2]-0.5) * bet
                        if after_action:# My comb is good enough against raise
                            value += prob * raise_prob * (wct_s[n1][cc1][n2][cc2]-0.5) * (1+bet*2)
                        else:
                            value += - prob * raise_prob * (1-wct_s[n1][cc1][n2][cc2])\
                                    - prob * raise_prob * bet
                    except:
                        print n1,cc1,n2,cc2
                        raw_input('error')
                        continue
                    value_expectation += value
                    if not [value, prob, n1, cc1, n2, cc2] in value_come_from:
                        value_come_from.append([value, prob, n1, cc1, n2, cc2])
    value_come_from = sorted(value_come_from, key=lambda x:x[0], reverse=True)
    return value_expectation / total_prob, value_come_from

def action_prob_according_to_win_chance(wc):
    if wc > 0.5:
        fold_chance = 0
    elif wc < 0.1:
        fold_chance = 1
    else:
        fold_chance = 1 - 2.5 * (wc-0.1)
    if wc > 0.8:
        call_chance = 0.1
    elif wc < 0.1:
        call_chance = 0
    elif wc < 0.5:
        call_chance = 2.5 * (wc-0.1)
    else:
        call_chance = 0.1 + 3 * (0.8-wc)
    if wc < 0.5:
        raise_chance = 0
    elif wc > 0.8:
        raise_chance = 0.9
    else:
        raise_chance = 0.9 - 3 * (0.8-wc)
    return fold_chance, call_chance, raise_chance
