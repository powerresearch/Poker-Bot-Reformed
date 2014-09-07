import json
import sys
sys.path.insert(1, '/Library/Python/2.7/site-packages')
from sklearn import tree

def main(training_n):
    with open('../X.json') as f:
        X = json.load(f)
    with open('../Y.json') as f:
        Y = json.load(f)

    Xt = X[:training_n]
    Yt = Y[:training_n]
    Xv = X[-10000:]
    Yv = Y[-10000:]
    
    max_depth = [50]
    min_samples_leaf = [2]
    min_samples_split = [2]
    prob_thres = [0.5]
    for md in max_depth:
        for msl in min_samples_leaf:
            for mss in min_samples_split:
                for pt in prob_thres:
                    print 'max_depth: %d, min_samples_leaf: %d, min_samples_split: %d, prob_thres: %.1f' % (md, msl, mss, pt)
                    t = tree.DecisionTreeClassifier(max_depth=md, min_samples_leaf=msl, min_samples_split=mss)
                    t.fit(Xt, Yt)
                    a = [0, 0]
                    for xx,yy in zip(Xt, Yt):
                        h = t.predict_proba(xx)
                        if h[0][1] > pt:
                            if yy == 1:
                                a[1] += 1
                            else:
                                a[0] += 1
                        else:
                            if yy == 1:
                                a[0] += 1
                            else:
                                a[1] += 1
                    print 'TrainingSetAccuracy: %f' % (1.0*a[1]/(a[0]+a[1])) 
                    a = [0, 0]
                    b = [0, 0]
                    for xx,yy in zip(Xv, Yv):
                        h = t.predict_proba(xx)
                        if h[0][1] > pt:
                            if yy == 1:
                                b[1] += 1
                                a[1] += 1
                            else:
                                a[0] += 1
                                b[0] += 1
                        else:
                            if yy == 1:
                                a[0] += 1
                            else:
                                a[1] += 1
                    print 'ValidationAccuracy: %f' % (1.0*a[1]/(a[0]+a[1])) 
                    print 'ValidationPrecision: %f' % (1.0*b[1]/(b[0]+b[1])), b 
                        

if __name__ == '__main__':
    main(30000)
