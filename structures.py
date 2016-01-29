# -*- coding:utf-8 -*-

import os
import codecs
import json
import copy
from pymystem3 import Mystem

__author__ = u'Gree-gorey'

m = Mystem(grammar_info=True, disambiguation=True, entire_input=True)

prepositions = json.load(codecs.open(u'prepositions.json', u'r', u'utf-8'))
complimentizers = json.load(codecs.open(u'complimentizers.json', u'r', u'utf-8'))


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

    def sentence_splitter(self, item):
        for i in xrange(len(item[0])):
            self.sentence_on()
            self.add_token(item[0][i]) if i == len(item[0])-1 else self.add_token(item[0][i], item[0][i+1])
            if self.end_of_sentence():
                self.sentence_off()
        self.sentence_off()

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

    def after_name(self):
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

    def add_punctuation(self, token, next_token):
        if token[u'text'] == u' ':
            self.sentences[-1].tokens[-1].pos = u'SPACE'
        else:
            if u',' in token[u'text']:
                self.sentences[-1].tokens[-1].pos = u'COMMA'
                if len(self.sentences[-1].tokens) > 1:
                    if self.sentences[-1].tokens[-2].content.isdigit():
                        if next_token is not None:
                            if next_token[u'text'].isdigit():
                                self.sentences[-1].tokens[-1].pos = u'pseudoCOMMA'
            elif u'.' in token[u'text']:
                self.sentences[-1].tokens[-1].pos = u'PERIOD'
                if self.sentences[-1].after_abbreviation:
                    self.sentences[-1].tokens[-1].after_abbreviation = True
                if next_token is not None:
                    if next_token[u'text'].istitle() or next_token[u'text'] == u'\"':
                        self.sentences[-1].tokens[-1].next_token_title = True
                        if u'analysis' in next_token:
                            if next_token[u'analysis'] is not []:
                                if u'фам' in next_token[u'analysis'][0][u'gr']:
                                    self.sentences[-1].tokens[-1].next_token_name = True
                                if u'сокр' in next_token[u'analysis'][0][u'gr']:
                                    self.sentences[-1].tokens[-1].next_token_title = False
            else:
                self.sentences[-1].tokens[-1].pos = u'MARK'

    def add_word(self, token):
        if token[u'analysis']:
            analysis = token[u'analysis'][0][u'gr'].split(u'=')
            constant = analysis[0].split(u',')
            self.sentences[-1].tokens[-1].pos = constant[0]
            self.sentences[-1].tokens[-1].lex = token[u'analysis'][0][u'lex']
            if len(analysis) > 1:
                analysis[1] = analysis[1].replace(u'(', u'')
                analysis[1] = analysis[1].replace(u')', u'')
                self.sentences[-1].tokens[-1].inflection = copy.deepcopy(
                        [x.split(u',') for x in analysis[1].split(u'|')])
            if self.sentences[-1].tokens[-1].pos == u'S':
                self.sentences[-1].tokens[-1].gender = constant[-2]
                if constant[1] in u'мнед':
                    for var in self.sentences[-1].tokens[-1].inflection:
                        var.append(constant[1])
            if self.sentences[-1].tokens[-1].pos == u'PR':
                if token[u'analysis'][0][u'lex'] in prepositions:
                    # print prepositions[token[u'analysis'][0][u'lex']][0]
                    self.sentences[-1].tokens[-1].inflection = copy.deepcopy(
                            prepositions[token[u'analysis'][0][u'lex']])
        else:
            self.sentences[-1].tokens[-1].pos = u'UNKNOWN'

    def add_token(self, token, next_token=None):
        self.sentences[-1].tokens.append(Token())
        self.sentences[-1].tokens[-1].begin = token[u'begin']
        self.sentences[-1].tokens[-1].end = token[u'end']
        self.sentences[-1].tokens[-1].content = token[u'text']
        if u'analysis' in token:
            self.add_word(token)
        else:
            self.add_punctuation(token, next_token)
        self.after_name()


