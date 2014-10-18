import json
import math
import cPickle
import sys
import random
sys.path.insert(1, '/Library/Python/2.7/site-packages')
from sklearn import tree 

def map_stack_data(stack):
    stack = math.sqrt(stack)
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
    for line in lines:
        feature = line.split(',')
        X = [feature[3], feature[5]]#feature[1:-1]
        if float(feature[-1]) == -1:
            Y = -1
        else:
            Y = 1
        allX.append(X)
        allY.append(Y)
    return allX, allY

def main(training_n, allX, allY):
    random.shuffle(allX)
    random.shuffle(allY)
    Xt = allX[:training_n]
    Yt = allY[:training_n]
    Xv = allX[-500:]
    Yv = allY[-500:]
    clf = tree.DecisionTreeClassifier()
    clf.max_depth = 5 
    clf.min_split = 5
    clf.fit(Xt, Yt)
    a = [0, 0]
    cost = 0
    index_map = [-1, 1]
    for xx,yy in zip(Xt, Yt):
#       print xx
        h = clf.predict_proba(xx)[0]
        if h[0] == max(h):
            predict = -1
        elif h[1] == max(h):
            predict = 1
#       print yy,h
        a[predict==yy] += 1
        cost += (1-h[0])*(yy==index_map[0])+(1-h[1])*(yy==index_map[1])
    print 'TrainingSetAccuracy: %f' % (1.0*a[1]/sum(a))
    print 'TrainingSetCost: %f' % (cost / training_n)
    a = [0, 0]
    b = [0, 0]
    cost = 0
    for xx,yy in zip(Xv, Yv):
        h = clf.predict_proba(xx)[0]
        if h[0] == max(h):
            predict = -1
        elif h[1] == max(h):
            predict = 1
        a[predict==yy] += 1
        cost += (1-h[0])*(yy==index_map[0])+(1-h[1])*(yy==index_map[1])
        if h[0] == 1:
            if yy == 1:
                b[1] += 1
            else:
                b[0] += 1
    print 'ValidationSetAccuracy: %f' % (1.0*a[1]/sum(a))
    print 'ValidationSetCost: %f' % (cost / len(Xv))

#    print 'ValidationSetPrecision: %f' % (1.0*b[1]/sum(b)), b

if __name__ == '__main__':
    filename = sys.argv[1]
    X, Y = load_data(filename)
    print len(X)
    t = [10, 20, 40, 100, 200, 400, 1000, 2000, 4000, 8000]
    for n in t:
        if n > len(X) * 3 / 3:
            continue
        print 'Samples: %d' % (n)
        main(n, X, Y)
