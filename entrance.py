from game_driver import GameDriver
import time

game_driver = GameDriver()
while True:
    print '\n\n\nStarting New Game'
    time.sleep(1)
    game_driver.game_stream()
