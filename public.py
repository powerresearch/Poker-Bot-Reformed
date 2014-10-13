import datetime
import time
import random
from collections import defaultdict
from copy import deepcopy
import random
import threading

def tree():
    return defaultdict(tree)

def rand_card():
    n = random.randint(2,14)#{{{
    c = random.randint(1,4)
    return [n, c]#}}}

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

def max(obj):
    if type(obj) == defaultdict:#{{{
        result = 0
        for k in obj:
            if obj[k] > 0 and k > result:
                result = k
        return result
    if type(obj) == list:
        result = -9999
        for i in obj:
            if i > result:
                result = i
        return result#}}}

def find_out(list_of_cards):
    while not list_of_cards[-1]:#{{{
        list_of_cards = list_of_cards[:-1]
    nums = list()
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
            
def mc_range_fight(comb1, comb2, board):
    t1 = time.clock()#{{{
    a = [0, 0, 0]
    for i in xrange(500):
        new_board = []+board
        for j in xrange(5-len(board)):
            new_board.append(rand_card())
        if has_same(new_board+comb1+comb2):
            continue
        fo0 = find_out(new_board+comb1)
        fo1 = find_out(new_board+comb2)
        if fo0 < fo1:
            a[0] += 1
        elif fo0 == fo1:
            a[1] += 1
        else:
            a[2] += 1
    a = [1.0*c/sum(a) for c in a]
    print a
    print time.clock()-t1#}}}

def get_win_chance_table(stats, board):
    while not board[-1]:
        board = board[:-1]
    if len(board) == 3:
        return get_win_chance_table_flop(stats, board)
    if len(board) == 4:
        return get_win_chance_table_turn(stats, board)
    if len(board) == 5:
        return get_win_chance_table_river(stats, board)

