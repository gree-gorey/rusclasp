# -*- coding:utf-8 -*-

import codecs
import time

__author__ = u'Gree-gorey'

t1 = time.time()

output = []

with codecs.open(u'dict.opcorpora.txt', u'r', u'utf-8') as f:
    for line in f:
        line = line.rstrip().split(u'\t')
        for item in line:
            if u'PREP' in item:
                output.append(line[0].lower())

with codecs.open(u'output.csv', u'w', u'utf-8') as w:
    for line in output:
        w.write(line + u'\n')

t2 = time.time()

print t2 - t1
