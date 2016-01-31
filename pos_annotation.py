# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = 'Gree-gorey'

t1 = time.time()

newCorpus = Corpus(u'/home/gree-gorey/Corpus/')

for text in newCorpus.texts(u'txt'):
    # write_brat_ann(item[1])
    text.pos_analyzer()
    text.write_pos_ann()
    # write_brat_ann(ann, item[1])

t2 = time.time()

print t2 - t1