def get_win_chance_table_flop(stats, board):
    combination = list()#{{{
    histogram = list()
    while not board[-1]:
        board = board[:-1]
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
                        if col1 == the_color and col2 == the_color:
                            if [[num1, col1], [num2, col2]] in combination:
                                histogram[combination.index([[num1, col1], [num2, col2]])] += 1
                                continue
                            else:
                                combination.append([[num1, col1], [num2, col2]])
                                histogram.append(1)
                        elif col1 == the_color:
                            if [[num1, col1], [num2, 0]] in combination:
                                histogram[combination.index([[num1, col1], [num2, 0]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, col1], [num2, 0]])
                        elif col2 == the_color:
                            if [[num1, 0], [num2, col2]] in combination:
                                histogram[combination.index([[num1, 0], [num2, col2]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, 0], [num2, col2]])
                        else:
                            if [[num1, 0], [num2, 0]] in combination:
                                histogram[combination.index([[num1, 0], [num2, 0]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, 0], [num2, 0]])
                    else:
                        if [[num1, 0], [num2, 0]] in combination:
                            histogram[combination.index([[num1, 0], [num2, 0]])] += 1
                            continue
                        else:
                            histogram.append(1)
                            combination.append([[num1, 0], [num2, 0]])#}}}
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
        for j in xrange(i+1, l):
            comb1 = combination[i]
            comb2 = combination[j]
            if has_same(comb1+comb2):
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
    big_table = tree()
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
                        if col1 == the_color and col2 == the_color:
                            the_index = combination.index([[num1, col1], [num2, col2]])
                        elif col1 == the_color:
                            the_index = combination.index([[num1, col1], [num2, 0]]) 
                        elif col2 == the_color:
                            the_index = combination.index([[num1, 0], [num2, col2]]) 
                        else:
                            the_index = combination.index([[num1, 0], [num2, 0]]) 
                    else:
                        the_index = combination.index([[num1, 0], [num2, 0]])
                    wc = 0
                    s = 0
                    for i in xrange(l):
                        if the_index == i:
                            continue
                        if small_table[the_index][i] == -1:
                            continue
                        wc += histogram[i] * small_table[the_index][i]
                        s += histogram[i]
                    wc /= s
                    big_table[num1][col1][num2][col2] = wc#}}}
    return big_table#}}}

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
                    if the_color:
                        if col1 == the_color and col2 == the_color:
                            if [[num1, col1], [num2, col2]] in combination:
                                histogram[combination.index([[num1, col1], [num2, col2]])] += 1
                                continue
                            else:
                                combination.append([[num1, col1], [num2, col2]])
                                histogram.append(1)
                        elif col1 == the_color:
                            if [[num1, col1], [num2, 0]] in combination:
                                histogram[combination.index([[num1, col1], [num2, 0]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, col1], [num2, 0]])
                        elif col2 == the_color:
                            if [[num1, 0], [num2, col2]] in combination:
                                histogram[combination.index([[num1, 0], [num2, col2]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, 0], [num2, col2]])
                        else:
                            if [[num1, 0], [num2, 0]] in combination:
                                histogram[combination.index([[num1, 0], [num2, 0]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, 0], [num2, 0]])
                    else:
                        if [[num1, 0], [num2, 0]] in combination:
                            histogram[combination.index([[num1, 0], [num2, 0]])] += 1
                            continue
                        else:
                            histogram.append(1)
                            combination.append([[num1, 0], [num2, 0]])#}}}
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
        for j in xrange(i+1, l):
            comb1 = combination[i]
            comb2 = combination[j]
            if has_same(comb1+comb2):
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
            small_table[j][i] = a[2] + 0.5*a[2]#}}}
    big_table = tree()
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
                        if col1 == the_color and col2 == the_color:
                            the_index = combination.index([[num1, col1], [num2, col2]])
                        elif col1 == the_color:
                            the_index = combination.index([[num1, col1], [num2, 0]]) 
                        elif col2 == the_color:
                            the_index = combination.index([[num1, 0], [num2, col2]]) 
                        else:
                            the_index = combination.index([[num1, 0], [num2, 0]]) 
                    else:
                        the_index = combination.index([[num1, 0], [num2, 0]])
                    wc = 0
                    s = 0
                    for i in xrange(l):
                        if the_index == i:
                            continue
                        if small_table[the_index][i] == -1:
                            continue
                        wc += histogram[i] * small_table[the_index][i]
                        s += histogram[i]
                    wc /= s
                    big_table[num1][col1][num2][col2] = wc#}}}
    return big_table#}}}

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
                    if the_color:
                        if col1 == the_color and col2 == the_color:
                            if [[num1, col1], [num2, col2]] in combination:
                                histogram[combination.index([[num1, col1], [num2, col2]])] += 1
                                continue
                            else:
                                combination.append([[num1, col1], [num2, col2]])
                                histogram.append(1)
                        elif col1 == the_color:
                            if [[num1, col1], [num2, 0]] in combination:
                                histogram[combination.index([[num1, col1], [num2, 0]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, col1], [num2, 0]])
                        elif col2 == the_color:
                            if [[num1, 0], [num2, col2]] in combination:
                                histogram[combination.index([[num1, 0], [num2, col2]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, 0], [num2, col2]])
                        else:
                            if [[num1, 0], [num2, 0]] in combination:
                                histogram[combination.index([[num1, 0], [num2, 0]])] += 1
                                continue
                            else:
                                histogram.append(1)
                                combination.append([[num1, 0], [num2, 0]])
                    else:
                        if [[num1, 0], [num2, 0]] in combination:
                            histogram[combination.index([[num1, 0], [num2, 0]])] += 1
                            continue
                        else:
                            histogram.append(1)
                            combination.append([[num1, 0], [num2, 0]])#}}}
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
        for j in xrange(i+1, l):
            comb1 = combination[i]
            comb2 = combination[j]
            if has_same(comb1+comb2):
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
    big_table = tree()
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
                        if col1 == the_color and col2 == the_color:
                            the_index = combination.index([[num1, col1], [num2, col2]])
                        elif col1 == the_color:
                            the_index = combination.index([[num1, col1], [num2, 0]]) 
                        elif col2 == the_color:
                            the_index = combination.index([[num1, 0], [num2, col2]]) 
                        else:
                            the_index = combination.index([[num1, 0], [num2, 0]]) 
                    else:
                        the_index = combination.index([[num1, 0], [num2, 0]])
                    wc = 0
                    s = 0
                    for i in xrange(l):
                        if the_index == i:
                            continue
                        if small_table[the_index][i] == -1:
                            continue
                        wc += histogram[i] * small_table[the_index][i]
                        s += histogram[i]
                    wc /= s
                    big_table[num1][col1][num2][col2] = wc#}}}
    return big_table#}}}

