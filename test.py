from public import show_stats
from stats.stats_handler import StatsHandler

def a(n, p):
    show_stats([StatsHandler.trans_prob(StatsHandler.get_preflop_prob(n, p))], 0)

while True:
    n = raw_input('n')
    p = raw_input('p')
    a(float(n), p)
