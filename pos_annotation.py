# -*- coding:utf-8 -*-

import time
from structures import read_texts, write_pos_ann, pos_analyzer, write_brat_ann

__author__ = 'Gree-gorey'

t1 = time.time()

for item in read_texts(u'txt', u'/home/gree-gorey/Corpus/'):
    ann = pos_analyzer(item[0])
    write_pos_ann(ann, item[1])
    # write_brat_ann(ann, item[1])

t2 = time.time()

print t2 - t1