def color_make_different(cards):
    cols = [0, 0, 0, 0, 0]#{{{
    for c in cards:
        cols[c[1]] += 1
    for i in xrange(1, 5):
        if cols[i] >= 4:
            return i
    return 0#}}}

def straight(ddict):
    result = [0,0,0,0,0,0,0,0,0,0,0]#{{{
    for i in xrange(2, 11):
        lack = list()
        for j in xrange(5):
            if ddict[i+j]:
                continue
            else:
                lack.append(i+j)
        if len(lack) == 0:
            result[i] = -1
        if len(lack) == 1:
            result[i] = lack[0]
    lack = list()
    if not ddict[14]:
        lack.append(14)
    for j in xrange(2, 6):
        if not ddict[j]:
            lack.append(j)
    if len(lack) == 0:
        result[1] = -1
    if len(lack) == 1:
        result[1] = lack[0]
    return result#}}}

def has_same(original_cards):
    while not original_cards[-1]:
        original_cards = original_cards[:-1]
    cards = original_cards#{{{
    for i in xrange(len(cards)):
        for j in xrange(i+1, len(cards)):
            if cards[i] == cards[j] and cards[i][1] != 0:
                return True
    return False#}}}

def how_much_can_beat(stats, power_rank, hole_cards, opponent):
    win_chance = 0#{{{
    lose_chance = 0
    win_chance2 = 0
    lose_chance2 = 0
    winning = 1
    max_stats_prob = 0
    for c1, c2, fo, outs, outs_in_specific in power_rank:
        max_stats_prob = max([max_stats_prob, stats[opponent][c1[0]][c1[1]][c2[0]][c2[1]]])
        if [c1, c2] == hole_cards or [c2, c1] == hole_cards:
            the_fo = fo
    for tup in power_rank:
        card1 = tup[0]
        card2 = tup[1]
        fo = tup[2]
        num1, col1 = card1[0], card1[1]
        num2, col2 = card2[0], card2[1]
        prob = stats[opponent][num1][col1][num2][col2]
        if prob < 0.1 * max_stats_prob:
            continue
        if the_fo >= fo:
            win_chance += prob
            win_chance2 += 0.1
        else:
            lose_chance += prob
            lose_chance2 += 0.1
    return win_chance / (win_chance+lose_chance)#, win_chance2 / (win_chance2+lose_chance2))#}}}

def straight_outs(cards, fo):
    if fo[0] >= 4:#{{{
        return 0
    nums = set()
    outs = set()
    for c in cards:
        nums.add(c[0])
    if 14 in nums:
        nums.add(1)
    nums = sorted(nums)
    for num in nums[:-3]:
        if num+1 in nums and num+2 in nums and num+3 in nums:
            if num == 1:
                outs.add(5)
            elif num == 11:
                outs.add(10)
            else:
                outs.add(num-1)
                outs.add(num+4)
            continue
        if num+1 in nums and num+2 in nums and num+4 in nums:
            outs.add(num+3)
            continue
        if num+1 in nums and num+3 in nums and num+4 in nums:
            outs.add(num+2)
            continue
        if num+2 in nums and num+3 in nums and num+4 in nums:
            outs.add(num+1)
    return len(outs)*4#}}}

def flush_outs(cards, fo):
    if fo[0] >= 5:#{{{
        return 0
    col = [0, 0, 0, 0, 0]
    for c in cards:
        col[c[1]] += 1
    if max(col) == 4:
        if cards[0][1] == cards[1][1] and col[cards[0][1]] == 4:
            return 9
        if cards[0][0] >= 12 and col[cards[0][1]] == 4:
            return 9
        if cards[1][0] >= 12 and col[cards[1][1]] == 4:
            return 9
        return 0
    else:
        return 0#}}}

def naive_flush_outs(cards):
    col = [0, 0, 0, 0, 0]#{{{
    for c in cards:
        col[c[1]] += 1
    if max(col) == 4:
        return 9
    else:
        return 0#}}}

