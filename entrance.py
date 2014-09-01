from game_driver import GameDriver
from pokerstars.get_name_figure import get_name_figure
from public import del_stdout_line
import sys
import time
import re

if sys.argv[1] == 'ps':
    while True:
        print '\n\n\nStarting New Game'
        time.sleep(1)
        game_driver = GameDriver('ps')
        game_driver.game_stream()
        game_driver.count_game()
        if game_driver.game_count % 10 == 0:
            get_name_figure()
            game_driver.data_manager.update()
else:
    with open('test_file.txt') as f:
        test_file = f.read()
    games = re.findall(r'PokerStars Zoom Hand \#.+?\*\*\* SUMMARY \*\*\*', test_file, re.DOTALL)
    for game in games:
#       print game
#       del_stdout_line(len(game.splitlines())+1)
        print '####################\n\n\n\n\n'
        print '####################'
        print 'Starting New Game'
        game_driver = GameDriver(game)
        game_driver.game_stream()
        raw_input('---ENDING GAME---')
