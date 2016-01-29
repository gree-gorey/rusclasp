# -*- coding:utf-8 -*-

import time
from structures import Text, read_texts, write_brat_ann, write_clause_ann

__author__ = 'Gree-gorey'

t1 = time.time()

for item in read_texts(u'json', u'/home/gree-gorey/Corpus/'):
    newText = Text()
    newText.sentence_splitter(item)

    for sent in newText.sentences:

        # sent.find_pp()
        # sent.find_np()
        # sent.eliminate_and_disambiguate()

    # write_brat_ann(newText, item[1])

        sent.span_splitter()

        for span in sent.spans:
            span.type()
            span.clear_boundaries()

        sent.restore_alpha()

    #     sent.restore_beta()

        for span in sent.spans:
            span.get_boundaries()

    write_clause_ann(newText, item[1])

    # for sent in newText.sentences:  # удаляем все вводные слова из разметки
    #     remove_inserted(sent)
    #     print len(sent.spans)
    #     for i in xrange(len(sent.spans)):
    #         if not conj(sent.spans[i].tokens[0]):
    #             print 1
    #             if not verb_in_span(sent.spans[i]):
    #                 print 2
    #                 w.write(sent.spans[i].content + u'\n')


t2 = time.time()

print t2 - t1
