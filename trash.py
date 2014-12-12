from collections import defaultdict

def rand_card():
    n = random.randint(2,14)#{{{
    c = random.randint(1,4)
    return [n, c]#}}}

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

def straight_outs(cards):
    number_count = {}#{{{
    color_count = {}
    for c in cards[2:]:
        if c[0] in number_count:
            return 0
        else:
            number_count[c[0]] = 1
        if c[1] in color_count:
            color_count[c[1]] += 1
            if color_count[c[1]] > 2:
                return 0
        else:
            color_count[c[1]] = 1
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

def flush_outs(cards):
    number_count = {}#{{{
    for c in cards[2:]:
        if c[0] in number_count:
            return 0
        else:
            number_count[c[0]] = 1
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
            if cards[0][1] in the_color:
                my_top = max([my_top, cards[0][0]])
            if cards[1][1] in the_color:
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
