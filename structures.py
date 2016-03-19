# -*- coding:utf-8 -*-

import os
import re
import copy
import json
import codecs
import shutil
import treetaggerwrapper
# from pymystem3 import Mystem

__author__ = u'gree-gorey'


class Data:
    def __init__(self):
        self.t = treetaggerwrapper.TreeTagger(TAGLANG=u'ru')
        # self.m = Mystem(grammar_info=True, disambiguation=True, entire_input=True)

        # self.prepositions = json.load(codecs.open(u'./data/prepositions.json', u'r', u'utf-8'))
        self.complimentizers = json.load(codecs.open(u'./data/complimentizers.json', u'r', u'utf-8'))
        self.inserted = json.load(codecs.open(u'./data/inserted.json', u'r', u'utf-8'))
        self.predicates = json.load(codecs.open(u'./data/predicates.json', u'r', u'utf-8'))
        self.inserted_evidence = json.load(codecs.open(u'./data/inserted_evidence.json', u'r', u'utf-8'))
        self.complex_complimentizers = json.load(codecs.open(u'./data/complex_complimentizers.json', u'r', u'utf-8'))
        self.specificators = json.load(codecs.open(u'./data/specificators.json', u'r', u'utf-8'))
        self.conditional_complimentizers = [u'а', u'как', u'то есть']

myData = Data()


class Corpus:
    def __init__(self, path):
        self.path = path

    def texts(self, extension):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if extension in filename:
                    open_name = self.path + filename
                    with codecs.open(open_name, u'r', u'utf-8') as f:
                        if extension == u'json':
                            result = json.load(f)
                        else:
                            result = f.read()
                    yield Text(result, open_name)


