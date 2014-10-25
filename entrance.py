from game_driver import GameDriver
from make_data import GameDriver as make_data
from pokerstars.get_name_figure import get_name_figure
from pokerstars.controller import Controller
from pokerstars.screen_scraper import get_shift
from public import del_stdout_line
import pyscreenshot
import sys
import os
import time
import re
import random

if sys.argv[1] == 'ps':
    game_number = 0
    last_game_number = 1
    stuck_count = 0
    very_starting_time = time.time()
    starting_time = time.time()
    session_length = 18000 + random.random() * 18000
    rest_length = random.random() * 1800
    shift = []
    while not shift:
        im = pyscreenshot.grab()
        shift = get_shift(im) 
    c = Controller(1, shift)
    while True:
#        if time.time() - starting_time > session_length:
#            print 'Rest for a while', rest_length
#            c.rest(rest_length)
#            starting_time = time.time()
#            session_length = 18000 + random.random() * 18000
#            rest_length = random.random() * 1800
        game_driver = GameDriver('ps', shift)
        stuck_count += 1
        if stuck_count > 2:
            print 'Stuck Count: ', stuck_count
        print game_number, last_game_number
        if game_number != last_game_number:
            stuck_count = 0
            game_driver.count_game()
            print '\n\n\nStarting New Game'
            print 'Time Consumed:', int(time.time()-very_starting_time)
            print 'Game Counting:', int(game_driver.game_count)
        if stuck_count > 100:
            c.sit_out()
            last_game_number = 1
            game_number = 0
            stuck_count = 0
            continue
        if stuck_count > 20:
            c.fold()
            last_game_number = 1
            game_number = 0
            continue
#       if stuck_count > 10:
#           im = pyscreenshot.grab()
#           im.save('stuckingshots/'+str(stuck_count)+'.png')
        last_game_number = game_number
        game_number = game_driver.game_stream(last_game_number)
        if game_driver.game_count % 50 == 0:
            print 'Getting Name Figure' 
            get_name_figure()
            print 'Updating Database...\n\n\n\n'
            game_driver.data_manager.update()
            game_driver.count_game()
elif sys.argv[1] == 'makedata':
    c = 0
    #for file_name in os.listdir('pokerdata'):
    for i in xrange(1):
        file_name = 'vali.txt'
        with open(file_name) as f:
            test_file = f.read()
            if '9-max Seat' in test_file:
                continue
        test_file = test_file.replace('\xe2\x82\xac', '$')
        games = re.findall(r'PokerStars Zoom Hand \#.+?FLOP.+?\*\*\* SUMMARY \*\*\*', test_file, re.DOTALL)
        for game in games:
            if not 'Seat 6' in game:
                continue
            c += 1
            if c % 10 == 0:
                print c, '/', len(games)
            game_driver = make_data(game, sys.argv[2])
            game_driver.game_stream(-1)
else:
    with open(sys.argv[1]) as f:
        test_file = f.read()
    games = re.findall(r'PokerStars Zoom Hand \#.+?PokerStars Zoom Hand', test_file, re.DOTALL)
    print len(games)
    random.shuffle(games)
    for game in games:
        if re.findall(r'deoxy1909.*folded before Flop', game):
            continue
        print game
#       del_stdout_line(len(game.splitlines())+1)
        print '####################\n\n\n\n\n'
        print '####################'
        print 'Starting New Game'
        game_driver = GameDriver(game)
        game_driver.game_stream(-1)
        raw_input('---ENDING GAME---')