def how_many_outs(public_cards, hole_cards):
    while not public_cards[-1]:#{{{
        public_cards = public_cards[:-1]
    highcard, twop, trip, straight, flush, fuhos = 0, 0, 0, 0, 0, 0
    cards = hole_cards + public_cards
    fo = find_out(cards)
    flush = flush_outs(cards, fo)
    straight = straight_outs(cards, fo)
    pub_nums = list()
    fop = find_out(public_cards)
    for c in public_cards:
        pub_nums.append(c[0])
    n1, n2 = hole_cards[0][0], hole_cards[1][0]
    m = max(pub_nums)
    if fo[0] == 3 and hole_cards[0][0] == hole_cards[1][0]:
        fuhos = 1 + (len(public_cards)-1)*3
    if fo[0] == 2 and hole_cards[0][0] in fo[1:3] and hole_cards[1][0] in fo[1:3]:
        fuhos = 4
    if fop[0] == 0:
        if n1 == n2:
            trip += 2
        else:
            if fo[0] == 0:
                if n1 > m:
                    highcard += 2# High card is not good outs
                if n2 > m:
                    highcard += 2# High card is not good outs
            elif fo[0] == 1 and fo[1] < max(pub_nums):
                trip += 2
                twop += 3
    elif fop[0] == 1:
        if n1 == n2:
            trip += 2
    if flush_outs(public_cards, fop) > 0:
        highcard, twop, trip, straight = 0, 0, 0, 0
    if straight_outs(public_cards, fop) > 0:
        highcard, twop, trip = 0, 0, 0
    return highcard+twop+trip+straight+flush+fuhos, highcard, twop, trip, straight, flush, fuhos#}}}

def get_power_rank(cards):
    power_rank = list()#{{{
    for num1 in xrange(2, 15):
        for col1 in xrange(1, 5):
            for num2 in xrange(2, 15):
                for col2 in xrange(1, 5):
                    card1 = [num1, col1]
                    card2 = [num2, col2]
                    if has_same(cards+[card1, card2]):
                        continue
                    if card1 > card2:
                        continue
                    fo = find_out(cards+[card1, card2])
                    outs = how_many_outs(cards, [card1, card2])
                    power_rank.append([card1, card2, fo, outs[0], outs[1:]])
    power_rank = sorted(power_rank, key=lambda x:x[2])
    return power_rank#}}}

def get_can_beat_table(stage, power_rank, stats, opponent, active):
    no = 0#{{{
    for item in active:
        if item:
            no += 1
    no -= 1
    can_beat_table = tree()
    outs_table = tree()
    prob = 0
    for c1, c2, fo, outs, outs_in_specific in power_rank:
        can_beat_table[c1[0]][c1[1]][c2[0]][c2[1]] = prob
        try:
            prob += stats[opponent][c1[0]][c1[1]][c2[0]][c2[1]]
        except:
            print stats[opponent]
            raise Exception
    for c1, c2, fo, outs, outs_in_specific in power_rank:
        can_beat_table[c1[0]][c1[1]][c2[0]][c2[1]] /= prob
        outs_table[c1[0]][c1[1]][c2[0]][c2[1]] = outs
    for n1 in xrange(2, 15):
        for c1 in xrange(1, 5):
            for n2 in xrange(2, 15):
                for c2 in xrange(1, 5):
                    if can_beat_table[n1][c1][n2][c2]:
                        outs = outs_table[n1][c1][n2][c2]
                        can_beat_table[n1][c1][n2][c2] = pow(can_beat_table[n1][c1][n2][c2], 0.5+no*0.5)
                        can_beat_table[n1][c1][n2][c2] = min(1, \
                                max([can_beat_table[n1][c1][n2][c2], outs*0.04*(3-stage)]))
    return can_beat_table, outs_table#}}}

def range_fight(power_rank, stat1, stat2):
    s1 = 0#{{{
    s2 = 0
    winning_chance = 0
#    for num1 in xrange(2, 15):
#        for col1 in xrange(1, 5):
#            for num2 in xrange(2, 15):
#                for col2 in xrange(1, 5):
#                    if [num1, col1] > [num2, col2]:
#                        continue
#                    if num1 == num2 and col1 == col2:
#                        continue
#                    z1 += stat1[num1][col1][num2][col2]
#                    z2 += stat2[num1][col1][num2][col2]
    for combo in power_rank:
        card1, card2 = combo[0], combo[1]
        winning_chance += s2 * stat1[card1[0]][card1[1]][card2[0]][card2[1]]
        winning_chance += 0.5 * stat1[card1[0]][card1[1]][card2[0]][card2[1]] \
                            * stat2[card1[0]][card1[1]][card2[0]][card2[1]]
        s2 += stat2[card1[0]][card1[1]][card2[0]][card2[1]]
        s1 += stat1[card1[0]][card1[1]][card2[0]][card2[1]]    
    winning_chance = winning_chance / s1 / s2
    return winning_chance#}}}

