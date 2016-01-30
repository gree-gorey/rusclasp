# -*- coding:utf-8 -*-

import time
from structures import Corpus, write_pos_ann, pos_analyzer

__author__ = 'Gree-gorey'

t1 = time.time()

newCorpus = Corpus(u'/home/gree-gorey/Corpus/')

for item in newCorpus.read_texts(u'txt'):
    # write_brat_ann(item[1])
    ann = pos_analyzer(item[0].replace(u' ', u' '))
    write_pos_ann(ann, item[1])
    # write_brat_ann(ann, item[1])

t2 = time.time()

print t2 - t1
