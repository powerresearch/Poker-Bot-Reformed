import json
import sys
sys.path.insert(1, '/Library/Python/2.7/site-packages')
from sklearn import svm

def main(training_n):
    with open('../X.json') as f:
        X = json.load(f)
    with open('../Y.json') as f:
        Y = json.load(f)

    Xt = X[:training_n]
    Yt = Y[:training_n]
    Xv = X[-10000:]
    Yv = Y[-10000:]

    clf = svm.SVC(C=100)
    clf.fit(Xt, Yt)
    a = [0, 0]
    for xx,yy in zip(Xt, Yt):
        h = clf.predict(xx)
        a[h[0]==yy] += 1
    print 'TrainingSetAccuracy: %f' % (1.0*a[1]/sum(a))
    a = [0, 0]
    b = [0, 0]
    for xx,yy in zip(Xv, Yv):
        h = clf.predict(xx)
        a[h[0]==yy] += 1
        if h[0] == 1:
            if yy == 1:
                b[1] += 1
            else:
                b[0] += 1
    print 'ValidationSetAccuracy: %f' % (1.0*a[1]/sum(a))
    print 'ValidationSetPrecision: %f' % (1.0*b[1]/sum(b)), b
