import json
import sys
import neurolab

def main(training_n):
    with open('../bigX.json') as f:
        X = json.load(f)
    with open('../bigY.json') as f:
        Y = json.load(f)

    Xt = X[:training_n]
    Yt = Y[:training_n]
    Xv = X[-10000:]
    Yv = Y[-10000:]

    net = neurolab.net.newff([[0,1]]*64, [10, 1])
    net.train(Xt, [[y] for y in Yt], epochs=100, show=1)
    a = [0, 0]
    for xx,yy in zip(Xt, Yt):
        if net.step(xx) > 0.5:
            h = 1
        else:
            h = 0
        a[h==yy] += 1
    print 'TrainingSetAccuracy: %f' % (1.0*a[1]/sum(a))
    a = [0, 0]
    b = [0, 0]
    for xx,yy in zip(Xv, Yv):
        if net.step(xx) > 0.5:
            h = 1
        else:
            h = 0
        a[h==yy] += 1
        if h==1:
            if yy == 1:
                b[1] += 1
            else:
                b[0] += 1
    print 'ValidationSetAccuracy: %f' % (1.0*a[1]/sum(a))
    try:
        print 'ValidationSetPrecision: %f' % (1.0*b[1]/sum(b)), b
    except:
        print 'ValidationSetPrecision: %f' % (0), b
