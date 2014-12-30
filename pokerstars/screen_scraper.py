import pyscreenshot
import re
from collections import defaultdict
from PIL import Image
from pokerstars.config import *
from public import map_card_string_to_tuple

def tree():
    return defaultdict(tree)

def merge(group, x, y, xx, yy):
    while len(group[xx][yy]) == 1:#{{{
        xx, yy = group[xx][yy][0][0], group[xx][yy][0][1]
    while len(group[x][y]) == 1:
        tmpx = x
        tmpy = y
        x, y = group[x][y][0][0], group[x][y][0][1]
        group[tmpx][tmpy][0][0] = xx
        group[tmpx][tmpy][0][1] = yy
    if x == xx and y == yy:
        return group
    for pair in group[x][y][1:]:
        group[xx][yy].append(pair)
    group[x][y] = [[xx, yy]]
    return group#}}}

def is_same_figure_stack(l1, l2):
    c1, c2, f1, f2 = 0, 0, 0, 0#{{{
    for pair in l1:
        if pair in l2:
            c1 += 1
        else:
            f1 += 1
    for pair in l2:
         if pair in l1:
             c2 += 1
         else:
             f2 += 1
    if 1.0 * c1 / (c1+f1) > 0.9 and 1.0 * c2 / (c2+f2) > 0.9:
        return True
    else:
        return False#}}}

def is_same_figure_card(l1, l2):
    c1, c2, f1, f2 = 0, 0, 0, 0#{{{
    for pair in l1:
        break_mark = 0
        for xchange in xrange(-1, 2):
            for ychange in xrange(-1, 2):
                if [pair[0]+xchange, pair[1]+ychange] in l2:
                    c1 += 1
                    break_mark = 1
                    break
            if break_mark:
                break
        if break_mark:
            continue
        return False
    for pair in l2:
        break_mark = 0
        for xchange in xrange(-1, 2):
            for ychange in xrange(-1, 2):
                if [pair[0]+xchange, pair[1]+ychange] in l1:
                    c2 += 1
                    break_mark = 1
                    break
            if break_mark:
                break
        if break_mark:
            continue
        return False
    return True#}}}

def norm(l):
    minx = 99999#{{{
    miny = 99999
    for p in l:
        minx = min(minx, p[0])
        miny = min(miny, p[1])
    for index in xrange(len(l)):
        l[index][0] = l[index][0] - minx
        l[index][1] = l[index][1] - miny
    return l#}}}

def get_shift(im, last_i=0, last_j=0):
    starti = last_i+285#{{{
    startj = last_j+235
    fail = 0
    count = 0
    for i in xrange(215):
        for j in xrange(50):
            pix = im.getpixel((starti+i, startj+j))
            if pix[0] != logo[count][0] or pix[1] != logo[count][1] or pix[2] != logo[count][2]:
                fail = 1
                break
            count += 1
        if fail:
            break
    if not fail:
        return [starti-285, startj-235]
    for starti in xrange(im.size[0]-215):
        for startj in xrange(im.size[1]-50):
            fail = 0
            count = 0
            for i in xrange(215):
                for j in xrange(50):
                    pix = im.getpixel((starti+i, startj+j))
                    if pix[0] != logo[count][0] or pix[1] != logo[count][1] or pix[2] != logo[count][2]:
                        fail = 1
                        break
                    count += 1
                if fail:
                    break
            if not fail:
                return [starti-285, startj-235]
    return []#}}}

class ScreenScraper():
    def __init__(self, game_driver, source='ps', shift=[0,0]):
        if source == 'ps':#{{{
            self.im = pyscreenshot.grab()
        self.shift = shift 
        self.source = source
        self.game_driver = game_driver
        self.got_names = 'to start'#}}}

    def update(self):
        self.im = pyscreenshot.grab()#{{{
        done_count = 0
        if self.got_names == 'in process':
            for i in xrange(6):
                if type(self.game_driver.player_name[i]) == unicode:
                    done_count += 1
                    continue
                else:
                    new_name = self.get_name(i)
                    if type(new_name) == unicode:
                        self.game_driver.player_name[i] = new_name 
                        print 'Name Updated:', i, unicode(self.game_driver.player_name[i])
            self.game_driver.data_manager.load_data(self.game_driver.player_name,\
                    self.game_driver.button)
            if done_count == 6:
                self.got_names = 'done'#}}}

    def get_init_values(self):
        result = {}#{{{
        stack = ['', '', '', '', '', '']
        game_number = []
        cards = ['', '']
        button = []
        player_name = [u'deoxy1909', '', '', '', '', '']#}}}
        if self.source == 'ps':
            fail = 0#{{{
            while not (game_number and (button in range(6))):
                game_number = self.get_game_number()
                button = self.get_button()
                if fail:
                    self.update()
