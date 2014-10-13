import json
import math
import cPickle
import sys
import random
sys.path.insert(1, '/Library/Python/2.7/site-packages')
from neurolab.net import newff
from norm import norm

def map_stack_data(stack):
    stack = math.sqrt(stack)
    stack /= 2
    if stack > 1:
        return 1
    else:
        return stack

def load_data(file_name):
    with open('../tmp.txt'+file_name) as f:
        raw_text = f.read()
    allX = list()
    allY = list()
    lines = raw_text.split('\n')[:-1]
    stack_feature = list()
    for line in lines:
        features = line.split(',')
        for i in xrange(len(features)-1):
            if float(features[i]) > 2:
                if not i in stack_feature:
                    stack_feature.append(i)
    for line in lines:
        feature = line.split(',')
        X = list()
        for i in xrange(len(features)-1):
            if i in stack_feature:
                X.append(map_stack_data(float(features[i])))
            else:
                X.append(float(feature[i]))
        if float(feature[-1]) == -1:
            Y = [1, 0, 0]
        elif float(feature[-1]) == 0:
            Y = [0, 1, 0]
        else:
            Y = [0, 0, 1]
        allX.append(X)
        allY.append(Y)
    return norm(allX), allY

def main(training_n, allX, allY):
    random.shuffle(allX)
    random.shuffle(allY)
    Xt = allX[:training_n]
    Yt = allY[:training_n]
    Xv = allX[-500:]
    Yv = allY[-500:]
    the_net = newff(len(Xt[0])*[[-1, 1]], [15, 3])
    the_net.train(Xt, Yt, show=100, epochs=10000000, goal=0.1)
    a = [0, 0]
    cost = 0
    index_map = [-1, 0, 1]
    for xx,yy in zip(Xt, Yt):
        h = the_net.step(xx)
        yy = yy.index(1)
        if h[0] == max(h):
            predict = -1
        elif h[1] == max(h):
            predict = 0
        else:
            predict = 1
        if predict == yy:
            a[0] += 1
        else:
            a[1] += 1
    print a
    print 'TrainingSetAccuracy: %f' % (1.0*a[1]/sum(a))
#    print 'TrainingSetCost: %f' % (cost / training_n)
    a = [0, 0]
    b = [0, 0]
    cost = 0
    for xx,yy in zip(Xv, Yv):
        yy = yy.index(1)
        h = the_net.step(xx)
        if h[0] == max(h):
            predict = -1
        elif h[1] == max(h):
            predict = 0
        else:
            predict = 1
        if predict == yy:
            a[1] += 1
        else:
            a[0] += 1
    print a
    print 'ValidationSetAccuracy: %f' % (1.0*a[1]/sum(a))
#    print 'ValidationSetCost: %f' % (cost / len(Xv))

#    print 'ValidationSetPrecision: %f' % (1.0*b[1]/sum(b)), b

if __name__ == '__main__':
    filename = sys.argv[1]
    X, Y = load_data(filename)
    print len(X)
    t = [4000, 4000, 8000]
    for n in t:
        if n > len(X) * 3 / 3:
            continue
        print 'Samples: %d' % (n)
        main(n, X, Y)