def most_probable(stats, n=100):
    all_combo = list()#{{{
    for num1 in stats:
        for col1 in stats[num1]:
            for num2 in stats[num1][col1]:
                for col2 in stats[num1][col1][num2]:
                    if [num1, col1] < [num2, col2]:
                        continue
                    prob = stats[num1][col1][num2][col2]
                    b = 0
                    for i in xrange(1, 5):
                        for j in xrange(1, 5):
                            if [round(prob, 2), num1, i, num2, j] in all_combo:
                                b = 1
                                break
                        if b:
                            break
                    if not b:
                        all_combo.append([round(prob, 2), num1, col1, num2, col2])
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

def show_can_beat_table(can_beat_table, outs_table):
    all_combo = list()#{{{
    for n1 in can_beat_table:
        for c1 in can_beat_table[n1]:
            for n2 in can_beat_table[n1][c1]:
                for c2 in can_beat_table[n1][c1][n2]:
                    if can_beat_table[n1][c1][n2][c2]:
                        b = 0
                        for i in xrange(1, 5):
                            for j in xrange(1, 5):
                                if can_beat_table[n1][i][n2][j]:
                                    if [round(can_beat_table[n1][c1][n2][c2], 2), n1, i, n2, j] in all_combo:
                                        b = 1
                                        break
                            if b:
                                break
                        if not b:
                            all_combo.append([round(can_beat_table[n1][c1][n2][c2], 2),\
                                    n1, c1, n2, c2])
    all_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
    p = len(all_combo) / 150
    j = len(all_combo) % 150
    for i in xrange(p):
        count = 0
        for combo in all_combo[i*150:i*150+150]:
            count += 1
            print combo, '\t',
            if count % 5 == 0:
                print
        raw_input('---press any key for next page---')
        del_stdout_line(31)
    count = 0
    for combo in all_combo[-j:]:
        count += 1
        print combo, '\t',
        if count % 5 == 0:
            print
    raw_input('---press any key---')
    del_stdout_line(count/5+2)
    #}}}
    
def show_win_chance_table(can_beat_table):
    all_combo = list()#{{{
    for n1 in can_beat_table:
        for c1 in can_beat_table[n1]:
            for n2 in can_beat_table[n1][c1]:
                for c2 in can_beat_table[n1][c1][n2]:
                    all_combo.append([round(can_beat_table[n1][c1][n2][c2], 2),\
                            n1, c1, n2, c2])
    all_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
    p = len(all_combo) / 150
    j = len(all_combo) % 150
    for i in xrange(p):
        count = 0
        for combo in all_combo[i*150:i*150+150]:
            count += 1
            print combo, '\t',
            if count % 5 == 0:
                print
        raw_input('---press any key for next page---')
        del_stdout_line(31)
    count = 0
    for combo in all_combo[-j:]:
        count += 1
        print combo, '\t',
        if count % 5 == 0:
            print
    raw_input('---press any key---')
    del_stdout_line(count/5+2)
    #}}}
    
def show_stats(stats, i):
    all_combo = most_probable(stats[i], 169)#{{{
    p = len(all_combo) / 150
    j = len(all_combo) % 150
    for ii in xrange(p):
        count = 0
        for combo in all_combo[ii*150:ii*150+150]:
            count += 1
            print combo, '\t',
            if count % 5 == 0:
                print
        raw_input('---press any key for next page---')
        del_stdout_line(31)
    count = 0
    for combo in all_combo[-j:]:
        count += 1
        print combo, '\t',
        if count % 5 == 0:
            print
    print 'Player:', i
    raw_input('---press any key---')
    del_stdout_line(count/5+2)
    #}}}

def move_last(active, button):
    i = 1#{{{
    while i <= button:
        if active[i] > 0:
            return 0 
        i += 1
    return 1#}}}

