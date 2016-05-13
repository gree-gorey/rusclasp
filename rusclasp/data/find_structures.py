# -*- coding:utf-8 -*-

import time
import codecs
import json
from structures import Corpus

__author__ = 'Gree-gorey'

t1 = time.time()


# w = codecs.open(u'structures.txt', u'w', u'utf-8')
#
# newCorpus = Corpus(u'/home/gree-gorey/CorpusWithAnn/')
#
# # for text in newCorpus.texts(u'txt'):
# #     text.result.replace(u'…', u'...')
# #     text.rewrite()
#
# for text in newCorpus.texts(u'json'):
#     text.sentence_splitter()
#     with codecs.open(text.path.replace(u'json', u'txt'), u'r', u'utf-8') as f:
#         a = f.read()
#         for sentence in text.sentences:
#             if sentence.contain_structure():
#                 line = a[sentence.tokens[0].begin:sentence.tokens[-1].end:]
#                 w.write(line + u' ')
#
# w.close()

t2 = time.time()

print t2 - t1
