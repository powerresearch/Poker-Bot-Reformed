import sys
sys.path.insert(0, '/Library/Python/2.7/site-packages/')
import numpy

def norm(mat):
    n1 = len(mat)
    n2 = len(mat[0])
    for i in xrange(n2):
        l = [a[i] for a in mat]
        m = numpy.mean(l)
        d = numpy.std(l)
        if d != 0:
            for j in xrange(n1):
                mat[j][i] = (mat[j][i]-m) / d
        else:
            for j in xrange(n1):
                mat[j][i] -= m
    return mat