def get_avg_stats(stats, active):
    avg_stats = deepcopy(stats[0])#{{{
    active_index = list()
    for i in xrange(1, 6):
        if active[i] == 1:
            active_index.append(i)
    if len(active_index) == 0:
        return stats[0]
    for n1 in avg_stats:
        for c1 in avg_stats[n1]:
            for n2 in avg_stats[n1][c1]:
                for c2 in avg_stats[n1][c1][n2]:
#                    print n1,c1,n2,c2
#                    print 'aaa',stats[0][n1][c1][n2][c2]
#                    print 'aaa',stats[2][n1][c1][n2][c2]
#                    print 'aaa',stats[4][n1][c1][n2][c2]
                    avg_stats[n1][c1][n2][c2] = 0
                    for i in active_index:
#                        print n1,c1,n2,c2,i
                        avg_stats[n1][c1][n2][c2] += stats[i][n1][c1][n2][c2]
                    avg_stats[n1][c1][n2][c2] /= len(active_index)
    return avg_stats#}}}

def random_cards(n):
    result = list()#{{{
    for i in xrange(n):
        result.append([random.randint(2, 15), random.randint(1,5)])
    return result#}}}

def get_board_wetness(stats, power_rank, active, cards):
    max_stats_prob = 0#{{{
    total_prob = 0
    while not cards[-1]:
        cards = cards[:-1]
    fo = find_out(cards)
    avg_stats = get_avg_stats(stats, active)
    likely_outs, real_outs = 0, 0
    for c1, c2, fot, outs, outs_in_specific in power_rank:
        max_stats_prob = max([max_stats_prob, avg_stats[c1[0]][c1[1]][c2[0]][c2[1]]])
    for tup in power_rank:
        card1 = tup[0]
        card2 = tup[1]
        num1, col1 = card1[0], card1[1]
        num2, col2 = card2[0], card2[1]
        prob = avg_stats[num1][col1][num2][col2]
        if prob < 0.1 * max_stats_prob:
            continue
        total_prob += prob
        likely_outs += prob * tup[3]
        if fo[0] <= 1 and fo[1] < 14:
            real_outs += prob * tup[3]
        elif fo[0] == 1 and fo[1] == 14:
            real_outs += prob * sum(tup[4][1:])
        elif fo[0] == 2:
            real_outs += prob * sum(tup[4][1:])
        elif fo[0] == 3:
            real_outs += prob * sum(tup[4][2:])
        elif fo[0] == 4:
            real_outs += prob * sum(tup[4][3:])
        elif fo[0] == 5:
            the_color = [0,0,0,0,0]
            for c in cards:
                the_color[c[1]] += 1
            for i in xrange(1,5):
                if the_color[i] > 4:
                    the_color = i
                    break
            my_top = 0
            if cards[0][1] == the_color:
                my_top = max([my_top, cards[0][0]])
            if cards[1][1] == the_color:
                my_top = max([my_top, cards[1][0]])
            how_many_big_vacant = 0
            for i in xrange(my_top+1, 15):
                if not i in fo[1:]:
                    how_many_big_vacant += 1
            if how_many_big_vacant > 1:
                real_outs += prob * sum(tup[4][4:])
            else:
                real_outs += prob * sum(tup[4][5:])
        else:
            pass
    likely_outs /= total_prob
    real_outs /= total_prob
    return likely_outs, real_outs#}}} 

def get_fold_chance(stats, power_rank, cards):
    total_prob = 0#{{{
    fold_prob = 0
    for c1, c2, fot, outs, outs_in_specific in power_rank:
        prob = stats[c1[0]][c1[1]][c2[0]][c2[1]]
        if fot[0] == 0 and outs < 8:
            total_prob += prob
            fold_prob += prob
        else:
            total_prob += prob
    return fold_prob / total_prob#}}}

def can_value(cards):
    if find_out(cards)[0] > 3:#{{{
        return True
    if find_out(cards)[0] == 1:
        if find_out(cards)[1] == max(cards)[0] and max(cards)[0] in [cards[0][0], cards[1][0]]:
            return True
    if find_out(cards)[0] == 2:
        if find_out(cards)[1] in [cards[0][0], cards[1][0]]\
                or find_out(cards)[1] in [cards[0][0], cards[1][0]]:
            return True
    if find_out(cards)[0] == 3:
        if find_out(cards)[1] in [cards[0][0], cards[1][0]]:
            return True
    return False#}}}

