# -*- coding:utf-8 -*-
__author__ = 'Gree-gorey'

import codecs, time
from structures import Text, read_texts, word_on, word_off, sentence_on, sentence_off, append_char, span_on, span_off
from structures import splitter, remove_inserted, if_verb

t1 = time.time()

low_letters = u'абвгдеёжзийклмнопрструфхцчшщъыьэюя'
up_letters = low_letters.upper()
numbers = u'0123456789'

writeName = '/home/gree-gorey/Py/verbs.txt'
w = codecs.open(writeName, 'w', 'utf-8')

sent_count = 0
token_count = 0

for item in read_texts():
    newText = Text()
    for i in xrange(len(item[0])):
        if item[0][i] in u'  ':
            word_off(newText, i, item)
        elif item[0][i] in u'.?!…,":;\'()':
            if i < len(item[0]):
                if item[0][i-1] not in numbers or item[0][i+1] not in numbers:
                    word_off(newText, i, item)
                    if item[0][i] in u'.?!…':
                        sentence_off(newText, i)
                    append_char(newText, item[0][i], i)
        elif item[0][i] in u'-–—':
            append_char(newText, item[0][i], i)
        elif item[0][i] in low_letters or item[0][i] in up_letters or item[0][i] in numbers:
            sentence_on(newText, i)
            word_on(newText, i)
    word_off(newText, len(item[0])-1, item)
    sentence_off(newText, len(item[0])-1)

    sent_count += len(newText.sentences)

    for sent in newText.sentences:
        span_on(newText, sent, sent.tokens[0])
        for token in sent.tokens:
            if token.content == u',':
                span_off(newText, sent, token)
            else:
                span_on(newText, sent, token)
                sent.spans[-1].tokens.append(token.content)
        span_off(newText, sent, sent.tokens[-1])

    for sent in newText.sentences:  # удаляем все вводные слова из разметки
        remove_inserted(sent)

    for sent in newText.sentences:  # соединяем отношением разорванные предикации
        for i in xrange(len(sent.spans)):
            if splitter(sent.spans, i):
                sent.relations.append((i, i+2))

    i = 0
    j = 0

    writeName = item[1].replace(u'txt', u'ann')
    w = codecs.open(writeName, 'w', 'utf-8')

    for sent in newText.sentences:
        for r in sent.relations:
            j += 1
            line = u'R' + str(j) + u'\t' + u'SplitSpan Arg1:T' + str(r[0]+i) + u' Arg2:T' + str(r[1]+i) + u'\t' + u'\n'
            w.write(line)
        for span in sent.spans:
            i += 1
            line = u'T' + str(i) + u'\t' + u'Span ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
            w.write(line)

    w.close()

w.close()

t2 = time.time()

print t2 - t1
