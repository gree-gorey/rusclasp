# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = 'Gree-gorey'

t1 = time.time()

newCorpus = Corpus(u'/home/gree-gorey/Corpus/')

for text in newCorpus.texts(u'json'):
    text.sentence_splitter()
    for sentence in text.sentences:
        # for token in sentence.tokens:
        #     if len(token.pos) == 0:
        #         print token.content

        sentence.find_pp()
        # sent.find_np()

        sentence.eliminate_pair_comma()

        sentence.span_splitter()

        for span in sentence.spans:

            span.type_inserted()
            span.type()

        sentence.split_embedded()

        sentence.restore_embedded()

        for span in sentence.spans:
            span.get_boundaries()

    text.write_clause_ann()

t2 = time.time()

print t2 - t1