def get_board_texture(stats, power_rank, active, cards):
    max_stats_prob = 0#{{{
    total_prob = 0
    high_card_feature = 0
    one_pair_feature = 0
    top_pair_feature = 0
    over_pair_feature = 0
    fake_two_pair_feature = 0
    real_two_pair_feature = 0
    trip_feature = 0
    set_feature = 0
    straight_feature = 0
    flush_feature = 0
    straight_outs_feature = 0
    flush_outs_feature = 0
    full_house_feature = 0
    while not cards[-1]:
        cards = cards[:-1]
    avg_stats = get_avg_stats(stats, active)
    for c1, c2, fo, outs, outs_in_specific in power_rank:
        max_stats_prob = max([max_stats_prob, avg_stats[c1[0]][c1[1]][c2[0]][c2[1]]])
    for tup in power_rank:
        card1 = tup[0]
        card2 = tup[1]
        num1, col1 = card1[0], card1[1]
        num2, col2 = card2[0], card2[1]
        fo = tup[2]
        prob = avg_stats[num1][col1][num2][col2]
        if prob < 0.1 * max_stats_prob:
            continue
        if cards[0][0] > max(cards[2:])[0]:
            high_card_feature += prob
        if cards[1][0] > max(cards[2:])[0]:
            high_card_feature += prob
        if fo[0] == 1 and fo[1] in [cards[0][0], cards[1][0]] and fo[1] < max(cards[2:])[0]:
            one_pair_feature += prob
        if fo[0] == 1 and fo[1] in [cards[0][0], cards[1][0]] and fo[1] == max(cards[2:])[0]:
            top_pair_feature += prob
        if fo[0] == 1 and fo[1] > max(cards[2:])[0]:
            over_pair_feature += prob
        if fo[0] == 2:
            if fo[1] in [cards[0][0], cards[1][0]] and fo[2] in [cards[0][0], cards[1][0]]:
                real_two_pair_feature += prob
            else:
                fake_two_pair_feature += prob
        if fo[0] == 3:
            if fo[1] == cards[0][0] and fo[1] == cards[1][0]:
                set_feature += prob
            else:
                trip_feature += prob
        if fo[0] == 4:
            straight_feature += prob
        if fo[0] == 5:
            flush_feature += prob
        if fo[0] == 6:
            full_house_feature += prob
        flush_outs_feature += naive_flush_outs(cards[2:]+[card1, card2]) * prob
        straight_outs_feature += straight_outs(cards[2:]+[card1, card2], [0]) * prob
        total_prob += prob
    high_card_feature /= total_prob
    one_pair_feature /= total_prob
    top_pair_feature /= total_prob
    over_pair_feature /= total_prob
    fake_two_pair_feature /= total_prob
    real_two_pair_feature /= total_prob
    trip_feature /= total_prob
    set_feature /= total_prob
    straight_feature /= total_prob
    flush_feature /= total_prob
    straight_outs_feature /= total_prob
    flush_outs_feature /= total_prob
    full_house_feature /= total_prob
    return [high_card_feature, one_pair_feature, top_pair_feature, over_pair_feature,
            fake_two_pair_feature, real_two_pair_feature, trip_feature, set_feature,
            straight_feature, flush_feature, straight_outs_feature, flush_outs_feature,
            full_house_feature]#}}} 