class Sentence:
    def __init__(self):
        self.tokens = []
        self.spans = []
        self.chunks = []
        self.relations = []
        self.np = []
        self.pp = []
        self.after_name = [False, 0]
        self.after_abbreviation = False
        self.span = False

    def contain_structure(self):
        for token in self.tokens:
            for var in token.inflection:
                if u'деепр' in var:
                    return True

    def add_token(self, token):
        self.spans[-1].tokens.append(token)

    def span_on(self, token):
        if not self.span:
            self.span = True
            self.spans.append(Span())
            self.spans[-1].begin = token.begin

    def span_off(self):
        if self.span:
            self.span = False
            self.spans[-1].tokens.pop()
            self.spans[-1].end = self.spans[-1].tokens[-1].end
            # self.spans[-1].content = u''.join(self.spans[-1].tokens)

    def span_splitter(self):
        for token in self.tokens:
            self.span_on(token)
            self.add_token(token)
            if token.end_of_span():
                self.span_off()
            else:
                self.span_on(token)
        self.span_off()

    def restore_alpha(self):
        for j in xrange(len(self.spans)-1, -1, -1):
            if self.spans[j].alpha:
                last_added = j
                for k in xrange(j+1, len(self.spans)):
                    if not self.spans[k].alpha and not self.spans[k].in_alpha:
                        if self.spans[k].accept_alpha():
                            if k != last_added+1:
                                self.spans[k].alpha = True
                                self.relations.append((j, k))
                            else:
                                self.spans[j].tokens += self.spans[k].tokens
                                self.spans[k].in_alpha = True
                                last_added = k
                        else:
                            break

    def restore_beta(self):
        for j in xrange(len(self.spans)):
            if not self.spans[j].alpha and not self.spans[j].in_alpha and not self.spans[j].in_beta:
                self.spans[j].beta = True
                for k in xrange(j+1, len(self.spans)):
                    if self.spans[k].accept_beta():
                        if k != j+1:
                            self.spans[k].beta = True
                            self.relations.append((j, k))
                        else:
                            self.spans[j].tokens += self.spans[k].tokens
                            self.spans[k].in_beta = True

    def find_np(self):
        match = -1
        for i in xrange(len(self.tokens)):
            if i > match:
                if not self.tokens[i].in_pp:
                    if self.tokens[i].is_adj():
                        # print self.tokens[i].content
                        for j in xrange(i+1, len(self.tokens)):
                            # print self.tokens[j].content
                            if not self.tokens[j].in_pp:
                                if not self.tokens[j].in_np:
                                    # self.tokens[j].in_pp = True
                                    if self.tokens[j].pos == u'S':
                                        if self.tokens[i].agree_adj_noun(self.tokens[j]):
                                            self.np.append([i, j])
                                            # print self.tokens[j].content
                                            for k in xrange(i, j+1):
                                                self.tokens[k].in_np = True
                                                match = j
                                            break

    def find_pp(self):
        for i in xrange(len(self.tokens)-1, -1, -1):
            if self.tokens[i].pos == u'PR':
                # print self.tokens[i].content
                for j in xrange(i+1, len(self.tokens)):
                    # print self.tokens[j].content
                    if not self.tokens[j].in_pp:
                        self.tokens[j].in_pp = True
                        if self.tokens[j].pos == u'S':
                            if self.tokens[i].agree_pr_noun(self.tokens[j]):
                                self.pp.append([i, j])
                                # print self.tokens[j].content
                                break

    def eliminate_and_disambiguate(self):
        for pair in self.np:
            for token in self.tokens[pair[0]+1: pair[1]]:
                if token.pos == u'COMMA':
                    token.pos = u'pseudoCOMMA'
        for pair in self.pp:
            for token in self.tokens[pair[0]+1: pair[1]]:
                if token.pos == u'COMMA':
                    token.pos = u'pseudoCOMMA'
                elif token.pos == u'S':
                    if len(token.inflection) > 1:
                        new_inflection = []
                        for var in token.inflection:
                            if u'им' not in var:
                                new_inflection.append(var)
                        token.inflection = new_inflection


class Token:
    def __init__(self):
        self.content = u''
        self.lex = u''
        self.pos = u''
        self.inflection = []
        self.gender = u''
        self.begin = 0
        self.end = 0
        self.after_name = False
        self.after_abbreviation = False
        self.next_token_title = False
        self.next_token_name = False
        self.in_pp = False
        self.in_np = False

    def end_of_span(self):
        return self.pos == u'COMMA'

    def agree_adj_noun(self, other):
        for varI in self.inflection:
            if other.gender in varI or u'мн' in varI:
                for varJ in other.inflection:
                    try:
                        if varJ[0] in varI and varJ[1] in varI:
                            return True
                    except:
                        print varJ[0], other.content

    def agree_pr_noun(self, other):
        for var in other.inflection:
            if var[0] in self.inflection:
                return True

    def is_adj(self):
        if self.pos == u'A':
            return True
        elif self.pos == u'V':
            for var in self.inflection:
                if u'прич' in var:
                    return True


