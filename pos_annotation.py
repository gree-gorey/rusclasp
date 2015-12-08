# -*- coding:utf-8 -*-
__author__ = 'Gree-gorey'

import time
from structures import Text, read_texts, word_on, word_off, sentence_on, sentence_off, append_char, write_pos_ann

t1 = time.time()

low_letters = u'абвгдеёжзийклмнопрструфхцчшщъыьэюя'
up_letters = low_letters.upper()
numbers = u'0123456789'

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

    for sent in newText.sentences:  # удаляем все вводные слова из разметки
        pass
        # print len(sent.spans)
        # for i in xrange(len(sent.spans)):
        #     if not conj(sent.spans[i].tokens[0]):
        #         print 1
        #         if not verb_in_span(sent.spans[i]):
        #             print 2
        #             w.write(sent.spans[i].content + u'\n')

    write_pos_ann(ann, item[1])

t2 = time.time()

print t2 - t1
