# -*- coding:utf-8 -*-

import os
import codecs
import json
from pymystem3 import Mystem

__author__ = 'Gree-gorey'

m = Mystem(grammar_info=True, disambiguation=True, entire_input=True)

# conj_list = [line.rstrip('\n') for line in codecs.open('/home/gree-gorey/Py/CourseWork/lists/conj.txt', 'r', 'utf-8')]
# ins = [line.rstrip('\n') for line in codecs.open('/home/gree-gorey/Py/CourseWork/lists/inserted.txt', 'r', 'utf-8')]


class Text:
    def __init__(self):
        self.sentences = []
        self.sentence = False

    def sentence_on(self):
        if not self.sentence:
            self.sentence = True
            self.sentences.append(Sentence())

    def sentence_off(self):
        if self.sentence:
            self.sentence = False

    def end_of_sentence(self):
        if self.sentences[-1].tokens[-1].pos == u'PERIOD':  # if it is a period
            if self.sentences[-1].tokens[-1].next_token_title:  # if the next token is uppercase
                if self.sentences[-1].tokens[-1].after_abbreviation:  # if the previous one is abbreviation
                    if self.sentences[-1].tokens[-1].next_token_name:  # if the next one in a name
                        if self.sentences[-1].tokens[-1].after_name:  # if one of the previous five tokens is a name
                            return True
                        else:
                            return False
                    else:
                        return True
                else:
                    return True
            else:
                return False
        return False

    def add_token(self, token, next_token=None):
        self.sentences[-1].tokens.append(Token())
        self.sentences[-1].tokens[-1].begin = token[u'begin']
        self.sentences[-1].tokens[-1].end = token[u'end']
        self.sentences[-1].tokens[-1].content = token[u'text']
        if u'analysis' in token:
            if token[u'analysis']:
                self.sentences[-1].tokens[-1].pos = token[u'analysis'][0][u'gr']
            else:
                self.sentences[-1].tokens[-1].pos = u'UNKNOWN'
        else:
            if token[u'text'] == u' ':
                self.sentences[-1].tokens[-1].pos = u'SPACE'
            else:
                if u',' in token[u'text']:
                    self.sentences[-1].tokens[-1].pos = u'COMMA'
                elif u'.' in token[u'text']:
                    self.sentences[-1].tokens[-1].pos = u'PERIOD'
                    if self.sentences[-1].after_abbreviation:
                        self.sentences[-1].tokens[-1].after_abbreviation = True
                    if next_token is not None:
                        if next_token[u'text'].istitle():
                            self.sentences[-1].tokens[-1].next_token_title = True
                            if u'analysis' in next_token:
                                if next_token[u'analysis'] is not []:
                                    if u'фам' in next_token[u'analysis'][0][u'gr']:
                                        self.sentences[-1].tokens[-1].next_token_name = True
                                    if u'сокр' in next_token[u'analysis'][0][u'gr']:
                                        self.sentences[-1].tokens[-1].next_token_title = False
                else:
                    self.sentences[-1].tokens[-1].pos = u'PUNCT'
        if self.sentences[-1].after_name[0]:
            if self.sentences[-1].after_name[1] <= 5:
                self.sentences[-1].tokens[-1].after_name = True
            else:
                self.sentences[-1].after_name = [False, 0]
            self.sentences[-1].after_name[1] += 1
        if u'фам' in self.sentences[-1].tokens[-1].pos:
            self.sentences[-1].after_name[0] = True
        if u'сокр' in self.sentences[-1].tokens[-1].pos:
            self.sentences[-1].after_abbreviation = True
        else:
            self.sentences[-1].after_abbreviation = False


class Sentence:
    def __init__(self):
        self.tokens = []
        self.spans = []
        self.relations = []
        self.after_name = [False, 0]
        self.after_abbreviation = False
        self.span = False

    def span_on(self, token):
        if not self.span:
            self.span = True
            self.spans.append(Span())
            self.spans[-1].begin = token.begin

    def span_off(self, token):
        if self.span:
            self.span = False
            self.spans[-1].end = token.end
            # self.spans[-1].content = u''.join(self.spans[-1].tokens)


class Token:
    def __init__(self):
        self.content = u''
        self.pos = u''
        self.begin = 0
        self.end = 0
        self.after_name = False
        self.after_abbreviation = False
        self.next_token_title = False
        self.next_token_name = False

    def end_of_span(self):
        return self.pos == u'COMMA'


class Span:
    def __init__(self):
        self.tokens = []


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


def write_clause_ann(text, path):
    i = 0
    j = 0

    write_name = path.replace(u'json', u'ann')
    w = codecs.open(write_name, 'w', 'utf-8')

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