class Span:
    def __init__(self):
        self.tokens = []
        self.begin = 0
        self.end = 0
        self.alpha = False
        self.in_alpha = False
        self.alpha_type = None
        self.beta = False
        self.in_beta = False

    def type(self):
        if self.is_alpha():
            self.alpha = True

    def is_alpha(self):
        if self.tokens[0].lex in complimentizers:
            self.alpha_type = u'complement'
            return True
        else:
            for token in self.tokens:
                if token.lex == u'который':
                    self.alpha_type = u'relative'
                    return True
                else:
                    for var in token.inflection:
                        if u'прич' in var and u'полн' in var:
                            self.alpha_type = u'participle'
                            return True
                        elif u'деепр' in var:
                            self.alpha_type = u'adverbial'
                            return True

    def accept_alpha(self):
        if self.alpha_type == u'adverbial' or self.alpha_type == u'participle':
            return self.infinite()
        elif self.alpha_type == u'relative' or self.alpha_type == u'complement':
            return self.finite()

    def infinite(self):
        for token in self.tokens:
            if token.pos == u'V':
                for var in token.inflection:
                    if u'инф' not in var and u'прич' not in var:
                        return False
            elif token.pos == u'S':
                for var in token.inflection:
                    if u'им' in var:
                        return False

    def finite(self):
        for token in self.tokens:
            if token.pos == u'V':
                for var in token.inflection:
                    if u'инф' not in var and u'прич' not in var:
                        return False
            elif token.pos == u'S':
                for var in token.inflection:
                    if u'им' in var:
                        return False

    def accept_beta(self):
        for token in self.tokens:
            if u'V' in token.pos:
                return True

    def get_boundaries(self):
        if self.alpha or self.beta:
            self.begin = self.tokens[0].begin
            self.end = self.tokens[-1].end

    def clear_boundaries(self):
        if self.tokens[0].content == u'\"':
            self.tokens.remove(self.tokens[0])
            self.begin = self.tokens[0].begin


def inserted(span):
    if span.content.lower() in ins:
        return True


def remove_inserted(sent):
    new_spans = []
    ins = False
    for i in xrange(len(sent.spans)):
        if inserted(sent.spans[i]):
            if i != 0 and i != len(sent.spans):
                new_span = Span()
                new_span.begin = sent.spans[i-1].begin
                new_span.end = sent.spans[i+1].end
                new_span.tokens = sent.spans[i-1].tokens + sent.spans[i+1].tokens
                new_spans.pop()
                new_spans.append(new_span)
                ins = True
        else:
            if not ins:
                new_spans.append(sent.spans[i])
            ins = False
    sent.spans = new_spans


def write_clause_ann(text, path):
    i = 0
    # j = 0

    write_name = path.replace(u'json', u'ann')
    w = codecs.open(write_name, u'w', u'utf-8')

    for sent in text.sentences:
        # for r in sent.relations:
        #     j += 1
        #     line = u'R' + str(j) + u'\t' + u'SplitSpan Arg1:T' + str(r[0]+i) + u' Arg2:T' + str(r[1]+i) + u'\t' + u'\n'
        #     w.write(line)
        for span in sent.spans:
            if span.alpha or span.beta:
                i += 1
                line = u'T' + str(i) + u'\t' + u'Span ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
                w.write(line)

    w.close()


def write_pos_ann(ann, path):
    name = path[:-3:] + u'json'
    w = codecs.open(name, u'w', u'utf-8')
    json.dump(ann, w, ensure_ascii=False, indent=2)
    w.close()


def write_brat_ann(text, path):
    name = path[:-4:] + u'ann'
    w = codecs.open(name, u'w', u'utf-8')
    i = 1
    for sent in text.sentences:
        for pp in sent.pp:
            w.write(u'T' + str(i) + u'\tSpan ' + str(sent.tokens[pp[0]].begin) + u' ' + str(sent.tokens[pp[1]].end) +
                    u'\n')
            i += 1
        for np in sent.np:
            w.write(u'T' + str(i) + u'\tSpan ' + str(sent.tokens[np[0]].begin) + u' ' + str(sent.tokens[np[1]].end) +
                    u'\n')
            i += 1
    w.close()


def write_brat_sent(text, path):
    name = path[:-4:] + u'ann'
    w = codecs.open(name, u'w', u'utf-8')
    i = 1
    for sentence in text.sentences:
        w.write(u'T' + str(i) + u'\tSpan ' + str(sentence.tokens[0].begin) + u' ' + str(sentence.tokens[-2].end) +
                u'\t' + u'\n')
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

# /home/gree-gorey/Corpus/
# /opt/brat-v1.3_Crunchy_Frog/data/right/collection/'
