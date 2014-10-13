import json
import math
import cPickle
import sys
import random
sys.path.insert(1, '/Library/Python/2.7/site-packages')
from sklearn import svm
from norm import norm

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
    stack_feature = list()
    for line in lines:
        features = line.split(',')
        for i in xrange(len(features)):
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
            Y = -1
        elif float(feature[-1]) == 0:
            Y = 0
        else:
            Y = 1
        allX.append(X)
        allY.append(Y)
    return norm(allX), allY

def main(training_n, allX, allY):
    random.shuffle(allX)
    random.shuffle(allY)
    Xt = allX[:training_n]
    Yt = allY[:training_n]
    X = [999]*len(Xt[0])
    Y = -1
    Xt.append(X)
    Yt.append(Y)
    Xv = allX[-1000:]
    Yv = allY[-1000:]
    clf = svm.SVC(C=999, probability=1)
    clf2 = svm.SVC(C=999)
    clf.fit(Xt, Yt)
    clf2.fit(Xt, Yt)
    a = [0, 0]
    cost = 0
    index_map = [-1, 0, 1]
    for xx,yy in zip(Xt, Yt):
        h = clf.predict_proba(xx)[0]
        h2 = clf.predict(xx)     
#       print yy, h
        a[h2[0]==yy] += 1
        cost += (1-h[0])*(yy==index_map[0])+(1-h[1])*(yy==index_map[1])+(1-h[2])*(yy==index_map[2])
    print 'TrainingSetAccuracy: %f' % (1.0*a[1]/sum(a))
    print 'TrainingSetCost: %f' % (cost / training_n)
    a = [0, 0]
    b = [0, 0]
    cost = 0
    for xx,yy in zip(Xv, Yv):
        h = clf.predict_proba(xx)[0]
        h2 = clf.predict(xx)     
        a[h2[0]==yy] += 1
        cost += (1-h[0])*(yy==index_map[0])+(1-h[1])*(yy==index_map[1])+(1-h[2])*(yy==index_map[2])
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
        if n > len(X) * 2 / 3:
            continue
        print 'Samples: %d' % (n)
        main(n, X, Y)