class Text:
    def __init__(self, result, path):
        self.result = result
        self.path = path
        self.sentences = []
        self.sentence = False
        self.analysis = None

    def mystem_analyzer(self):
        self.result = self.result.replace(u' ', u' ')
        # self.analysis = myData.m.analyze(self.result)
        position = 0
        if self.analysis[-1][u'text'] == u'\n':
            del self.analysis[-1]
        for token in self.analysis:
            token[u'begin'] = position
            position += len(token[u'text'])
            token[u'end'] = position

    def treetagger_analyzer(self):
        # self.result = self.result.replace(u' ', u' ')
        self.result = re.sub(u'["«»‘’]', u'\'', self.result, flags=re.U)
        self.result = re.sub(u'(^|\. )\'(.+?)\'(, ?[—-])', u'\\1"\\2"\\3', self.result, flags=re.U)
        # print self.result
        self.analysis = myData.t.tag_text(self.result, tagblanks=True)
        # for item in self.analysis:
        #     print item
        position = 0
        new_analysis = []
        for token in self.analysis:
            if token[0] == u'<':
                # new_token[u'text'], new_token[u'gr'], new_token[u'lex'] = None, u'SPACE', None
                position += 1
            else:
                new_token = dict(begin=position)
                new_token[u'text'], new_token[u'gr'], new_token[u'lex'] = token.split(u'\t')
                position += len(new_token[u'text'])
                new_token[u'end'] = position
                new_analysis.append(new_token)
        self.analysis = new_analysis

    def sentence_on(self):
        if not self.sentence:
            self.sentence = True
            self.sentences.append(Sentence())

    def sentence_off(self):
        if self.sentence:
            self.sentence = False

    def sentence_splitter(self):
        for i, result in enumerate(self.result):
            self.sentence_on()
            if i == len(self.result)-1:
                self.add_token(result)
            elif i == len(self.result)-2:
                self.add_token(result, self.result[i+1])
            else:
                self.add_token(result, self.result[i+1], self.result[i+2])
            # self.add_token(result) if i == len(self.result)-1 else self.add_token(result, self.result[i+1])
            if self.end_of_sentence():
                # print self.result[i-1]['lex']
                self.sentence_off()
        self.sentence_off()

    def end_of_sentence(self):
        if self.sentences[-1].tokens[-1].pos == u'PERIOD':  # if it is a period
            # print 1
            if self.sentences[-1].tokens[-1].next_token_title:  # if the next token is uppercase
                # print 1
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
        if len(self.sentences[-1].tokens[-1].pos) > 1:
            if self.sentences[-1].tokens[-1].pos[1] == u'p':
                self.sentences[-1].after_name[0] = True
        if self.sentences[-1].tokens[-1].pos == u'-':
            if self.sentences[-1].tokens[-1].content[0].isalpha() and u'.' in self.sentences[-1].tokens[-1].content:
                self.sentences[-1].after_abbreviation = True
        else:
            self.sentences[-1].after_abbreviation = False

    def add_punctuation(self, token, next_token, token_after_next=None):
        if token[u'gr'] == u',':
            self.sentences[-1].tokens[-1].pos = u'COMMA'
            if len(self.sentences[-1].tokens) > 1:
                if self.sentences[-1].tokens[-2].content[-1].isdigit():
                    if next_token is not None:
                        if next_token[u'text'][0].isdigit():
                            self.sentences[-1].tokens[-1].pos = u'pseudoCOMMA'
        elif token[u'gr'] == u'-':
            if token[u'lex'] in u'-:;':
                self.sentences[-1].tokens[-1].pos = u'COMMA'
                self.sentences[-1].tokens[-1].lex = token[u'lex']
            elif token[u'lex'] in u'—':
                self.sentences[-1].tokens[-1].pos = u'pairCOMMA'
                self.sentences[-1].tokens[-1].lex = token[u'lex']
            elif token[u'lex'] in u'()':
                self.sentences[-1].tokens[-1].pos = u'pairCOMMA'
                self.sentences[-1].tokens[-1].lex = u'|'
            elif token[u'lex'] in u'\'':
                self.sentences[-1].tokens[-1].pos = u'QUOTE'
            else:
                self.sentences[-1].tokens[-1].pos = u'UNKNOWN'
                self.sentences[-1].tokens[-1].lex = token[u'lex']
        elif token[u'gr'] == u'SENT':
            self.add_period(next_token, token_after_next)

    def add_period(self, next_token, token_after_next=None):
        self.sentences[-1].tokens[-1].pos = u'PERIOD'
        if self.sentences[-1].after_abbreviation:
            self.sentences[-1].tokens[-1].after_abbreviation = True
        if next_token and token_after_next:
            if next_token[u'text'].replace(u'-', u'').istitle():
                # print next_token[u'text']
                self.sentences[-1].tokens[-1].next_token_title = True
                if next_token[u'gr'][0] == u'N':
                    if next_token[u'gr'][1] == u'p':
                        self.sentences[-1].tokens[-1].next_token_name = True
            elif next_token[u'text'] in u'\"\'' and token_after_next[u'text'].replace(u'-', u'').istitle():
                # print next_token[u'text']
                self.sentences[-1].tokens[-1].next_token_title = True
                if next_token[u'gr'][0] == u'N':
                    if next_token[u'gr'][1] == u'p':
                        self.sentences[-1].tokens[-1].next_token_name = True
        elif next_token:
            # print next_token[u'text']
            if next_token[u'text'].replace(u'-', u'').istitle():
                # print next_token[u'text']
                self.sentences[-1].tokens[-1].next_token_title = True
                if next_token[u'gr'][0] == u'N':
                    if next_token[u'gr'][1] == u'p':
                        self.sentences[-1].tokens[-1].next_token_name = True

                # elif next_token[u'gr'] == u'-':
                #     self.sentences[-1].tokens[-1].next_token_title = False

    def add_word(self, token, next_token):
        if u'.' in token[u'text']:
            if token[u'text'][:-1:].isdigit():
                self.sentences[-1].tokens[-1].pos = u'M'
                self.sentences[-1].tokens[-1].end -= 1
                self.sentences[-1].tokens.append(Token())
                self.sentences[-1].tokens[-1].begin = self.sentences[-1].tokens[-2].end
                self.sentences[-1].tokens[-1].end = self.sentences[-1].tokens[-1].begin + 1
            self.add_period(next_token)
        else:
            self.sentences[-1].tokens[-1].pos = token[u'gr']
            self.sentences[-1].tokens[-1].lex = token[u'lex']

    def add_token(self, token, next_token=None, token_after_next=None):
        self.sentences[-1].tokens.append(Token())
        self.sentences[-1].tokens[-1].begin = token[u'begin']
        self.sentences[-1].tokens[-1].end = token[u'end']
        self.sentences[-1].tokens[-1].content = token[u'text']
        if token[u'gr'][0].isalpha() and token[u'gr'] != u'SENT':
            self.add_word(token, next_token)
        else:
            self.add_punctuation(token, next_token, token_after_next)
        self.after_name()

    def write_clause_ann(self):
        i = 0
        j = 0

        write_name = self.path.replace(u'json', u'ann')
        w = codecs.open(write_name, u'w', u'utf-8')

        for sentence in self.sentences:
            for span in sentence.spans:
                if span.embedded:
                    i += 1
                    line = u'T' + str(i) + u'\t' + u'Embedded ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
                    w.write(line)
                elif span.inserted:
                    i += 1
                    line = u'T' + str(i) + u'\t' + u'Inserted ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
                    w.write(line)
                elif span.base:
                    i += 1
                    line = u'T' + str(i) + u'\t' + u'Base ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
                    w.write(line)
                span.entity_number = i
            for r in sentence.relations:
                j += 1
                line = u'R' + str(j) + u'\t' + u'Split Arg1:T' + str(sentence.spans[r[0]].entity_number) +\
                       u' Arg2:T' + str(sentence.spans[r[1]].entity_number) + u'\t' + u'\n'
                w.write(line)
            for r in sentence.verb_relations:
                # print sentence.spans[r[1]].entity_number
                j += 1
                line = u'R' + str(j) + u'\t' + u'Coordination Arg1:T' + str(sentence.spans[r[0]].entity_number) +\
                       u' Arg2:T' + str(sentence.spans[r[1]].entity_number) + u'\t' + u'\n'
                w.write(line)

        w.close()

    def write_pos_ann(self):
        name = self.path[:-3:] + u'json'
        w = codecs.open(name, u'w', u'utf-8')
        json.dump(self.analysis, w, ensure_ascii=False, indent=2)
        w.close()

    def copy_into_brat(self):
        text = self.path.replace(u'json', u'txt')
        ann = self.path.replace(u'json', u'ann')
        shutil.copy(text, u'/opt/brat-v1.3_Crunchy_Frog/data/right/' + text.split(u'/')[-1])
        shutil.copy(ann, u'/opt/brat-v1.3_Crunchy_Frog/data/right/' + ann.split(u'/')[-1])

    def normalize(self):
        self.result = self.result.replace(u' ', u' ')
        self.result = self.result.replace(u'\r\n', u' ')
        self.result = self.result.replace(u'\n', u' ')
        self.result = self.result.replace(u'…', u'...')
        self.result = re.sub(u'( |^)[A-Za-z]+?\.[A-Za-z].*?( |$)', u'\\1"Английское название"\\2', self.result,
                             flags=re.U)
        self.result = re.sub(u' +', u' ', self.result, flags=re.U)
        self.result = re.sub(u' $', u'', self.result, flags=re.U)
        # здесь былы реги для кавычек
        with codecs.open(self.path, u'w', u'utf-8') as w:
            w.write(self.result)


