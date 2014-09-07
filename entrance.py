from game_driver import GameDriver
from make_data import GameDriver as make_data
from pokerstars.get_name_figure import get_name_figure
from public import del_stdout_line
import sys
import time
import re

if sys.argv[1] == 'ps':
    game_number = 0
    last_game_number = 1
    while True:
        game_driver = GameDriver('ps')
        if game_number != last_game_number:
            game_driver.count_game()
            print '\n\n\nStarting New Game'
            print 'Game Counting:', int(game_driver.game_count)
        last_game_number = game_number
        game_number = game_driver.game_stream(last_game_number)
        if game_driver.game_count % 20 == 0:
            get_name_figure()
            game_driver.data_manager.update()
elif sys.argv[1].startswith('makedata'):
    c = 0
    with open('learning/'+sys.argv[1][8:]) as f:
        test_file = f.read()
    games = re.findall(r'PokerStars Zoom Hand \#.+?\*\*\* SUMMARY \*\*\*', test_file, re.DOTALL)
    games.reverse()
    for game in games:
        c += 1
        if c % 100 == 0:
            print c, '/', len(games)
        game_driver = make_data(game, sys.argv[2])
        game_driver.game_stream(-1)
else:
    with open(sys.argv[1]) as f:
        test_file = f.read()
    games = re.findall(r'PokerStars Zoom Hand \#.+?\*\*\* SUMMARY \*\*\*', test_file, re.DOTALL)
    for game in games:
        print game
#       del_stdout_line(len(game.splitlines())+1)
        print '####################\n\n\n\n\n'
        print '####################'
        print 'Starting New Game'
        game_driver = GameDriver(game)
        game_driver.game_stream(-1)
        raw_input('---ENDING GAME---')