def what_do_i_have(cards):
    while not cards[-1]:#{{{
        cards = cards[:-1]
    fo = find_out(cards)
    if cards[0] < cards[1]:
        tmp = cards[0]
        cards[0] = cards[1]
        cards[1] = tmp
    if cards[0][0] > max(cards[2:])[0]:
        high_card_feature0 = 1.0*cards[0][0] / 14 
    else:
        high_card_feature0 = -1
    if cards[1][0] > max(cards[2:])[0]:
        high_card_feature1 = 1.0*cards[1][0] / 14
    else:
        high_card_feature1 = -1
    high_card_feature = [high_card_feature0, high_card_feature1]
    if fo[0] == 1 and fo[1] in [cards[0][0], cards[1][0]] and fo[1] < max(cards[2:])[0]:
        one_pair_feature = 1.0*fo[1] / 14
    else:
        one_pair_feature = -1
    if fo[0] == 1 and fo[1] == cards[0][0]:
        top_pair_feature = 1.0*cards[1][0] / 14
    elif fo[0] == 1 and fo[1] == cards[1][0]:
        top_pair_feature = 1.0*cards[0][0] / 14
    else:
        top_pair_feature = -1
    if fo[0] == 1 and fo[1] > max(cards[2:])[0]:
        over_pair_feature = 1.0*fo[1] / 14
    else:
        over_pair_feature = -1
    fake_two_pair_feature = -1 
    real_two_pair_feature = -1
    if fo[0] == 2:
        if fo[1] in [cards[0][0], cards[1][0]] and fo[2] in [cards[0][0], cards[1][0]]:
            hat = 0
            for c in cards[2:]:
                if cards[0][0] < c[0]:
                    hat += 1
            real_two_pair_feature = 1.0*(len(cards)-2-hat) / (len(cards)-2)
        else:
            if fo[1] == cards[0][0] or fo[2] == cards[0][0]:
                hat = 0
                for c in cards[2:]:
                    if cards[0][0] < c[0]:
                        hat += 1
                fake_two_pair_feature = 1.0*(len(cards)-2-hat) / (len(cards)-2)
            elif fo[1] == cards[1][0] or fo[2] == cards[1][0]:
                hat = 0
                for c in cards[2:]:
                    if cards[1][0] < c[0]:
                        hat += 1
                fake_two_pair_feature = 1.0*(len(cards)-2-hat) / (len(cards)-2)
    set_feature = -1
    trip_feature = -1
    if fo[0] == 3:
        if fo[1] == cards[0][0] and fo[1] == cards[1][0]:
            set_feature = 1
        else:
            if cards[0][0] == fo[1]:
                trip_feature = 1.0*cards[1][0] / 14
            elif cards[1][0] == fo[1]:
                trip_feature = 1.0*cards[0][0] / 14
    if fo[0] == 4:
        no_use_card = 0
        free_card = 0
        if cards[0][0] in [c[0] for c in cards[2:]]:
            no_use_card += 1
        if cards[1][0] in [c[0] for c in cards[2:]]:
            no_use_card += 1
        if cards[0][0] == cards[1][0]:
            no_use_card += 1
        if not fo[1] in [c[0] for c in cards[2:]]:
            free_card += 1
            if not fo[1]+1 in [c[0] for c in cards[2:]]:
                free_card += 1
        straight_feature = 1.0*(2-no_use_card-free_card)/2
    else:
        straight_feature = -1
    if fo[0] == 5:
        color = [0,0,0,0,0]
        for c in cards:
            color[c[1]] += 1
        my_top = 0
        hat = 0
        if color[cards[0][1]] >= 5:
            my_top = cards[0][0]
        elif color[cards[1][1]] >= 5:
            my_top = cards[1][0]
        for i in xrange(my_top+1, 15):
            if not i in fo[1:]:
                hat += 1
        flush_feature = 1.0*(8-hat) / 8
    else:
        flush_feature = -1
    if fo[0] >= 6:
        full_house_feature = 1
    else:
        full_house_feature = -1
    straight_outs_feature = 1.0*straight_outs(cards, [0]) / 8
    if not straight_outs_feature:
        straight_outs_feature = -1
    if flush_outs(cards, fo) > 0:
        color = [0,0,0,0,0]
        for c in cards:
            color[c[1]] += 1
        my_top = 0
        hat = 0
        if color[cards[0][1]] >= 4:
            my_top = cards[0][0]
        elif color[cards[1][1]] >= 4:
            my_top = cards[1][0]
        for i in xrange(my_top+1, 15):
            if not i in fo[1:]:
                hat += 1
        flush_outs_feature = 1.0*(8-hat) / 8
    else:
        flush_outs_feature = -1
    return high_card_feature + [one_pair_feature, top_pair_feature, over_pair_feature,
            fake_two_pair_feature, real_two_pair_feature, trip_feature, set_feature,
            straight_feature, flush_feature, straight_outs_feature, flush_outs_feature,
            full_house_feature]#}}} 
