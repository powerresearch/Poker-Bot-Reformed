from game_driver import GameDriver
from pokerstars.get_name_figure import get_name_figure
import time

while True:
    print '\n\n\nStarting New Game'
    time.sleep(1)
    game_driver = GameDriver()
    game_driver.game_stream()
    game_driver.count_game()
    if game_driver.game_count % 10 == 0:
        get_name_figure()
        game_driver.data_manager.update()
