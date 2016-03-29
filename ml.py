# -*- coding:utf-8 -*-

import time
import numpy as np
from sklearn import svm

__author__ = u'gree-gorey'


def main():
    t1 = time.time()

    data = [[12, 1], [13, 1], [4, 0], [6, 0]]
    data = np.asarray(data)

    target = ['V', 'V', 'N', 'N']
    target = np.asarray(target)

    clf = svm.SVC(gamma=0.001, C=100.)

    clf.fit(data, target)

    check = [[8, 1]]
    check = np.asarray(check)

    print clf.predict(check)

    t2 = time.time()

    print t2 - t1

if __name__ == '__main__':
    main()