class Sentence:
    def __init__(self):
        self.tokens = []
        self.spans = []
        self.chunks = []
        self.relations = []
        self.verb_relations = []
        self.np = []
        self.pp = []
        self.after_name = [False, 0]
        self.after_abbreviation = False
        self.span = False
        self.quotes = False
        self.new_spans = []

    def contain_structure(self):
        for token in self.tokens:
            if token.lex == u'который':
                return True

    def add_token(self, token):
        self.spans[-1].tokens.append(token)

    def span_on(self):
        if not self.span:
            self.span = True
            self.spans.append(Span())
            if self.quotes:
                self.spans[-1].inside_quotes = True

    def span_off(self):
        if self.span:
            # print self.spans[-1].tokens[-1].content
            self.span = False
            if self.spans[-1].tokens[-1].content:
                if self.spans[-1].tokens[-1].content in u';()':
                    self.spans[-1].semicolon = True
                elif self.spans[-1].tokens[-1].content == u'—':
                    # print 1
                    self.spans[-1].before_dash = True
                elif self.spans[-1].tokens[-1].content == u':':
                    # print 1
                    self.spans[-1].before_colon = True

            if self.spans[-1].tokens[0].lex == u'—':
                self.spans[-1].tokens.pop(0)

            if len(self.spans[-1].tokens) > 0:
                self.spans[-1].tokens.pop()

            if len(self.spans[-1].tokens) < 1:
                self.spans.pop()

    def span_splitter(self):
        for token in self.tokens:
            if token.content != u'\"':
                self.span_on()
                self.add_token(token)
            else:
                if not self.quotes:
                    self.quotes = True
                else:
                    self.quotes = False
            if token.end_of_span():
                # print token.content
                self.span_off()
            # elif token.content != u'\"':
            #     self.span_on()
        self.span_off()

    def eliminate_pair_comma(self):
        predicate = False
        begin = {u'—': False, u'|': False, u'"': False}
        end = False
        left = None
        for i, token in enumerate(self.tokens):
            if token.pos == u'pairCOMMA' and not begin[token.lex]:
                left = i
                begin[token.lex] = True
                end = False
            elif token.pos[0] == u'V' and sum(begin.values()) > 0:
                predicate = True
            elif token.pos == u'pairCOMMA' and begin[token.lex]:
                right = i
                begin[token.lex] = False
                if predicate:
                    self.tokens[left].pos = self.tokens[right].pos = u'COMMA'
                predicate = False
                end = True
        if not end and left:
            self.tokens[left].pos = u'COMMA'

    def find_names(self):
        begin = False
        name = False
        for i, token in enumerate(self.tokens):
            if token.pos == u'QUOTE' and not begin:
                if len(self.tokens) > i+1:
                    if self.tokens[i+1].content.istitle():
                        name = True
                begin = True
            elif token.pos[0] == u'V' and begin:
                if name:
                    token.pos = u'insideNAME'
            elif token.pos == u'QUOTE' and begin:
                begin = False

    def get_shared_tokens(self):
        for span in self.spans:
            span.shared_tokens += span.tokens

    def split_double_complimentizers(self):
        new = []
        for span in self.spans:
            if len(span.tokens) > 1:
                if span.tokens[0].pos == u'C' and span.tokens[1].pos == u'C':
                    if span.tokens[0].lex in myData.complimentizers and span.tokens[1].lex in myData.complimentizers:
                        new_span = Span()
                        new_span.tokens += span.tokens[:1:]
                        span.tokens.pop(0)
                        new.append(new_span)
            new.append(span)
        self.spans = copy.deepcopy(new)

    def restore_embedded(self):
        for i, span in reversed(list(enumerate(self.spans))):
            if span.embedded:
                # print span.tokens[0].content, span.semicolon
                if not span.semicolon:
                    # print span.tokens[0].content
                    last_added = i
                    last_connected = i
                    last_connected_verb = i
                    for j, following_span in enumerate(self.spans[i+1::], start=i+1):
                        # print span.tokens[0].content, following_span.tokens[0].content
                        if not following_span.embedded and not following_span.in_embedded and not following_span.inserted:

                            if span.predicate_coordination(following_span):
                                # print following_span.tokens[0].content
                                # print last_connected, j
                                following_span.embedded = True
                                span.before_dash += following_span.before_dash
                                following_span.embedded_type = span.embedded_type
                                self.verb_relations.append((last_connected_verb, j))
                                last_connected_verb = j

                            else:

                                # если это НЕ примыкающий спан!!!
                                if j != last_added + 1:

                                    # если это спан СО СВЯЗЬЮ!!!
                                    if j != last_connected + 1:
                                        if span.accept_embedded(following_span):
                                            span.shared_tokens += following_span.tokens
                                            span.before_dash += following_span.before_dash
                                            following_span.embedded = True
                                            following_span.embedded_type = span.embedded_type
                                            self.relations.append((last_connected, j))
                                            last_connected = j
                                            # span.semicolon = following_span.semicolon
                                        else:
                                            break

                                    # если это ПРИМЫКАЮЩИЙ к висящему куску спан!!!
                                    else:
                                        # print span.tokens[0], 888
                                        # проверка на сочинение!
                                        if span.accept_embedded(following_span):
                                            self.spans[last_connected].tokens += following_span.tokens
                                            span.before_dash += following_span.before_dash
                                            following_span.in_embedded = True
                                            last_added = j
                                            # span.semicolon = following_span.semicolon
                                        else:
                                            break

                                # если это ПРИМЫКАЮЩИЙ спан!!!
                                else:
                                    # print following_span.tokens[0].content, 777
                                    # проверка на сочинение!
                                    # print span.accept_embedded(following_span), span.coordinate(following_span)
                                    if span.accept_embedded(following_span) and span.coordinate(following_span):
                                        span.before_dash += following_span.before_dash
                                        span.tokens += following_span.tokens
                                        span.shared_tokens += following_span.tokens
                                        following_span.in_embedded = True
                                        last_added = j
                                        # span.semicolon = following_span.semicolon
                                    else:
                                        break

                        elif following_span.embedded:
                            if span.incomplete():
                                if span.accept_embedded(following_span) and span.coordinate(following_span):
                                    span.before_dash += following_span.before_dash
                                    span.tokens += following_span.tokens
                                    span.shared_tokens += following_span.tokens
                                    following_span.in_embedded = True
                                    following_span.embedded = False
                                    last_added = j
                                    # span.semicolon = following_span.semicolon

                            if span.predicate_coordination(following_span):
                                # print following_span.tokens[0].content
                                # print last_connected, j
                                span.before_dash += following_span.before_dash
                                following_span.embedded_type = span.embedded_type
                                self.verb_relations.append((last_connected_verb, j))
                                last_connected_verb = j

                        if following_span.semicolon:
                            break

    def restore_base(self):
        for i, span in reversed(list(enumerate(self.spans))):
            if span.basic:
                # print span.tokens[1].content, span.finite()
                if not span.finite():
                    continue
                else:
                    # print span.tokens[1].content
                    self.join_base(span, i)

        for i, span in enumerate(self.spans):
            if span.basic and not span.base and not span.in_base:
                # print span.tokens[0].content
                self.join_base(span, i, False)

    def join_base(self, span, i, backward=True):
        switch = False
        span.base = True
        span.in_base = True
        last_added = i
        last_connected = i
        for j, following_span in enumerate(self.spans[i+1::], start=i+1):
            if span.finite() and following_span.finite():
                break
            if not backward:
                if following_span.basic and following_span.in_base is backward and following_span.base is backward:
                    # print span.tokens[0].content, following_span.tokens[0].content, 555, j

                    # если это ПРИМЫКАЮЩИЙ спан!!!
                    if j == last_added + 1:
                        # print span.tokens[0].content, following_span.tokens[0].content,
                        # span.accept_base(following_span), span.coordinate(following_span)
                        if span.accept_base(following_span) and span.coordinate(following_span):
                            # print span.tokens[0].content, following_span.tokens[0].content, 777, j
                            # print following_span.tokens[0].content, backward
                            span.tokens += following_span.tokens
                            span.shared_tokens += following_span.tokens
                            span.before_dash += following_span.before_dash
                            following_span.in_base = True
                            following_span.base = False
                            last_added = j
                            if span.before_dash:
                                span.null_copula = True
                            continue
            # print span.tokens[0].content, following_span.tokens[1].content, 111, following_span.base, backward
            if following_span.basic and following_span.in_base is not backward and following_span.base is not backward:
                # print span.tokens[0].content, following_span.tokens[0].content, 555, j

                switch = following_span.base

                # если это НЕ примыкающий спан!!!
                if j != last_added + 1:
                    # print span.tokens[0].content, following_span.tokens[0].content, 555, j

                    # если это спан СО СВЯЗЬЮ!!!
                    if j != last_connected + 1:
                        if span.accept_base(following_span):
                            span.shared_tokens += following_span.tokens
                            span.before_dash += following_span.before_dash
                            following_span.in_base = True
                            following_span.base = True
                            self.relations.append((last_connected, j))
                            last_connected = j

                    # если это ПРИМЫКАЮЩИЙ к висящему куску спан!!!
                    else:
                        # print span.tokens[0].content, following_span.tokens[0].content,
                        # span.accept_base(following_span), span.coordinate(following_span)
                        if span.accept_base(following_span) and span.coordinate(following_span):
                            # print span.tokens[0].content, following_span.tokens[0].content
                            self.spans[last_connected].tokens += following_span.tokens
                            span.before_dash += following_span.before_dash
                            following_span.in_base = True

                # если это ПРИМЫКАЮЩИЙ спан!!!
                else:
                    # print span.tokens[0].content, following_span.tokens[0].content,
                    # span.accept_base(following_span), span.coordinate(following_span)
                    if span.accept_base(following_span) and span.coordinate(following_span):
                        # print span.tokens[0].content, following_span.tokens[0].content, 777, j
                        # print following_span.tokens[0].content, backward
                        span.tokens += following_span.tokens
                        span.shared_tokens += following_span.tokens
                        span.before_dash += following_span.before_dash
                        following_span.in_base = True
                        following_span.base = False
                        last_added = j

            # if following_span.base:
            #     break

            if span.finite() and switch:
                # print span.tokens[0].content, 888
                break

    def split_embedded(self):
        find = False
        for span in self.spans:
            self.new_spans.append(span)
            if span.embedded:
                find_gerund = False
                if span.embedded_type == u'gerund':
                    if span.gerund > 1:
                        for i, token in reversed(list(enumerate(span.tokens))):
                            if len(token.pos) > 2:
                                if token.pos[0] == u'V':
                                    if token.pos[2] == u'g':
                                        find_gerund = True
                                        find += True
                            elif token.lex == u'и':
                                if find_gerund:
                                    if i > 0:
                                        new_span = Span()
                                        new_span.embedded = True
                                        new_span.embedded_type = span.embedded_type
                                        for following_token in span.tokens[i::]:
                                            new_span.tokens.append(following_token)
                                        self.new_spans[-1].tokens = span.tokens[:i:]
                                        self.new_spans.append(new_span)
                                        break
                else:
                    find += self.find_coordination(span)

        if find:
            self.spans = copy.deepcopy(self.new_spans)

    def split_base(self):
        self.new_spans = []
        find = False
        for span in self.spans:
            self.new_spans.append(span)
            if not span.embedded and not span.in_embedded and not span.inserted:
                # print span.tokens[0].content
                span.basic = True
                find += self.find_coordination(span)
        if find:
            # print self.new_spans
            self.spans = copy.deepcopy(self.new_spans)

    def find_coordination(self, span):
        and_number = len([True for token in span.tokens if token.lex == u'и'])
        predicate_number = len([True for token in span.tokens if token.predicate()])
        if predicate_number > 1:
            if and_number == 1:
                for i, token in reversed(list(enumerate(span.tokens))):
                    if token.lex == u'и':
                        if i > 0:
                            for j, following_token in enumerate(span.tokens[i+1::], start=i+1):
                                if following_token.lex == u'который':
                                    continue
                                if following_token.predicate():
                                    # print following_token.content
                                    new_span = copy.deepcopy(span)
                                    new_span.tokens = span.tokens[i::]
                                    new_span.shared_tokens = span.shared_tokens[i::]
                                    span.tokens = span.tokens[:i:]
                                    span.shared_tokens = span.shared_tokens[:i:]
                                    self.new_spans.append(new_span)
                                    return True

                                elif following_token.pos[0] != u'R':
                                    return False
            elif and_number > 1:
                for i, token in reversed(list(enumerate(span.tokens))):
                    if token.lex == u'и':
                        if i > 0:
                            left_span = Span()
                            left_span.tokens = left_span.shared_tokens = span.tokens[:i:]
                            right_span = Span()
                            right_span.tokens = right_span.shared_tokens = span.tokens[i+1::]
                            if left_span.coordinate(right_span):
                                # print left_span.tokens[-1].content, right_span.tokens[0].content
                                continue
                            else:
                                # print 1
                                for j, following_token in enumerate(span.tokens[i+1::], start=i+1):
                                    # if following_token.lex == u'который':
                                    #     continue
                                    if following_token.predicate():
                                        # print following_token.content
                                        new_span = copy.deepcopy(span)
                                        new_span.tokens = span.tokens[i::]
                                        new_span.shared_tokens = span.shared_tokens[i::]
                                        span.tokens = span.tokens[:i:]
                                        span.shared_tokens = span.shared_tokens[:i:]
                                        self.new_spans.append(new_span)
                                        return True

                                    # elif following_token.pos[0] != u'R':
                                    #     return False
        return False

    def find_complimentizers(self):
        for i, token in enumerate(self.tokens):
            if token.content.lower() in myData.complex_complimentizers:
                for item in myData.complex_complimentizers[token.content.lower()]:
                    end = i + item[1]
                    if len(self.tokens) >= end + 1:
                        new = [token]
                        j = i
                        while len(new) != item[1]:
                            j += 1
                            if u'COMMA' not in self.tokens[j].pos:
                                new.append(self.tokens[j])
                        new_complimentizer = u' '.join([next_token.content.lower() for next_token in new])

                        # print new_complimentizer_lex, 2
                        if new_complimentizer == item[0]:
                            # print new_complimentizer
                            token.content = new_complimentizer
                            token.lex = new_complimentizer
                            token.pos = u'C'
                            token.end = new[-1].end
                            for next_token in self.tokens[i+1:j+1:]:
                                self.tokens.remove(next_token)
                            if i != 0:
                                if u'COMMA' not in self.tokens[i-1].pos:
                                    new_comma = Token()
                                    new_comma.pos = u'COMMA'
                                    self.tokens.insert(i, new_comma)

    def find_np(self):
        match = -1
        for i, token in enumerate(self.tokens):
            if i > match:
                if not token.in_pp:
                    if token.is_adj():
                        # print self.tokens[i].content
                        for j, following_token in enumerate(self.tokens[i+1::], start=i+1):
                            # print self.tokens[j].content
                            if not following_token.in_pp:
                                if not following_token.in_np:
                                    # self.tokens[j].in_pp = True
                                    if following_token.pos == u'S':
                                        if token.agree_adj_noun(following_token):
                                            self.np.append([i, j])
                                            # print self.tokens[j].content
                                            for k in xrange(i, j+1):
                                                self.tokens[k].in_np = True
                                                match = j
                                            break

    def find_pp(self):
        for i, token in reversed(list(enumerate(self.tokens))):
            if token.pos[0] == u'S':
                # print token.content, u'\n'
                for j, following_token in enumerate(self.tokens[i+1::], start=i+1):
                    # print following_token.content, 555, following_token.in_pp
                    if not following_token.in_pp:
                        # print following_token.content, 777
                        if following_token.pos[0] in u'NP':
                            # print following_token.content, 888
                            if token.agree_pr_noun(following_token):
                                # print following_token.content
                                self.pp.append([i, j])
                                for inner_token in self.tokens[i: j+1]:
                                    print inner_token.content
                                    inner_token.in_pp = True
                                    if inner_token.pos == u'COMMA':
                                        inner_token.pos = u'pseudoCOMMA'
                                break

    def eliminate_and_disambiguate(self):
        pass
        # for pair in self.np:
        #     for token in self.tokens[pair[0]+1: pair[1]]:
        #         if token.pos == u'COMMA':
        #             token.pos = u'pseudoCOMMA'


