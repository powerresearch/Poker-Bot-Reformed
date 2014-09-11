import json
import cPickle
import sys
sys.path.insert(1, '/Library/Python/2.7/site-packages')
from sklearn import svm

with open('../bigX.json') as f:
    X = json.load(f)
with open('../bigY.json') as f:
    Y = json.load(f)
with open('../smallX.json') as f:
    Xv = json.load(f)
with open('../smallY.json') as f:
    Yv = json.load(f)

def main(training_n):
    
    Xt = X[:training_n]
    Yt = Y[:training_n]

    clf = svm.SVC(C=10000)
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
    if training_n == 40000:
        with open('svm_model.pkl', 'w') as f:
            cPickle.dump(clf, f)


if __name__ == '__main__':
    t = [10, 20, 40, 100, 200, 400, 1000, 2000, 4000, 10000, 20000, 40000]
    for n in t:
        print 'Samples: %d' % (n)
        main(n)
