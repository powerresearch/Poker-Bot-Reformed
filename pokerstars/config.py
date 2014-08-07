import json

# Path
hhpath = '/Users/zw/Library/Application Support/PokerStars/HandHistory/'


# Position
game_number_x = 46
game_number_y = 72

label_position = (600, 520)

fold_position = (450, 560)
call_position = (590, 565)
raise_position = (725, 560)

xy1 = (390, 460)
xy2 = (55, 360)
xy3 = (55, 190)
xy4 = (345, 125)
xy5 = (690, 190)
xy6 = (690, 360)

cardposition1 = (385, 413)
cardposition2 = (77, 327)
cardposition3 = (74, 156)
cardposition4 = (372, 89)
cardposition5 = (720, 156)
cardposition6 = (720, 329)
cardposition = [cardposition1, cardposition2, cardposition3, cardposition4, cardposition5, cardposition6]

button1 = (465, 390)
button2 = (203, 355)
button3 = (180, 225)
button4 = (338, 170)
button5 = (624, 228)
button6 = (590, 354)

holecard1 = (344, 391)
holecard2 = (394, 392)
card1 = (262, 232)
card2 = (315, 232)
card3 = (370, 232)
card4 = (424, 232)
card5 = (479, 232)

button = [button1, button2, button3, button4, button5, button6]
card_position = [holecard1, holecard2, card1, card2, card3, card4, card5]
xy = [xy1,xy2,xy3,xy4,xy5,xy6]

name_xy1 = (359, 437)
name_xy2 = (30, 342)
name_xy3 = (30, 170)
name_xy4 = (327, 104)
name_xy5 = (657, 169)
name_xy6 = (657, 341)
name_width = 150
name_height = 20

name_xy = [name_xy1, name_xy2, name_xy3, name_xy4, name_xy5, name_xy6]

stack_width = 70
stack_height = 25

card_width = 20
card_height = 40

window_close = (15.5, 35.5)
sitout_confirm = (366.5, 345)
join_game = (900, 660)

with open('pokerstars/hand_figure.json') as f:
    hand_figure = json.load(f)

with open('pokerstars/graph_data.json') as f:
    graph_data = json.load(f)

with open('pokerstars/names.json') as f:
    names = json.load(f)