#               print 'stucking at getting game number and button', game_number, button
                fail += 1
                if fail > 200:
                    return 'sit out'
                if fail > 100:
                    if not game_number:
                        return 'sit out'
                    if self.has_fold(1) and self.has_fold(2) and self.has_fold(3)\
                            and self.has_fold(4) and self.has_fold(5):
                        return 'get back'
                if fail > 10:
                    if self.get_stack(0) == []:
                        return 'sit out'
            fail = 0
            for i in xrange(6):
                fail = 0
                while stack[i] == '':
                    stack[i] = self.get_stack(i)
                    if stack[i] == 'sitting out':
                        stack[i] = 2.0001
                    if fail:
                        self.update()
                    fail += 1
                    if fail > 200:
                        if self.has_fold(1) and self.has_fold(2) and self.has_fold(3)\
                                and self.has_fold(4) and self.has_fold(5):
                            if stack[0] == '':
                                return 'sit out'
                            return 'get back'
#               print 'stucking at getting stack'
            fail = 0
            while not (cards[0] and cards[1]):
                cards[0] = self.get_card(0)
                cards[1] = self.get_card(1)
                if fail:
                    self.update()
#               print 'stucking at getting cards'
                fail = 1
            cards[0], cards[1] = min(cards[:2]), max(cards[:2])
            fail = 0
#            while not (type(player_name[0]) == unicode and type(player_name[1]) == unicode\
#                    and type(player_name[3]) == unicode and type(player_name[4]) == unicode\
#                    and type(player_name[5]) == unicode and type(player_name[2]) == unicode):
            for i in xrange(6):
                if type(player_name[i]) == unicode:
                    continue
                else:
                    player_name[i] = self.get_name(i)
            self.got_names = 'in process'
