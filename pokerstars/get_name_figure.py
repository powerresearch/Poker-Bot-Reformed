import json
import os
import re
import datetime
from pokerstars.config import hhpath
from public import is_recent_file

def get_name_figure():
    names_to_figure = list()
    with open('pokerstars/names_to_figure.txt') as f:
        line = f.readline()
        while line:
            if len(line) > 1:
                line = line.split(',')
                names_to_figure.append(line)
            line = f.readline()
    with open('pokerstars/names.json') as f:
        names = json.load(f)

    game_record = dict()

    for file_name in os.listdir(hhpath+'deoxy1909'):
        if not is_recent_file(file_name):
            continue
        with open(hhpath+'deoxy1909/'+file_name) as f:
            text = f.read()
        games = text.split('\n\n\n\n')
        for game in games:
            lines = game.split('\n')
            if len(lines) < 10:
                continue
            game_number = re.findall(r'[0-9]+', lines[0])[0]
            player = [0, 0, 0, 0, 0, 0]
            name_number = {}
            for i in xrange(6):
                line = lines[2+i]
                line = line[8:]
                line = line[:-10]
                line = line.split(' (')
                player[i] = ' ('.join(line[:-1])
            game_record[game_number] = {}
            game_record[game_number]['player'] = player

    with open('pokerstars/names_to_figure.txt', 'w') as f:
        for tup in names_to_figure:
            try:
                names[tup[2].strip('\n')] = game_record[tup[0].strip('#')]['player'][int(tup[1])]
                print 'Got name:' + game_record[tup[0].strip('#')]['player'][int(tup[1])]
            except:
                print 'failing', tup[0]
                f.write(','.join(tup))

    with open('pokerstars/names.json', 'w') as f:
        f.write(json.dumps(names))

if __name__ == '__main__':
    get_name_figure()
