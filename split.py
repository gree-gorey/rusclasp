# -*- coding:utf-8 -*-

import time
from structures import Text, read_texts, write_brat_sent, write_clause_ann

__author__ = 'Gree-gorey'

t1 = time.time()

for item in read_texts(u'json', u'/home/gree-gorey/Corpus/'):
    newText = Text()
    for i in xrange(len(item[0])):
        newText.sentence_on()
        newText.add_token(item[0][i]) if i == len(item[0])-1 else newText.add_token(item[0][i], item[0][i+1])
        if newText.end_of_sentence():
            newText.sentence_off()
    newText.sentence_off()

    for sent in newText.sentences:
        for token in sent.tokens:
            sent.span_on(token)
            sent.add_token(token)
            if token.end_of_span():
                sent.span_off(token)
            else:
                sent.span_on(token)
        sent.span_off(sent.tokens[-1])

        for span in sent.spans:
            span.type()

        for j in xrange(len(sent.spans)-1, -1, -1):
            if sent.spans[j].alpha:
                for k in xrange(j+1, len(sent.spans)):
                    if not sent.spans[k].alpha:
                        pass


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

    # for sent in newText.sentences:  # соединяем отношением разорванные предикации
    #     for i in xrange(len(sent.spans)):
    #         if splitter(sent.spans, i):
    #             sent.relations.append((i, i+2))


t2 = time.time()

print t2 - t1