#            if fail:
#                self.update()
#                print 'stucking at getting names'
#            fail = 1
            result['stack'] = stack 
            result['game_number'] = game_number 
            result['cards'] = cards 
            result['player_name'] = player_name
            result['button'] = button#}}}
        else:
            lines = self.source.splitlines()#{{{
            game_number = re.findall(r'[0-9]+', lines[0])[0]
            player = [0, 0, 0, 0, 0, 0]
            seat = {}
            tmp_seat = {}
            tmp_stack = [0, 0, 0, 0, 0, 0]
            tmp_player = ['', '', '', '', '', '']
            for i in xrange(6):
                line = lines[2+i]
                line = line[8:]
                line = line[:-10]
                line = line.split(' (')
                tmp_stack[i] = float(line[-1][1:])#re.findall(r'\($([0-9\.]*) ', line[-1])[0]
                tmp_player[i] = ' ('.join(line[:-1])
                tmp_seat[' ('.join(line[:-1])] = i
            try:
                hero_name = re.findall(r'Dealt to (.*) \[', self.source)[0]
            except:
                hero_name = tmp_player[0]
            hero_seat = tmp_seat[hero_name]
            button = (0-hero_seat) % 6
            for i in xrange(6):
                stack[(i-hero_seat)%6] = tmp_stack[i]
                player[(i-hero_seat)%6] = tmp_player[i]
            for name in tmp_seat:
                seat[name] = (tmp_seat[name]-hero_seat) % 6
            try:
                card01 = re.findall('Dealt to .+? \[(.+?)]', self.source)[0]
                cards[0] = map_card_string_to_tuple(card01[:2])
                cards[1] = map_card_string_to_tuple(card01[3:])
                cards[0], cards[1] = min(cards[:2]), max(cards[:2])
            except:
                cards[0] = [2,1]
                cards[1] = [2,2]
            result['cards'] = cards
            result['game_number'] = game_number
            result['stack'] = stack
            result['player_name'] = player
            result['seat'] = seat
            result['button'] = button#}}}
        return result

    def get_game_number(self):
        im = self.im#{{{
        pixels = tree()
        group = tree()
        result = ''
        for digi in xrange(13):
            code = '' 
            i = 0
            for x in xrange(5):
                for y in xrange(8):
                    if sum(im.getpixel((game_number_x+digi*6+x+self.shift[0], game_number_y+y+self.shift[1]))) > 300:
                        code += '1'
                    else:
                        code += '0'
                    i += 1
            if code in hand_figure:
                result += str(hand_figure[code])
        return result#}}}

    def get_card(self, number):
        im = self.im#{{{
        fail = 0
        card = ''
        group = tree()
        pixels = tree()
        for x in xrange(card_width):
            for y in xrange(card_height):
                group[x][y] = [[x, y], [x, y]]
        for x in xrange(card_width):
            for y in xrange(card_height):
                color = im.getpixel((card_position[number][0]+x+self.shift[0], card_position[number][1]+y+self.shift[1]))
                if sum(color) > 500:
                    pixels[x][y] = 0
                else:
                    pixels[x][y] = 1
        for x in xrange(card_width):
            for y in xrange(card_height):
                if pixels[x][y] == 1 and pixels[x-1][y] == 1:
                    group = merge(group, x, y, x-1, y)
                if pixels[x][y] == 1 and pixels[x+1][y] == 1:
                    group = merge(group, x, y, x+1, y)
                if pixels[x][y] == 1 and pixels[x][y-1] == 1:
                    group = merge(group, x, y, x, y-1)
                if pixels[x][y] == 1 and pixels[x][y+1] == 1:
                    group = merge(group, x, y, x, y+1)
        for y in xrange(card_height):
            for x in xrange(card_width):
                if len(group[x][y]) > 20:
                    group[x][y] = norm(group[x][y])
                    over_width = 0
                    for pair in group[x][y][1:]:
                        if pair[0] > 15 or pair[1] > 25:
                            over_width = 1
                    if over_width:
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['spade']):
                        card += 's'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['heart']):
                        card += 'h'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['club']):
                        card += 'c'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['diamond']):
                        card += 'd'
                        continue
                    if number < 2:
                        for i in xrange(15):
                            if is_same_figure_card(group[x][y][1:], graph_data['c'+str(i)]):
                                card += str(i)
                                break
                    else:
                        for i in xrange(15):
                            if is_same_figure_card(group[x][y], graph_data['pc'+str(i)]):
                                card += str(i)
                                break
        card = card.replace('01', '10')
        if len(card) < 2:
            return ''
        card_pair = [1, 1]
        card_pair[0] = int(card[:-1])
        if card[-1] == 's':
            card_pair[1] = 1
        if card[-1] == 'h':
            card_pair[1] = 2
        if card[-1] == 'c':
            card_pair[1] = 3
        if card[-1] == 'd':
            card_pair[1] = 4
        return card_pair#}}}

    def shining(self, number='search'):
        im = self.im#{{{
        if number == 'search':
            for i in xrange(6):
                if self.shining(number=i):
                    return i
            return []
        for y in xrange(50):
            if sum(im.getpixel((xy[number][0]+self.shift[0], xy[number][1]+y+self.shift[1]))) > 450 and \
                    sum(im.getpixel((xy[number][0]+self.shift[0], xy[number][1]+y+self.shift[1]))) > 450:
                mark = 1
                for x in xrange(-5, 15):
                    if sum(im.getpixel((xy[number][0]+x+self.shift[0], xy[number][1]+y+self.shift[1]))) <= 450:
                        mark = 0
                if mark == 1:
                    return True
        return False#}}}

    def get_stack(self, number):
        im = self.im#{{{
        fail = 0
        stack = ''
        group = tree()
        pixels = tree()
        for x in xrange(stack_width):
            for y in xrange(stack_height):
                group[x][y] = [[x, y], [x, y]]
        for x in xrange(stack_width):
            for y in xrange(stack_height):
                if sum(im.getpixel((xy[number][0]+x+self.shift[0], xy[number][1]+y+self.shift[1]))) > 180:
                    pixels[x][y] = 1
                else:
                    pixels[x][y] = 0
        for x in xrange(stack_width):
            for y in xrange(stack_height):
                if pixels[x][y] == 1 and pixels[x-1][y] == 1:
                    merge(group, x, y, x-1, y)
                if pixels[x][y] == 1 and pixels[x+1][y] == 1:
                    merge(group, x, y, x+1, y)
                if pixels[x][y] == 1 and pixels[x][y-1] == 1:
                    merge(group, x, y, x, y-1)
                if pixels[x][y] == 1 and pixels[x][y+1] == 1:
                    merge(group, x, y, x, y+1)
        for x in xrange(stack_width):
            for y in xrange(stack_height):
                if len(group[x][y]) > 3:
                    norm(group[x][y])
                    over_width = 0
                    for pair in group[x][y][1:]:
                        if pair[0] > 10:
                            over_width = 1
                    if over_width:
                        continue
                    if len(group[x][y]) == 5:
                        stack += '.'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['$']):
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['a']):
                        stack += 'a'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['l']):
                        stack += 'l'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['i']):
                        stack += 'i'
                        continue
                    if is_same_figure_stack(group[x][y][1:], graph_data['n']):
                        stack += 'n'
                        continue
                    success_mark = 0
                    for i in xrange(10):
                        if is_same_figure_stack(group[x][y][1:], graph_data[str(i)]):
                            stack += str(i)
                            success_mark = 1
                            break
                    if not success_mark:
                        #fail += 1
                        pass
        if fail or not stack:
            return [] 
        stack.replace('i', 'l')
        if 'l' in stack:
            stack = 0
            return stack
        try:
            stack = float(stack)
        except:
