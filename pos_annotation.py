# -*- coding:utf-8 -*-
__author__ = 'Gree-gorey'

import time
from structures import read_texts, write_pos_ann, pos_analyzer

t1 = time.time()

for item in read_texts():
    ann = pos_analyzer(item[0])
    write_pos_ann(ann, item[1])

t2 = time.time()

print t2 - t1