class Span:
    def __init__(self):
        self.tokens = []
        self.shared_tokens = []
        self.begin = 0
        self.end = 0
        self.embedded = False
        self.in_embedded = False
        self.embedded_type = None
        self.base = False
        self.in_base = False
        self.basic = False
        self.inserted = False
        self.indicative = False
        self.gerund = 0
        self.relative = 0
        self.inside_quotes = False
        self.semicolon = False
        self.before_dash = False
        self.before_colon = False
        self.complement_type = None
        self.null_copula = False
        # self.finite = False

    def incomplete(self):
        if self.embedded_type == u'complement':
            return not self.finite()

    def predicate_coordination(self, following_span):
        # print self.shared_tokens[1].content, self.nominative(),
        # following_span.nominative(), following_span.shared_tokens[0].content
        if self.inside_quotes is following_span.inside_quotes:
            if not(self.nominative() and following_span.nominative()):
                if self.embedded_type and following_span.embedded_type:
                    if self.embedded_type != following_span.embedded_type:
                        return False
                    if self.embedded_type == u'complement':
                        if self.complement_type != following_span.complement_type:
                            return False
                for token in self.shared_tokens:
                    if token.predicate():
                        # print token.content
                        for other_token in following_span.tokens:
                            # if token.pos[0] == u'V' and other_token.pos[0] == u'V':
                                # print token.content
                            if token.coordinate(other_token):
                                # print token.content, other_token.content
                                return self.finite() is following_span.finite()
                                # return True

    def coordinate(self, following_span):
        # print following_span.tokens[0].lex, 111
        if following_span.tokens[0].lex in myData.specificators:
            # print following_span.tokens[0].lex
            return True
        if self.before_dash or self.before_colon:
            return True
        for token in reversed(self.shared_tokens):
            # print token.content, 9000
            if following_span.tokens[0].lex == u'как':
                return True
            if token.predicate():
                # print token.lex
                return False
            else:
                if following_span.find_right(token):
                    # print 777
                    # print token.lex
                    return True
                if token.lex == u'такой' and following_span.tokens[0].lex == u'как':
                    return True
                if following_span.tokens[0].lex == u'прежде всего':
                    return True

    def find_right(self, token):
        for token_right in self.shared_tokens:
            # print token.content, token_right.content, 888
            if token_right.predicate():
                return False
            else:
                if token.pos[0] in u'ANP' and token_right.pos[0] in u'ANP':
                    # print token.content, token_right.content
                    # print token.case(), token_right.case()
                    return token.case() == token_right.case()
                elif token.pos[0] == u'R' and token_right.pos[0] == u'R':
                    return True
        return False

    def type(self):
        if self.is_inserted():
            self.inserted = True
        if self.is_embedded():
            self.embedded = True

    def is_inserted(self):
        if len(self.tokens) < 10:
            if self.tokens[0].lex in [u'по', u'на']:
                if len(self.tokens) > 2:
                    if self.tokens[1].content in myData.inserted_evidence or self.tokens[2].content in myData.inserted_evidence:
                        return True
            if self.tokens[0].content.lower() in myData.inserted:
                # print self.tokens[0].content.lower()
                content = u''
                for token in self.tokens:
                    content += token.content.lower()
                    content += u' '
                for var in myData.inserted[self.tokens[0].content.lower()]:
                    if var == content[:-1:]:
                        return True

    def is_embedded(self):
        if not self.inserted:
            if self.tokens[0].pos[0] in u'CP':
                # print self.tokens[0].content
                if self.tokens[0].lex in myData.complimentizers:
                    if self.tokens[0].lex in myData.conditional_complimentizers:
                        # print self.tokens[0].lex, self.tokens[2].lex
                        if self.finite():
                            # print self.tokens[0].lex, self.tokens[2].lex, 777
                            self.embedded_type = u'complement'
                            self.complement_type = self.tokens[0].lex
                            return True
                        else:
                            return False
                    else:
                        self.embedded_type = u'complement'
                        self.complement_type = self.tokens[0].lex
                        return True

            for token in self.tokens:
                if token.lex == u'который':
                    self.relative += 1
                if len(token.pos) > 2:
                    if token.pos[0] == u'V':
                        if token.pos[2] == u'g':
                            self.gerund += 1
                        elif token.pos[2] == u'i':
                            self.indicative = True

            if self.tokens[0].lex == u'какой':
                self.embedded_type = u'relative'
                return True

            if self.gerund > 0 and not self.indicative:
                self.embedded_type = u'gerund'
                return True
            elif self.relative > 0:
                self.embedded_type = u'relative'
                return True

            for token in self.tokens:
                # print token.content, token.pos
                if token.pos[0] in u'CQR':
                    continue
                elif re.match(u'V.p.+', token.pos):
                    # print token.content, 777
                    if not self.finite():
                        self.embedded_type = u'participle'
                        return True
                else:
                    return False

    def accept_embedded(self, other):
        if self.inside_quotes is other.inside_quotes:
            if self.embedded_type == u'gerund' or self.embedded_type == u'participle':
                return not other.finite() and not other.nominative()
            elif self.embedded_type == u'relative' or self.embedded_type == u'complement':
                # print self.finite(), other.finite(), 111, other.tokens[0].content
                if not(self.finite() and other.finite()):
                    return not other.begin_with_and()
                else:
                    return False
        else:
            return False

    def accept_base(self, other):
        if self.inside_quotes is other.inside_quotes:
            return True
        else:
            return False

    def begin_with_and(self):
        return self.tokens[0].lex == u'и'

    def nominative(self):
        # print self.shared_tokens[1].content, 777
        for token in self.shared_tokens:
            if re.match(u'(N...n.)|(P....n.)|(M...[n-])', token.pos):
                # print token.content
                return True
        return False

    def finite(self):
        nominative = 0
        for i, token in enumerate(self.shared_tokens):
            # print u' '.join([token.content for token in self.shared_tokens])
            # print token.pos, token.content, 777
            if re.match(u'(V.[imc].......)|(V.p....ps.)|(A.....s)', token.pos):
                # print u' '.join([token.content for token in self.shared_tokens])
                return True
            elif re.match(u'V.n.......', token.pos) and self.shared_tokens[0].lex == u'чтобы':
                # print self.shared_tokens[0].content
                return True
            if token.lex in myData.predicates:
                # print self.shared_tokens[0].content
                return True
            if token.lex == u'—' or token.lex == u'-':
                # print u' '.join([token.content for token in self.shared_tokens]), token.content, token.lex
                self.null_copula = True
            elif token.lex == u'здесь':
                self.null_copula = True
            if re.match(u'(N...n.)|(P....n.)|(M...[n-])', token.pos):
                nominative += 1
                if len(self.shared_tokens[i+1::]) > 1:
                    if self.shared_tokens[i+1].lex == u'не':
                        if self.shared_tokens[i+2].pos[0] in u'NS':
                            return True
            if token.pos[0] == u'Q':
                # print token.content
                nominative += 1
        # print u' '.join([token.content for token in self.shared_tokens])
        if nominative > 1 and self.null_copula:
            # print u' '.join([token.content for token in self.shared_tokens])
            return True
        return False

    def get_boundaries(self):
        # if self.tokens:
        if self.tokens[0].content == u'\"':
            self.tokens.remove(self.tokens[0])
        self.begin = self.tokens[0].begin
        self.end = self.tokens[-1].end


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

    def case(self):
        if self.pos[0] == u'N':
            if self.pos[4] == u'n':
                return u'a'
            return self.pos[4]
        elif self.pos[0] in u'AP':
            return self.pos[5]
        return False

    def coordinate(self, other):
        # pos = zip(self.pos, other.pos)[1:3:] + zip(self.pos, other.pos)[4:7:]  # без учета времени
        if self.pos[0] == other.pos[0] == u'V':
            pos = zip(self.pos, other.pos)[1:7:] + zip(self.pos, other.pos)[8:9:]
            # print pos, self.content
        # elif self.pos[0] == u'A':
        else:
            # print self.content, other.content
            pos = zip(self.pos, other.pos)
            # print pos
        for item in pos:
            if u'-' in item:
                pass
            else:
                if item[0] != item[1]:
                    return False
        return True

    def predicate(self):
        # if re.match(u'(V.[imc].......)|(V.p....ps.)|(A.....s)', self.pos):
        if re.match(u'(V.[cim].......)|(V.p....ps.)|(A.....s)', self.pos):
            return True
        if self.lex in myData.predicates:
            return True
        return False

    def infinitive(self):
        if re.match(u'V.n.......', self.pos):
            return True
        return False

    def end_of_span(self):
        return self.pos == u'COMMA'

    def agree_pr_noun(self, noun):
        if noun.pos[0] == u'N':
            if self.pos[3] == noun.pos[4]:
                return True
        else:
            if self.pos[3] == noun.pos[5]:
                return True

    def is_adj(self):
        if self.pos == u'A':
            return True
        elif self.pos == u'V':
            for var in self.inflection:
                if u'прич' in var:
                    return True
