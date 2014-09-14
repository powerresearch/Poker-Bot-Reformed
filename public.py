import datetime
from collections import defaultdict
from copy import deepcopy

def tree():
    return defaultdict(tree)

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
    try:
        cards = list()#{{{
        original_number = defaultdict(int)
        color = defaultdict(int)
        for card in list_of_cards:
            original_number[card[0]] += 1
            color[card[1]] += 1
            cards.append(card[0])
        number = deepcopy(original_number)
        for key in number:
            result = [0, 0]
            if number[key] == 4:
                result[0] = key
                number[key] -= 4
                result[1] = max(number)
                return [7] + result + [0, 0, 0]
        number = deepcopy(original_number)
        for key in number:
            result = [0, 0]
            if number[key] == 3:
                result[0] = key
                number[key] -= 3
                for key2 in number:
                    if number[key2] >= 2:
                        if key2 > result[1]:
                            result[1] = key2 
                if result[1] > 0:
#                if cards[0] == key and cards[1] == key:
                    return [6] + result + [0, 0, 0]
#                if key in cards[:2]:
#                    return [3] + result
#                if key2 in cards[:2]:
#                    return [2] + result
#                return [0] + result
        number = deepcopy(original_number)
        for i in xrange(1, 5):
            if color[i] >= 5:
                result = [5]
                for card in sorted(list_of_cards, key=lambda x:x[0], reverse=True):
                    if card[1] == i:
                        result.append(card[0])
                        if len(result) == 6:
                            return result
        number = deepcopy(original_number)
        result = straight(number)
        for i in xrange(11):
            if result[i] == -1:
                return [4, i, 0, 0, 0, 0]
        number = deepcopy(original_number)
        for key in number:
            if number[key] == 3:
                number[key] -= 3
                kicker1 = max(number)
                number[kicker1] -= 1
                kicker2 = max(number)
#            if key in cards[:2]:
#                return [3, key, kicker1, kicker2, 0, 0]
#            else:
                return [3, key, kicker1, kicker2, 0, 0]
        number = deepcopy(original_number)
        pair1, pair2 = 0, 0
        for key in number:
            if number[key] == 2:
                if key > pair2:
                    pair2 = key
                    if pair2 > pair1:
                        pair2, pair1 = pair1, pair2
        if pair2 > 0:
            number[pair1] -= 2
            number[pair2] -= 2
            kicker = max(number)
#        if pair1 in cards[:2] and pair2 in cards[:2]:
#            return [2, pair1, pair2, kicker, 0, 0]
#        if pair1 in cards[:2] or pair2 in cards[:2]:
#            return [1, pair1, pair2, kicker, 0, 0]
            return [2, pair1, pair2, kicker, 0, 0]
        number = deepcopy(original_number)
        for key in number:
            if number[key] == 2:
                number[key] -= 2
                pair = key
                kicker1 = max(number)
                number[kicker1] -= 1
                kicker2 = max(number)
                number[kicker2] -= 1
                kicker3 = max(number)
#            if pair > max(cards[2:]):
#                return [1.5, pair, kicker1, kicker2, kicker3, 0]
#            if not pair in cards[:2]:
#                return [0, pair, kicker1, kicker2, kicker3, 0]
#            if cards[0] == pair and cards[1] > 10:
#                return [1.5, pair, kicker1, kicker2, kicker3, 0]
#            if cards[1] == pair and cards[0] > 10:
#                return [1.5, pair, kicker1, kicker2, kicker3, 0]
#            if pair in cards[:2]:
#                return [1, pair, kicker1, kicker2, kicker3, 0]
#            if pair < max(cards[2:]):
#                return [1, pair, kicker1, kicker2, kicker3, 0]
                return [1, pair, kicker1, kicker2, kicker3, 0]
        number = deepcopy(original_number)
        h1 = max(number)
        number[h1] -= 1
        h2 = max(number)
        number[h2] -= 1
        h3 = max(number)
        number[h3] -= 1
        h4 = max(number)
        number[h4] -= 1
        h5 = max(number)
#    if max(cards[:2]) > 11:
#        return [0.5, h1, h2, h3, h4, h5]
#    else:
        return [0, h1, h2, h3, h4, h5]#}}}
    except:
#       print list_of_cards
        pass

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
    cards = original_cards#{{{
    while not cards[-1]:
        cards = cards[:-1]
    for i in xrange(len(cards)):
        for j in xrange(len(cards)):
            if i == j: 
                continue
            else:
                if cards[i] == cards[j]:
                    return True
    return False#}}}

