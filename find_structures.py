# -*- coding:utf-8 -*-

import time
import codecs
from structures import Text, read_texts

__author__ = 'Gree-gorey'

t1 = time.time()


w = codecs.open(u'structures.txt', u'w', u'utf-8')

for item in read_texts(u'json', u'/home/gree-gorey/Corpus/'):
    newText = Text()
    newText.sentence_splitter(item)

    for sent in newText.sentences:
        if sent.contain_structure():
            line = u''
            for token in sent.tokens:
                line += token.content
            w.write(line + u'\n')

t2 = time.time()

print t2 - t1
