# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = 'Gree-gorey'

t1 = time.time()

newCorpus = Corpus(u'/home/gree-gorey/Corpus/')

for text in newCorpus.texts(u'json'):
    text.sentence_splitter()
    for sentence in text.sentences:

        # sent.find_pp()
        # sent.find_np()
        # sent.eliminate_and_disambiguate()

        sentence.span_splitter()

        for span in sentence.spans:
            span.type_inserted()

            span.type()
            span.clear_boundaries()

        sentence.restore_embedded()

        sentence.restore_base()

        for span in sentence.spans:
            span.get_boundaries()

    text.write_clause_ann()

t2 = time.time()

print t2 - t1
