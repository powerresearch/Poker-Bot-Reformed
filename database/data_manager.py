import json
import re
import os
from pokerstars.config import hhpath
from public import is_recent_file

class DataManager():
    def __init__(self):
        with open('database/data/default_data.json') as f:#{{{
            self.default_data = json.load(f)#}}}

    def load_data(self, player_name):
        self.player_data = list()#{{{
        for i in xrange(6):
            if player_name[i] != u'd':
                try:
                    with open('database/data/player '+player_name[i].replace('/', '')+'.json') as f:
                        single_data = json.load(f)
                except Exception as e:
                    print e
                    print player_name[i]
                    single_data = self.default_data
                if single_data[u'HANDS'] > 30:
                    self.player_data.append(single_data)
                else:
                    self.player_data.append(self.default_data)
            else:
                self.player_data.append(self.default_data)#}}}

    def get_item(self, seat, item):
        if type(self.player_data[seat][item]) in [float, int]:#{{{
            return self.player_data[seat][item]
        elif self.player_data[seat][item][1] < 10:
            return 1.0 * self.default_data[item][0] / self.default_data[item][1]
        else:
            return 1.0 * self.player_data[seat][item][0] / self.default_data[item][1]#}}}

    def update(self):
        with open('database/file_parsed.json') as f:#{{{
            file_parsed = json.load(f)
        with open('database/game_parsed.json') as f:
            game_parsed = json.load(f)
        player_data = {}
        for file_name in os.listdir(hhpath+'deoxy1909'):
            if file_name[0] == '.':
                continue
            if 'Play Money' in file_name:
                continue
            if file_name in file_parsed and not is_recent_file(file_name):
                continue
            else:
                file_parsed[file_name] = 0
            with open(hhpath+'deoxy1909/'+file_name) as f:
                text = f.read()
            games = re.findall(r'PokerStars Zoom Hand \#.+?\*\*\* SUMMARY \*\*\*', text, re.DOTALL)
            for game in games:
                lines = game.splitlines()
                game_number = re.findall(r'[0-9]+', lines[0])[0]
                if game_number in game_parsed:
                    continue
                else:
                    game_parsed[game_number] = 0
                player = [0, 0, 0, 0, 0, 0]
                seat = {}
                for i in xrange(6):
                    line = lines[2+i]
                    line = line[8:]
                    line = line[:-10]
                    line = line.split(' (')
                    player[i] = ' ('.join(line[:-1])
                    seat[' ('.join(line[:-1])] = i
                    if not player[i] in player_data:
                        try:
                            with open('database/data/player '+player[i].replace('/', '')+'.json') as f:
                                player_data[player[i]] = json.load(f)
                        except:
                            player_data[player[i]] = self.player_data_init()
                            player_data[player[i]]['NAME'] = player[i]
                    player_data[player[i]]['HANDS'] += 1
                lines = lines[10:]
                game_over = 0
                stage = 0
                pf_bet = 1
                pf_opener = -1
                last_better = -1
                show_down = 0
                active = [1, 1, 1, 1, 1, 1]
                vpip = [0, 0, 0, 0, 0, 0]
                pfr = [0, 0, 0, 0, 0, 0]
                flck = [0, 0, 0, 0, 0, 0]
                tuck = [0, 0, 0, 0, 0, 0]
                rvck = [0, 0, 0, 0, 0, 0]
                flst = ''
                tust = ''
                rvst = ''
                winner = list()
                for line in lines:
                    if line.startswith(r'*** HOLE CARDS ***'):
                        stage = 1
                        continue
                    if line.startswith(r'*** FLOP ***'):
                        stage = 2
                        continue
                    if line.startswith(r'*** TURN ***'):
                        stage = 3
                        continue
                    if line.startswith(r'*** RIVER ***'):
                        stage = 4
                        continue
                    if line == r'*** SHOW DOWN ***':
                        stage = 5
                        show_down = 1
                        for i in xrange(6):
                            if active[i]:
                                player_data[player[i]]['WAS'][1] += 1
                        continue
                    if line == r'*** SUMMARY ***':
                        if pf_bet == 1:
                            player_data[player[0]]['BSA'][1] += 1
                            player_data[player[1]]['BSA'][1] += 1
                            player_data[player[5]]['BSA'][1] += 1
                            player_data[player[0]]['BSAB'][1] += 1
                            player_data[player[1]]['BSAS'][1] += 1
                            player_data[player[5]]['BSAC'][1] += 1
                        elif pf_opener == 5:
                            player_data[player[5]]['BSA'][0] += 1
                            player_data[player[5]]['BSA'][1] += 1
                            player_data[player[5]]['BSAC'][0] += 1
                            player_data[player[5]]['BSAC'][1] += 1
                            if not vpip[0]:
                                player_data[player[1]]['SFBS'][1] += 1
                                if not vpip[1]:
                                    player_data[player[1]]['SFBS'][0] += 1
                                    player_data[player[2]]['BFBS'][1] += 1
                                    if not vpip[2]:
                                        player_data[player[2]]['BFBS'][0] += 1
                        elif pf_opener == 0:
                            player_data[player[0]]['BSA'][0] += 1
                            player_data[player[0]]['BSA'][1] += 1
                            player_data[player[5]]['BSA'][1] += 1
                            player_data[player[5]]['BSAC'][1] += 1
                            player_data[player[0]]['BSAB'][0] += 1
                            player_data[player[0]]['BSAB'][1] += 1
                            
                            player_data[player[1]]['SFBS'][1] += 1
                            if not vpip[1]:
                                player_data[player[1]]['SFBS'][0] += 1
                                player_data[player[2]]['BFBS'][1] += 1
                                if not vpip[2]:
                                    player_data[player[2]]['BFBS'][0] += 1
                        elif pf_opener == 1:
                            player_data[player[1]]['BSA'][0] += 1
                            player_data[player[1]]['BSA'][1] += 1
                            player_data[player[1]]['BSAS'][0] += 1
                            player_data[player[1]]['BSAS'][1] += 1
                            player_data[player[5]]['BSA'][1] += 1
                            player_data[player[5]]['BSAC'][1] += 1
                            player_data[player[0]]['BSA'][1] += 1
                            player_data[player[0]]['BSAB'][1] += 1

                            player_data[player[2]]['BFBS'][1] += 1
                            if not vpip[2]:
                                player_data[player[2]]['BFBS'][0] += 1

                        if len(winner) == 1:
                            player_data[winner[0]]['WWS'][1] += 1
                            if show_down:
                                player_data[winner[0]]['WAS'][0] += 1
                            else:
                                player_data[winner[0]]['WWS'][0] += 1

                        for i in xrange(6):
                            if vpip[i]:
                                player_data[player[i]]['VPIP'] += 1
                                player_data[player[i]]['VPIP'+str(i)] += 1
                            if pfr[i]:
                                player_data[player[i]]['PFR'] += 1
                                player_data[player[i]]['PFR'+str(i)] += 1
                        break
                    if stage == 1:
                        if re.match(r'.+? collected .+? from pot', line):
                            p = line.split(' collected')[0]
                            winner.append(p)
                            continue
                        if re.match(r'.+?: raises .+', line):
                            p = line.split(': raises')[0]
                            last_better = p
                            pf_bet += 1
                            vpip[seat[p]] = pf_bet
                            pfr[seat[p]] = 1
                            if pf_bet == 2:
                                pf_opener = seat[p]
                                continue
                            if pf_bet == 3:
                                player_data[p]['3B'][0] += 1
                                continue
                            if pf_bet == 4:
                                player_data[p]['4B'][0] += 1
                                player_data[p]['F3B'][1] += 1
                                continue
                            if pf_bet == 5:
                                player_data[p]['F4B'][1] += 1
                                continue
                        if re.match(r'.+?: calls .+', line):
                            p = line.split(': calls')[0]
                            vpip[seat[p]] = pf_bet
                            if pf_bet == 2:
                                player_data[p]['3B'][1] += 1
                            if pf_bet == 3:
                                player_data[p]['F3B'][1] += 1
                                player_data[p]['4B'][1] += 1
                                continue
                            if pf_bet == 4:
                                player_data[p]['F4B'][1] += 1
                                continue
                        if re.match(r'.+?: folds.+', line):
                            p = line.split(': folds')[0]
                            active[seat[p]] = 0
                            if pf_bet == 2:
                                player_data[p]['3B'][1] += 1
                            if pf_bet == 3:
                                player_data[p]['4B'][1] += 1
                            if vpip[seat[p]] <= 1:
                                continue
                            elif vpip[seat[p]] == 2 and pf_bet == 3:
                                player_data[p]['F3B'][0] += 1
                                player_data[p]['F3B'][1] += 1
                                continue
                            elif vpip[seat[p]] == 3 and pf_bet == 4:
                                player_data[p]['F4B'][0] += 1
                                player_data[p]['F4B'][1] += 1
                                continue
                    elif stage == 2:
                        if re.match(r'.+? collected .+? from pot', line):
                            p = line.split(' collected')[0]
                            winner.append(p)
                            continue
                        if re.match(r'.+?: checks', line):
                            p = line.split(': checks')[0]
                            flck[seat[p]] = 1
                            if sum(flck) == 1:
                                player_data[p]['FLCR'][1] += 1
                            if last_better == p:
                                player_data[p]['FLCB'][1] += 1
                            else:
                                player_data[p]['FLDK'][1] += 1
                            continue
                        if re.match(r'.+?: bets .+', line):
                            p = line.split(': bets')[0]
                            if last_better == p:
                                player_data[p]['FLCB'][0] += 1
                                player_data[p]['FLCB'][1] += 1
                                flst = 'cb'
                            else:
                                player_data[p]['FLDK'][0] += 1
                                player_data[p]['FLDK'][1] += 1
                                last_better = p
                                flst = 'dk'
                            continue
                        if re.match(r'.+?: calls', line):
                            p = line.split(': calls')[0]
                            if flst == 'cb':
                                player_data[p]['FLFCB'][1] += 1
                                player_data[p]['FLR'][1] += 1
                                continue
                            if flst == 'dk':
                                player_data[p]['FLFDK'][1] += 1
                                player_data[p]['FLR'][1] += 1
                                continue
                            if flst == 'r':
                                player_data[p]['FLFR'][1] += 1
                                continue
                            if flst == 'cr':
                                player_data[p]['FLFCR'][1] += 1
                                continue
                        if re.match(r'.+?: raises .+', line):
                            p = line.split(': raises')[0]
                            player_data[p]['FLR'][0] += 1
                            if flst == 'cb':
                                if flck[seat[p]]:
                                    player_data[p]['FLCR'][0] += 1
                                    flst = 'cr'
                                else:
                                    player_data[p]['FLFCB'][1] += 1
                                    flst = 'r'
                                continue
                            if flst == 'dk':
                                if flck[seat[p]]:
                                    player_data[p]['FLCR'][0] += 1
                                    flst = 'cr'
                                else:
                                    player_data[p]['FLFDK'][1] += 1
                                    flst = 'r'
                                continue
                            if flst == 'r':
                                player_data[p]['FLFR'][1] += 1
                                continue
                            if flst == 'cr':
                                player_data[p]['FLFCR'][1] += 1
                                continue
                            if flck[seat[p]]:
                                player_data[p]['FLCR'][0] += 1
                                flst = 'cr'
                                continue

                        if re.match(r'.+?: folds', line):
                            p = line.split(': folds')[0]
                            active[seat[p]] = 0
                            if flst == 'cb':
                                player_data[p]['FLFCB'][0] += 1
                                player_data[p]['FLFCB'][1] += 1
                                player_data[p]['FLR'][1] += 1
                                continue
                            if flst == 'dk':
                                player_data[p]['FLFDK'][0] += 1
                                player_data[p]['FLFDK'][1] += 1
                                player_data[p]['FLR'][1] += 1
                                continue
                            if flst == 'r':
                                player_data[p]['FLFR'][0] += 1
                                player_data[p]['FLFR'][1] += 1
                                continue
                            if flst == 'cr':
                                player_data[p]['FLFCR'][0] += 1
                                player_data[p]['FLFCR'][1] += 1
                                continue
                    
                    elif stage == 3:
                        if re.match(r'.+? collected .+? from pot', line):
                            p = line.split(' collected')[0]
                            winner.append(p)
                            continue
                        if re.match(r'.+?: checks', line):
                            p = line.split(': checks')[0]
                            tuck[seat[p]] = 1
                            if sum(tuck) == 1:
                                player_data[p]['TUCR'][1] += 1
                            if last_better == p:
                                player_data[p]['TUCB'][1] += 1
                            else:
                                player_data[p]['TUDK'][1] += 1
                            continue
                        if re.match(r'.+?: bets .+', line):
                            p = line.split(': bets')[0]
                            if last_better == p:
                                player_data[p]['TUCB'][0] += 1
                                player_data[p]['TUCB'][1] += 1
                                tust = 'cb'
                            else:
                                player_data[p]['TUDK'][0] += 1
                                player_data[p]['TUDK'][1] += 1
                                last_better = p
                                tust = 'dk'
                            continue
                        if re.match(r'.+?: calls', line):
                            p = line.split(': calls')[0]
                            if tust == 'cb':
                                player_data[p]['TUFCB'][1] += 1
                                player_data[p]['TUR'][1] += 1
                                continue
                            if tust == 'dk':
                                player_data[p]['TUFDK'][1] += 1
                                player_data[p]['TUR'][1] += 1
                                continue
                            if tust == 'r':
                                player_data[p]['TUFR'][1] += 1
                                continue
                            if tust == 'cr':
                                player_data[p]['TUFCR'][1] += 1
                                continue
                        if re.match(r'.+?: raises .+', line):
                            p = line.split(': raises')[0]
                            player_data[p]['TUR'][0] += 1
                            if tust == 'cb':
                                if tuck[seat[p]]:
                                    player_data[p]['TUCR'][0] += 1
                                    tust = 'cr'
                                else:
                                    player_data[p]['TUFCB'][1] += 1
                                    tust = 'r'
                                continue
                            if tust == 'dk':
                                if tuck[seat[p]]:
                                    player_data[p]['TUCR'][0] += 1
                                    tust = 'cr'
                                else:
                                    player_data[p]['TUFDK'][1] += 1
                                    tust = 'r'
                                continue
                            if tust == 'r':
                                player_data[p]['TUFR'][1] += 1
                                continue
                            if tust == 'cr':
                                player_data[p]['TUFCR'][1] += 1
                                continue
                            if tuck[seat[p]]:
                                player_data[p]['TUCR'][0] += 1
                                flst = 'cr'
                                continue

                        if re.match(r'.+?: folds', line):
                            p = line.split(': folds')[0]
                            active[seat[p]] = 0
                            if tust == 'cb':
                                player_data[p]['TUFCB'][0] += 1
                                player_data[p]['TUFCB'][1] += 1
                                player_data[p]['TUR'][1] += 1
                                continue
                            if tust == 'dk':
                                player_data[p]['TUFDK'][0] += 1
                                player_data[p]['TUFDK'][1] += 1
                                player_data[p]['TUR'][1] += 1
                                continue
                            if tust == 'r':
                                player_data[p]['TUFR'][0] += 1
                                player_data[p]['TUFR'][1] += 1
                                continue
                            if tust == 'cr':
                                player_data[p]['TUFCR'][0] += 1
                                player_data[p]['TUFCR'][1] += 1
                                continue

                    elif stage == 4:
                        if re.match(r'.+? collected .+? from pot', line):
                            p = line.split(' collected')[0]
                            winner.append(p)
                            continue
                        if re.match(r'.+?: checks', line):
                            p = line.split(': checks')[0]
                            rvck[seat[p]] = 1
                            if sum(rvck) == 1:
                                player_data[p]['RVCR'][1] += 1
                            if last_better == p:
                                player_data[p]['RVCB'][1] += 1
                            else:
                                player_data[p]['RVDK'][1] += 1
                            continue
                        if re.match(r'.+?: bets .+', line):
                            p = line.split(': bets')[0]
                            if last_better == p:
                                player_data[p]['RVCB'][0] += 1
                                player_data[p]['RVCB'][1] += 1
                                rvst = 'cb'
                            else:
                                player_data[p]['RVDK'][0] += 1
                                player_data[p]['RVDK'][1] += 1
                                last_better = p
                                rvst = 'dk'
                            continue
                        if re.match(r'.+?: calls', line):
                            p = line.split(': calls')[0]
                            if rvst == 'cb':
                                player_data[p]['RVFCB'][1] += 1
                                player_data[p]['RVR'][1] += 1
                                continue
                            if rvst == 'dk':
                                player_data[p]['RVFDK'][1] += 1
                                player_data[p]['RVR'][1] += 1
                                continue
                            if rvst == 'r':
                                player_data[p]['RVFR'][1] += 1
                                continue
                            if rvst == 'cr':
                                player_data[p]['RVFCR'][1] += 1
                                continue
                        if re.match(r'.+?: raises .+', line):
                            p = line.split(': raises')[0]
                            player_data[p]['RVR'][0] += 1
                            if rvst == 'cb':
                                if rvck[seat[p]]:
                                    player_data[p]['RVCR'][0] += 1
                                    rvst = 'cr'
                                else:
                                    player_data[p]['RVFCB'][1] += 1
                                    rvst = 'r'
                                continue
                            if rvst == 'dk':
                                if rvck[seat[p]]:
                                    player_data[p]['RVCR'][0] += 1
                                    rvst = 'cr'
                                else:
                                    player_data[p]['RVFDK'][1] += 1
                                    rvst = 'r'
                                continue
                            if rvst == 'r':
                                player_data[p]['RVFR'][1] += 1
                                continue
                            if rvst == 'cr':
                                player_data[p]['RVFCR'][1] += 1
                                continue
                            if rvck[seat[p]]:
                                player_data[p]['RVCR'][0] += 1
                                rvst = 'cr'
                                continue

                        if re.match(r'.+?: folds', line):
                            p = line.split(': folds')[0]
                            active[seat[p]] = 0
                            if rvst == 'cb':
                                player_data[p]['RVFCB'][0] += 1
                                player_data[p]['RVFCB'][1] += 1
                                player_data[p]['RVR'][1] += 1
                                continue
                            if rvst == 'dk':
                                player_data[p]['RVFDK'][0] += 1
                                player_data[p]['RVFDK'][1] += 1
                                player_data[p]['RVR'][1] += 1
                                continue
                            if rvst == 'r':
                                player_data[p]['RVFR'][0] += 1
                                player_data[p]['RVFR'][1] += 1
                                continue
                            if rvst == 'cr':
                                player_data[p]['RVFCR'][0] += 1
                                player_data[p]['RVFCR'][1] += 1
                                continue

                    elif stage == 5:
                        if re.match(r'.+? collected .+? from pot', line):
                            p = line.split(' collected')[0]
                            winner.append(p)
                            continue
        for name in player_data:
            player_data[name]['pfr'] = 1.0 * player_data[name]['PFR'] / player_data[name]['HANDS']
            player_data[name]['vpip'] = 1.0 * player_data[name]['VPIP'] / player_data[name]['HANDS']
            with open('database/data/player '+name.replace('/', '')+'.json', 'w') as f:
                json.dump(player_data[name], f)
        with open('database/file_parsed.json', 'w') as f:
            json.dump(file_parsed, f)
        with open('database/game_parsed.json', 'w') as f:
            json.dump(game_parsed, f)#}}}

    def player_data_init(self):
       #{{{ 
        result = {}
        result['NAME'] = ''
        result['HANDS'] = 0
        result['WAS'] = [0, 0]  # [WAS, TOTAL SHOWDOWN]
        result['WWS'] = [0, 0]  # [WWS, TOTAL WIN]
        result['VPIP'] = 0
        result['VPIP0'] = 0
        result['VPIP1'] = 0
        result['VPIP2'] = 0
        result['VPIP3'] = 0
        result['VPIP4'] = 0
        result['VPIP5'] = 0
        result['PFR'] = 0
        result['PFR0'] = 0
        result['PFR1'] = 0
        result['PFR2'] = 0
        result['PFR3'] = 0
        result['PFR4'] = 0
        result['PFR5'] = 0
        result['BSA'] = [0, 0]  # [BSA, CO&BTN&SB]
        result['BSAC'] = [0, 0] # [BSA at CO, CO]
        result['BSAB'] = [0, 0] # [BSA at BTN, BTN]
        result['BSAS'] = [0, 0] # [BSA at SB, SB]
        result['SFBS'] = [0, 0]  # [FBS at SB, SB]
        result['BFBS'] = [0, 0]  # [FBS at BB, BB]
        result['3B'] = [0, 0]
        result['F3B'] = [0, 0]  # [F3B, OPENER or CALLER]
        result['4B'] = [0, 0]
        result['F4B'] = [0, 0]
        result['FLCB'] = [0, 0] 
        result['FLFCB'] = [0, 0]
        result['FLDK'] = [0, 0] 
        result['FLFDK'] = [0, 0]
        result['FLR'] = [0, 0]
        result['FLCR'] = [0, 0] # [CR, CHECK]
        result['FLFR'] = [0, 0]
        result['FLFCR'] = [0, 0]
        result['TUCB'] = [0, 0]
        result['TUFCB'] = [0, 0]
        result['TUDK'] = [0, 0]
        result['TUFDK'] = [0, 0]
        result['TUR'] = [0, 0]
        result['TUCR'] = [0, 0]
        result['TUFR'] = [0, 0]
        result['TUFCR'] = [0, 0]
        result['RVCB'] = [0, 0]
        result['RVFCB'] = [0, 0]
        result['RVDK'] = [0, 0]
        result['RVFDK'] = [0, 0]
        result['RVR'] = [0, 0]
        result['RVCR'] = [0, 0]
        result['RVFR'] = [0, 0]
        result['RVFCR'] = [0, 0]
        return result
#}}}
