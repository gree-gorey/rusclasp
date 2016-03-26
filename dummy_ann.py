# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = u'gree-gorey'

t1 = time.time()

newCorpus = Corpus(u'/home/gree-gorey/CorpusTest/')

for text in newCorpus.texts(u'txt'):

    text.write_dummy_ann()

    text.copy_into_brat(u'/opt/brat-v1.3_Crunchy_Frog/data/left/', True)

t2 = time.time()

print t2 - t1