def how_much_can_beat(stats, hole_cards, public_cards, opponent):
    while not public_cards[-1]:#{{{
        public_cards = public_cards[:-1]
    win_chance = 0
    lose_chance = 0
    win_chance2 = 0
    lose_chance2 = 0
    fo0 = find_out(hole_cards+public_cards)
    for num1 in xrange(2, 15):
        for num2 in xrange(2, 15):
            for col1 in xrange(1, 5):
                for col2 in xrange(1, 5):
                    card1 = [num1, col1]
                    card2 = [num2, col2]
                    if card2 < card1:
                        continue
                    if has_same(hole_cards+public_cards+[card1, card2]):
                        continue
                    fo1 = find_out([card1, card2]+public_cards)
                    prob = stats[opponent][num1][col1][num2][col2]
                    if fo0 > fo1:
                        win_chance += prob
                        win_chance2 += 0.1
                    elif fo0 < fo1:
                        lose_chance += prob
                        lose_chance2 += 0.1
                    else:
                        win_chance2 += 0.05
                        lose_chance2 += 0.05
                        win_chance += prob * 0.5
                        lose_chance += prob * 0.5
    return min(win_chance / (win_chance+lose_chance), win_chance2 / (win_chance2+lose_chance2))#}}}

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
        return 9
    else:
        return 0#}}}

def how_many_outs(public_cards, hole_cards):
    while not public_cards[-1]:#{{{
        public_cards = public_cards[:-1]
    cards = public_cards + hole_cards
    fo = find_out(cards)
    outs = flush_outs(cards, fo) + straight_outs(cards, fo)
    pub_nums = list()
    fop = find_out(public_cards)
    for c in public_cards:
        pub_nums.append(c[0])
    n1, n2 = hole_cards[0][0], hole_cards[1][0]
    m = max(pub_nums)
    if fop[0] == 0:
        if fo >= [1, m]:
            return outs
        if n1 == n2:
            outs += 2
        else:
            if fo[0] == 0:
                if n1 > m:
                    outs += 3
                if n2 > m:
                    outs += 3
            elif fo[0] == 1 and fo[1] < max(pub_nums):
                outs += 5
    elif fop[0] == 1:
        if n1 == n2:
            outs += 2
    return outs#}}}

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
                    power_rank.append([card1, card2, fo, outs])
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
    for c1, c2, fo, outs in power_rank:
        can_beat_table[c1[0]][c1[1]][c2[0]][c2[1]] = prob
        try:
            prob += stats[opponent][c1[0]][c1[1]][c2[0]][c2[1]]
        except:
            print stats[opponent]
            raise Exception
    for c1, c2, fo, outs in power_rank:
        can_beat_table[c1[0]][c1[1]][c2[0]][c2[1]] /= prob
        outs_table[c1[0]][c1[1]][c2[0]][c2[1]] = outs
        can_beat_table[c1[0]][c1[1]][c2[0]][c2[1]] = max([can_beat_table[c1[0]][c1[1]][c2[0]][c2[1]],\
                outs*0.03*(3-stage)])
    for n1 in xrange(2, 15):
        for c1 in xrange(1, 5):
            for n2 in xrange(2, 15):
                for c2 in xrange(1, 5):
                    if can_beat_table[n1][c1][n2][c2]:
                        can_beat_table[n1][c1][n2][c2] = pow(can_beat_table[n1][c1][n2][c2], 0.5+no*0.5)
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
                    all_combo.append([prob, (num1, col1), (num2, col2)])
    sorted_combo = sorted(all_combo, key=lambda x:x[0], reverse=True)
    return print_stats(sorted_combo, n)#}}}

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
    for i in xrange(n):#{{{
        CURSOR_UP_ONE = '\x1b[1A'
        ERASE_LINE = '\x1b[2K'
        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)#}}}

def show_stats(stats, i):
    sorted_combo = most_probable(stats[i], 169)#{{{
    count = 0
    for combo in sorted_combo:
        count += 1
        print combo,'     \t',
        if count % 5 == 0:
            print
    print 'Player', i
    raw_input('---press any key---')
    del_stdout_line(35)
    print#}}}

def move_last(active, button):
    i = 1#{{{
    while i <= button:
        if active[i] > 0:
            return 0 
        i += 1
    return 1#}}}