#           print stack
            return 'sitting out'
        return round(stack, 2)#}}}

    def get_button(self):
        im = self.im#{{{
        button_position = 0
        for number in xrange(6):
            success = 0
            for i in xrange(-3, 4, 1):
                if success:
                    break
                for j in xrange(-3, 4, 1):
                    color = im.getpixel((button[number][0]+i+self.shift[0], button[number][1]+j+self.shift[1]))
                    if color[0] > 2 * (color[1]+color[2]):
                        success = 1
                        break
            if success:
                return number#}}}

    def my_turn(self):
        im = self.im#{{{
        for i in xrange(-10, 10):
            for j in xrange(-10, 10):
                x = raise_position[0] + i
                y = raise_position[1] + j
                color = im.getpixel((x+self.shift[0], y+self.shift[1]))
                if color[0] > color[1] + 30 and color[0] > color[2] + 30:
                    return True
        return False#}}}

    def has_fold(self, number):
        im = self.im#{{{
        x, y = cardposition[number][0], cardposition[number][1]
        for i in xrange(x-10, x+10):
            for j in xrange(y-10, y+10):
                if im.getpixel((i+self.shift[0], j+self.shift[1]))[0] > 100 and im.getpixel((i+self.shift[0], j+self.shift[1]))[0] == max(im.getpixel((i+self.shift[0], j+self.shift[1]))):
                    return False
        return True#}}}

    def get_name(self, i):
        im = self.im#{{{
        global to_figure
        try:
            to_figure.add(1)
            to_figure.remove(1)
        except:
            to_figure = set()
        code = ''
        blue_mark = 0
        shining_mark = self.shining(i)
        if shining_mark:
            return 1 #'shining'
        anchor = self.find_anchor(i)
        if not anchor:
            return 3 #'no anchor, why?'
        for x in xrange(90):
            for y in xrange(20):
                tup = im.getpixel((anchor[0]-45+x+self.shift[0], anchor[1]-20+y+self.shift[1]))
                if sum(tup) > 450:
                    code += str(x)+str(y)
                if tup[2] - 30 > tup[0] and tup[2] - 30 > tup[1]:
                    blue_mark = 1
                    break
            if blue_mark:
                break
        if blue_mark:
            return 0 #'blue'
        if code in names:
            return names[code]
        else:
            if not code in to_figure:
                hand = self.get_game_number()
                with open('pokerstars/names_to_figure.txt', 'a') as f:
                    f.write(hand.strip('#'))
                    f.write(',')
                    f.write(str((i-self.get_button()+6)%6))
                    f.write(',')
                    f.write(code)
                    f.write('\n')
            return u'd' #'none'#}}}

    def find_anchor(self, number):
        im = self.im#{{{    
        for x in xrange(25, -25, -1):
            for y in xrange(10, -10, -1):
                tup = im.getpixel((xy[number][0]+x+self.shift[0], xy[number][1]+y+self.shift[1]))
                if tup[0] == 200 and tup[1] == 200 and tup[2] == 200:
                    tup = im.getpixel((xy[number][0]+x+1+self.shift[0], xy[number][1]+y+self.shift[1]))
                    if tup[0] == 217 and tup[1] == 217 and tup[2] == 217:
                        return (xy[number][0]+x+19, xy[number][1]+y)
        print 'fail to get anchor!!!'
        return []#}}}
