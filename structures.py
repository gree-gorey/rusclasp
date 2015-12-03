# -*- coding:utf-8 -*-
__author__ = 'Gree-gorey'

import os, codecs, re

conj = [line.rstrip('\n') for line in codecs.open('/home/gree-gorey/Py/CourseWork/lists/conj.txt', 'r', 'utf-8')]
ins = [line.rstrip('\n') for line in codecs.open('/home/gree-gorey/Py/CourseWork/lists/inserted.txt', 'r', 'utf-8')]

class Text:
    def __init__(self):
        self.sentences = []
        self.sentence = False
        self.word = False
        self.span = False


class Sentence:
    def __init__(self):
        self.begin = 0
        self.end = 0
        self.tokens = []
        self.spans = []
        self.relations = []


class Token:
    def __init__(self):
        self.content = u''
        self.begin = 0
        self.end = 0


class Span:
    def __init__(self):
        self.content = u''
        self.begin = 0
        self.end = 0
        self.tokens = []


def append_char(text, char, i):
    if len(text.sentences) != 0:
        text.sentences[-1].tokens.append(Token())
        text.sentences[-1].tokens[-1].begin = i
        text.sentences[-1].tokens[-1].end = i
        text.sentences[-1].tokens[-1].content = char


def word_on(text, i):
    if text.word is False:
        text.word = True
        text.sentences[-1].tokens.append(Token())
        text.sentences[-1].tokens[-1].begin = i


def word_off(text, i, item):
    if text.word is True:
        text.word = False
        text.sentences[-1].tokens[-1].end = i-1
        text.sentences[-1].tokens[-1].content = item[0][text.sentences[-1].tokens[-1].begin:
                                                   text.sentences[-1].tokens[-1].end+1:]


def span_on(text, sent, token):
    if text.span is False:
        text.span = True
        sent.spans.append(Span())
        sent.spans[-1].begin = token.begin


def span_off(text, sent, token):
    if text.span is True:
        text.span = False
        sent.spans[-1].end = token.end
        sent.spans[-1].content = u' '.join(sent.spans[-1].tokens)


def sentence_on(text, i):
    if text.sentence is False:
        text.sentence = True
        text.sentences.append(Sentence())
        text.sentences[-1].begin = i


def sentence_off(text, i):
    if text.sentence is True:
        text.sentence = False
        text.sentences[-1].end = i


def splitter(spans, i):
    if i < xrange(len(spans)):
        if spans[i].tokens[0].lower()[:5:] == u'котор' and spans[i+1].tokens[0].lower() not in conj:
            return True


def inserted(span):
    if span.content.lower() in ins:
        return True


def remove_inserted(sent):
    newSpans = []
    ins = False
    for i in xrange(len(sent.spans)):
        if inserted(sent.spans[i]):
            if i != 0 and i != len(sent.spans):
                newSpan = Span()
                newSpan.begin = sent.spans[i-1].begin
                newSpan.end = sent.spans[i+1].end
                newSpan.tokens = sent.spans[i-1].tokens + sent.spans[i+1].tokens
                newSpans.pop()
                newSpans.append(newSpan)
                ins = True
        else:
            if not ins:
                newSpans.append(sent.spans[i])
            ins = False
    sent.spans = newSpans


def if_verb(token):
    end = u'(ть|ти|чь)(ся|сь)?$'
    abstr = u'ост.$'
    if re.search(end, token, flags=re.U):
        if not re.search(abstr, token, flags=re.U):
            return True


def read_texts():
    for root, dirs, files in os.walk(u'/opt/brat-v1.3_Crunchy_Frog/data/right/collection'):
        for filename in files:
            if u'txt' in filename:
                open_name = u'/opt/brat-v1.3_Crunchy_Frog/data/right/collection/' + filename
                f = codecs.open(open_name, 'r', 'utf-8')
                text = f.read()
                f.close()
                yield text, open_name

# /home/gree-gorey/Py/CourseWork/corpus/
# /opt/brat-v1.3_Crunchy_Frog/data/right/collection/'
# /opt/brat-v1.3_Crunchy_Frog/data/right/all/