# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = 'Gree-gorey'

t1 = time.time()

newCorpus = Corpus(u'/home/gree-gorey/Corpus/')

for text in newCorpus.texts(u'txt'):
    # text.mystem_analyzer()
    text.treetagger_analyzer()
    text.write_pos_ann()

t2 = time.time()

print t2 - t1
