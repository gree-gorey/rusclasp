# -*- coding:utf-8 -*-
__author__ = 'Gree-gorey'

import os
import codecs
import json
from pymystem3 import Mystem

m = Mystem(grammar_info=True, disambiguation=True, entire_input=True)

# conj_list = [line.rstrip('\n') for line in codecs.open('/home/gree-gorey/Py/CourseWork/lists/conj.txt', 'r', 'utf-8')]
# ins = [line.rstrip('\n') for line in codecs.open('/home/gree-gorey/Py/CourseWork/lists/inserted.txt', 'r', 'utf-8')]


class Text:
    def __init__(self):
        self.sentences = []
        self.sentence = False
        self.word = False
        self.span = False


class Sentence:
    def __init__(self):
        self.tokens = []
        self.spans = []
        self.relations = []


class Token:
    def __init__(self):
        self.content = u''
        self.pos = u''
        self.begin = 0
        self.end = 0


class Span:
    def __init__(self):
        self.tokens = []


def add_token(text, token):
    text.sentences[-1].tokens.append(Token())
    text.sentences[-1].tokens[-1].begin = token[u'begin']
    text.sentences[-1].tokens[-1].end = token[u'end']
    text.sentences[-1].tokens[-1].content = token[u'text']
    if u'analysis' in token:
        text.sentences[-1].tokens[-1].pos = u'temp' # token[u'analysis'][0][u'gr']
    else:
        if token[u'text'] == u' ':
            text.sentences[-1].tokens[-1].pos = u'SPACE'
        else:
            if u',' in token[u'text']:
                text.sentences[-1].tokens[-1].pos = u'COMMA'
            elif u'.' in token[u'text']:
                text.sentences[-1].tokens[-1].pos = u'PERIOD'
            else:
                text.sentences[-1].tokens[-1].pos = u'PUNCT'


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


def sentence_on(text):
    if text.sentence is False:
        text.sentence = True
        text.sentences.append(Sentence())


def sentence_off(text):
    if text.sentence is True:
        text.sentence = False


def end_of_sentence(pre_token, token, post_token):
    if u'analysis' not in token and u'text' in token:
        if u'.' in token[u'text']:
            if u'analysis' in pre_token and u'analysis' in post_token:
                if u'сокр' in pre_token[u'analysis'][0][u'gr']:
                    return False
                else:
                    return True
    else:
        return False



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


def conj(token):
    if token in conj_list:
        return True


def verb_in_span(span):
    pos = tt.tag(span.content)
    for token in pos:
        if token[1][0] == u'V':
            return True


def write_clause_ann(text, path):
    i = 0
    j = 0

    writeName = path.replace(u'txt', u'ann')
    w = codecs.open(writeName, 'w', 'utf-8')

    for sent in text.sentences:
        for r in sent.relations:
            j += 1
            line = u'R' + str(j) + u'\t' + u'SplitSpan Arg1:T' + str(r[0]+i) + u' Arg2:T' + str(r[1]+i) + u'\t' + u'\n'
            w.write(line)
        for span in sent.spans:
            i += 1
            line = u'T' + str(i) + u'\t' + u'Span ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
            w.write(line)

    w.close()


def write_pos_ann(ann, path):
    name = path[:-3:] + u'json'
    w = codecs.open(name, u'w', u'utf-8')
    json.dump(ann, w, ensure_ascii=False, indent=2)
    w.close()


def write_brat_ann(ann, path):
    name = path[:-3:] + u'ann'
    w = codecs.open(name, u'w', u'utf-8')
    i = 1
    for token in ann:
        w.write(u'T' + str(i) + u'\tSpan ' + str(token[u'begin']) + u' ' + str(token[u'end']) + u'\t' + token[u'text'] + u'\n')
        i += 1
    w.close()


def write_brat_sent(text, path):
    name = path[:-4:] + u'ann'
    w = codecs.open(name, u'w', u'utf-8')
    i = 1
    for sentence in text.sentences:
        w.write(u'T' + str(i) + u'\tSpan ' + str(sentence.tokens[0].begin) + u' ' + str(sentence.tokens[-2].end) + u'\t' + u'\n')
        i += 1
    w.close()


def pos_analyzer(text):
    analysis = m.analyze(text)
    position = 0
    if analysis[-1][u'text'] == u'\n':
        del analysis[-1]
    for token in analysis:
        token[u'begin'] = position
        position += len(token[u'text'])
        token[u'end'] = position
    return analysis


def read_texts(extension, path):
    for root, dirs, files in os.walk(path):
        for filename in files:
            if extension in filename:
                open_name = path + filename
                f = codecs.open(open_name, u'r', u'utf-8')
                if extension == u'json':
                    result = json.load(f)
                else:
                    result = f.read()
                f.close()
                yield result, open_name

# /home/gree-gorey/Py/CourseWork/corpus/
# /home/gree-gorey/Corpus/
# /opt/brat-v1.3_Crunchy_Frog/data/right/collection/'
# /opt/brat-v1.3_Crunchy_Frog/data/right/all/