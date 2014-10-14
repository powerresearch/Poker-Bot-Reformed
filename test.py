from public import get_win_chance_table
from public import tree

stats = tree()
for num1 in xrange(2, 15):
    for col1 in xrange(1, 5):
        for num2 in xrange(2, 15):
            for col2 in xrange(1, 5):
                stats[num1][col1][num2][col2] = 0.1


get_win_chance_table(stats, [[14, 1], [10, 2], [8, 1]])
