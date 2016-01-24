# -*- coding:utf-8 -*-

import time
from structures import Text, read_texts, write_brat_sent, write_clause_ann, Chunk

__author__ = 'Gree-gorey'

t1 = time.time()

for item in read_texts(u'json', u'/home/gree-gorey/Corpus/'):
    newText = Text()
    newText.sentence_splitter(item)

    for sent in newText.sentences:
        # sent.span_splitter()

        # sent.find_np()
        sent.find_pp()
        # sent.eliminate_commas()

        # for token in sent.tokens:
        #     print token.pos, token.content

                        # print sent.tokens[j].gender, sent.tokens[j].inflection[0], sent.tokens[j].inflection[1]


        # for j in xrange(len(sent.tokens)-1, -1, -1):
        #     if u'PR' in sent.tokens[j].pos:
        #         sent.chunk = True
        #         sent.tokens[j].in_PP = True
        #         sent.chunks.append(Chunk())
        #         sent.chunks[-1].append(sent.tokens[j])
        #         for k in xrange(j+1, len(sent.tokens)):
        #             if not sent.tokens[k].in_PP:
        #                 sent.tokens[k].in_PP = True
        #                 sent.chunks[-1].append(sent.tokens[j])
        #                 if sent.tokens[k].agree(sent.tokens[j]):
        #                     sent.chunk = False
        #                     break

        # for span in sent.spans:
        #     span.type()
        #
        # sent.get_alpha()
        #
        # sent.get_beta()
        #
        # for span in sent.spans:
        #     span.get_boundaries()

    # write_brat_sent(newText, item[1])

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
