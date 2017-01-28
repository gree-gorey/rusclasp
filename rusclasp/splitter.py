# -*- coding:utf-8 -*-

import os
import re
import copy
import json
import codecs
import shutil
import treetaggerwrapper

__author__ = u'gree-gorey'


class Data:
    def __init__(self):
        self.t = treetaggerwrapper.TreeTagger(TAGLANG=u'ru')

        self.path = os.path.dirname(os.path.abspath(__file__))

        self.complimentizers = json.load(codecs.open(self.path + u'/data/complimentizers.json', u'r', u'utf-8'))
        self.inserted = json.load(codecs.open(self.path + u'/data/inserted.json', u'r', u'utf-8'))
        self.predicates = json.load(codecs.open(self.path + u'/data/predicates.json', u'r', u'utf-8'))
        self.inserted_evidence = json.load(codecs.open(self.path + u'/data/inserted_evidence.json', u'r', u'utf-8'))
        self.complex_complimentizers = json.load(codecs.open(self.path + u'/data/complex_complimentizers.json', u'r',
                                                             u'utf-8'))
        self.specificators = json.load(codecs.open(self.path + u'/data/specificators.json', u'r', u'utf-8'))
        self.conditional_complimentizers = [u'а', u'как', u'то есть', u'а также']

myData = Data()


class Splitter:
    def __init__(self):
        self.result = dict()

    def split(self, string, mode=u'json'):
        # создаем экземпляр класса текст
        text = Text(string)
        # нормализуем и записываем результат в JSON
        text.normalize()
        self.result[u'text'] = text.result
        # делаем pos-tagging
        text.treetagger_analyzer()
        # это так надо чтобы не переделывать весь код
        text.result = text.analysis
        # разбиваем текст на предложения
        text.sentence_splitter()
        # обходим предложения
        for sentence in text.sentences:
            # разбиваем предложение на предикации
            sentence.split()
        # создаем JSON с результатом
        text.get_json(self.result)
        # возвращаем результат
        return self.result


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

    def size(self):
        tokens = 0
        for text in self.texts(u'json'):
            tokens += len(text.result)
        return tokens


class PairCorpora:
    def __init__(self, path_to_gold, path_to_tested):
        self.path_to_gold = path_to_gold
        self.path_to_tested = path_to_tested
        self.texts = []
        self.precision = 0
        self.recall = 0
        self.f_value = 0
        self.match = 0
        self.length_gold = 0
        self.length_tested = 0

    def annotations(self):
        for root, dirs, files in os.walk(self.path_to_tested):
            for filename in files:
                if u'.ann' in filename:
                    open_name_gold = self.path_to_gold + filename
                    open_name_tested = self.path_to_tested + filename
                    open_name_json = self.path_to_tested + filename.replace(u'ann', u'json')
                    with codecs.open(open_name_gold, u'r', u'utf-8') as f:
                        ann_gold = f.readlines()
                    with codecs.open(open_name_tested, u'r', u'utf-8') as f:
                        ann_tested = f.readlines()
                    with codecs.open(open_name_json, u'r', u'utf-8') as f:
                        tokens = json.load(f)
                    yield EvaluatedText(ann_gold, ann_tested, tokens)

    def evaluate(self):
        for text in self.texts:
            self.match += text.match
            self.length_gold += len(text.spans_gold)
            self.length_tested += len(text.spans_tested)
        self.precision = float(self.match) / float(self.length_tested)
        self.recall = float(self.match) / float(self.length_gold)
        self.f_value = (self.precision + self.recall) / 2


class EvaluatedText:
    def __init__(self, ann_gold, ann_tested, tokens):
        self.ann_gold = ann_gold
        self.ann_tested = ann_tested
        self.tokens = tokens
        self.spans_gold = []
        self.spans_tested = []
        self.relations_gold = []
        self.relations_tested = []
        self.match = 0

    def count_match(self):
        for span_gold in self.spans_gold:
            for span_tested in self.spans_tested:
                if span_gold.tokens == span_tested.tokens:
                    self.match += 1
                    break

    def restore_split(self):
        for r in sorted(self.relations_gold, reverse=True):
            self.find_relation(r, self.spans_gold)

        for r in sorted(self.relations_tested, reverse=True):
            self.find_relation(r, self.spans_tested)

    def find_relation(self, r, spans):
        for span in spans:
            if span.entity_number == r[0]:
                for following_span in spans:
                    if following_span.entity_number == r[1]:
                        span.tokens += following_span.tokens
                        spans.remove(following_span)
                        return

    def get_spans(self):
        for span in self.spans_generator(self.ann_gold):
            self.spans_gold.append(span)

        for span in self.spans_generator(self.ann_tested):
            self.spans_tested.append(span)

    def spans_generator(self, annotation):
        for line in annotation:
            line = line.split(u'\t')
            if line[0][0] == u'T':
                new_span = Span()
                new_span.entity_number = int(line[0][1::])
                coordinates = line[1].split(u' ')
                new_span.begin = int(coordinates[1])
                new_span.end = int(coordinates[2])
                # print new_span.entity_number, new_span.begin

                for token in self.tokens:
                    if token[u'gr'] not in u'CR,-SENT' and token[u'gr'][0] != u'S':
                        if token[u'begin'] >= new_span.begin:
                            if token[u'end'] <= new_span.end:
                                new_span.tokens.append(token[u'text'])
                                # print token[u'text']
                            else:
                                break

                yield new_span

    def get_relations(self):
        for r in self.relations_generator(self.ann_gold):
            self.relations_gold.append(r)

        for r in self.relations_generator(self.ann_tested):
            self.relations_tested.append(r)

    def relations_generator(self, annotation):
        for line in annotation:
            line = line.split(u'\t')
            if line[0][0] == u'R':
                arguments = line[1].split(u' ')
                arg1 = int(arguments[1].split(u':')[1][1::])
                arg2 = int(arguments[2].split(u':')[1][1::])
                yield (arg1, arg2)


class Text:
    def __init__(self, result, path=None):
        self.result = result
        self.path = path
        self.sentences = []
        self.sentence = False
        self.analysis = None

    def treetagger_analyzer(self):
        # self.result = self.result.replace(u' ', u' ')
        self.result = re.sub(u'["«»‘’]', u'\'', self.result, flags=re.U)
        self.result = re.sub(u'(^|\. )\'(.+?)\'(, ?)([—-])', u'\\1"\\2"\\3~', self.result, flags=re.U)
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

    def write_stupid_clause_ann(self):
        i = 0
        write_name = self.path.replace(u'json', u'ann')
        w = codecs.open(write_name, u'w', u'utf-8')

        for sentence in self.sentences:
            for span in sentence.spans:
                i += 1
                line = u'T' + str(i) + u'\t' + u'Span ' + str(span.begin) + u' ' + str(span.end) + u'\t' + u'\n'
                w.write(line)

        w.close()

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
            # for r in sentence.verb_relations:
            #     # print sentence.spans[r[1]].entity_number
            #     j += 1
            #     line = u'R' + str(j) + u'\t' + u'Coordination Arg1:T' + str(sentence.spans[r[0]].entity_number) +\
            #            u' Arg2:T' + str(sentence.spans[r[1]].entity_number) + u'\t' + u'\n'
            #     w.write(line)

        w.close()

    def get_json(self, result):
        result[u'entities'] = list()
        result[u'relations'] = list()

        i = 0
        j = 0

        for sentence in self.sentences:
            for span in sentence.spans:
                if span.embedded or span.inserted or span.base:
                    i += 1
                    entity = list()
                    entity.append(u'T' + str(i))
                    entity.append(u'Span')
                    entity.append([[span.begin, span.end]])

                    result[u'entities'].append(entity)

                span.entity_number = i
            for r in sentence.relations:
                j += 1
                relation = list()
                relation.append(u'R' + str(j))
                relation.append(u'Split')
                arg1 = u'T' + str(sentence.spans[r[0]].entity_number)
                arg2 = u'T' + str(sentence.spans[r[1]].entity_number)
                relation.append([[u'LeftSpan', arg1], [u'RightSpan', arg2]])

                result[u'relations'].append(relation)


    def write_dummy_ann(self):
        write_name = self.path.replace(u'txt', u'ann')
        w = codecs.open(write_name, u'w', u'utf-8')
        w.close()

    def write_pos_ann(self):
        name = self.path[:-3:] + u'json'
        w = codecs.open(name, u'w', u'utf-8')
        json.dump(self.analysis, w, ensure_ascii=False, indent=2)
        w.close()

    def copy_into_brat(self, path, dummy=False):
        if dummy:
            text = self.path
            ann = self.path.replace(u'txt', u'ann')
        else:
            text = self.path.replace(u'json', u'txt')
            ann = self.path.replace(u'json', u'ann')
        shutil.copy(text, path + text.split(u'/')[-1])
        shutil.copy(ann, path + ann.split(u'/')[-1])

    def normalize(self, mode=None):
        self.result = self.result.replace(u' ', u' ')
        self.result = self.result.replace(u'\r\n', u' ')
        self.result = self.result.replace(u'\n', u' ')
        self.result = self.result.replace(u'…', u'...')
        self.result = re.sub(u'( |^)[A-Za-z]+?\.[A-Za-z].*?( |$)', u'\\1"Английское название"\\2', self.result,
                             flags=re.U)
        self.result = re.sub(u' +', u' ', self.result, flags=re.U)
        self.result = re.sub(u' $', u'', self.result, flags=re.U)
        if mode:
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

    def split(self):
        self.find_complimentizers()
        self.find_names()
        self.eliminate_pair_comma()
        self.span_splitter()
        self.get_shared_tokens()
        self.split_double_complimentizers()

        for span in self.spans:
            span.type()

        # пробуем удалить пустые спаны
        non_empty_spans = []
        for span in self.spans:
            if span.tokens:
                non_empty_spans.append(span)

        self.spans = non_empty_spans[::]

        self.split_embedded()
        self.restore_embedded()
        self.split_base()
        self.restore_base()

        for span in self.spans:
            span.get_boundaries()

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

            if self.spans[-1].tokens[0].lex == u'~':
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

    def stupid_span_splitter(self):
        for token in self.tokens:
            add = False
            off = False
            while not add:
                if token.content != u'\"':
                    self.span_on()
                    self.add_token(token)
                    if not token.stupid_end_of_span():
                        add = True
                    if token.stupid_end_of_span() and off:
                        add = True
                        continue
                else:
                    if not self.quotes:
                        self.quotes = True
                    else:
                        self.quotes = False
                    add = True
                if token.stupid_end_of_span():
                    # print token.content
                    self.span_off()
                    off = True
                    if token.pos == u'COMMA':
                        add = True
                # elif token.content != u'\"':
                #     self.span_on()
        self.span_off()

    def eliminate_pair_comma(self):
        predicate = False
        begin = {u'—': False, u'|': False, u'"': False}
        end = False
        left = None
        for i, token in enumerate(self.tokens):
            # print token.content
            if token.pos == u'pairCOMMA' and not begin[token.lex]:
                # print token.content, 777
                left = i
                begin[token.lex] = True
                end = False
            elif token.pos[0] == u'V' and sum(begin.values()) > 0:
                # print token.content
                predicate = True
            elif token.pos == u'pairCOMMA' and begin[token.lex]:
                right = i
                begin[token.lex] = False
                if predicate:
                    self.tokens[left].pos = self.tokens[right].pos = u'COMMA'
                predicate = False
                end = True
        if not end and left:
            # print 1
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
                        new_span = copy.deepcopy(span)
                        new_span.tokens = span.tokens[:1:]
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

                            # связь COORDINATION!!!
                            if span.predicate_coordination(following_span):
                                # print following_span.tokens[0].content
                                # print last_connected, j
                                following_span.embedded = True
                                span.before_dash += following_span.before_dash
                                following_span.embedded_type = span.embedded_type
                                following_span.quasi_embedded = True
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

                            # связь COORDINATION!!!
                            if span.predicate_coordination(following_span):
                                # print following_span.tokens[0].content
                                # print last_connected, j
                                span.before_dash += following_span.before_dash
                                following_span.embedded_type = span.embedded_type
                                following_span.quasi_embedded = True
                                self.verb_relations.append((last_connected_verb, j))
                                last_connected_verb = j

                        if following_span.semicolon:
                            break

    def complete_base(self, span, i):
        for j, following_span in enumerate(self.spans[i+1::], start=i+1):
            if following_span.quasi_embedded:
                if span.accept_base(following_span):
                    span.shared_tokens += following_span.tokens
                    span.before_dash += following_span.before_dash
                    following_span.embedded = False
                    following_span.base = True
                    following_span.in_base = True
                    self.relations.append((i, j))
                    to_remove = []
                    for k, relation in enumerate(self.verb_relations):
                        if j in relation:
                            to_remove.append(k)
                    for position in to_remove:
                        self.verb_relations.pop(position)
                    break

    def restore_base(self):
        for i, span in reversed(list(enumerate(self.spans))):
            if span.basic:
                # print span.tokens[1].content, span.finite()
                if not span.finite() and not span.before_dash:
                    # print span.tokens[0].content
                    continue
                else:
                    # print span.tokens[0].content
                    self.join_base(span, i)

        for i, span in enumerate(self.spans):
            if span.basic and not span.base and not span.in_base:
                # print span.tokens[0].content
                self.join_base(span, i, False)

        for i, span in enumerate(self.spans):
            if span.base and not span.finite():
                # print span.tokens[0].content, span.ellipsis
                self.complete_base(span, i)

    def join_base(self, span, i, backward=True):
        switch = False
        span.base = True
        span.in_base = True
        last_added = i
        last_connected = i
        for j, following_span in enumerate(self.spans[i+1::], start=i+1):
            if following_span.basic:
                if span.finite() and following_span.finite():
                    # print span.tokens[0].content, following_span.tokens[0].content
                    break
            if not backward:
                # print span.tokens[0].content
                # print following_span.basic, following_span.in_base, following_span.base, backward
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
                                span.after_dash = True
                                if span.tokens[0].lex not in myData.specificators:
                                    # print 1
                                    span.ellipsis = True
                            continue
            # print span.tokens[0].content, following_span.tokens[0].content, 111, following_span.base, following_span.in_base, backward
            if following_span.basic and following_span.in_base is not backward and following_span.base is not backward:
                # print span.tokens[0].content, following_span.tokens[0].content, 555, j

                switch = following_span.base

                # если это НЕ примыкающий спан!!!
                if j != last_added + 1:
                    # print span.tokens[0].content, following_span.tokens[0].content, 555, j

                    # если это спан СО СВЯЗЬЮ!!!
                    if j != last_connected + 1:
                        if span.accept_base(following_span):
                            # print 1
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
                    if span.after_dash:
                        if span.accept_base(following_span) and span.coordinate(following_span):
                            # print span.tokens[0].content, following_span.tokens[0].content, 777, j
                            # print following_span.tokens[0].content, backward
                            span.ellipsis = False
                            span.base = False
                            span.in_base = False
                            span.tokens += following_span.tokens
                            span.shared_tokens += following_span.tokens
                            span.before_dash += following_span.before_dash
                            following_span.in_base = True
                            following_span.base = False
                            last_added = j
                    else:
                        # print span.tokens[0].content, following_span.tokens[0].content,\
                        #     span.accept_base(following_span), span.coordinate(following_span)
                        # print span.tokens[0].content
                        """
                        Было и работало неверно:
                        print span.before_dash, span.finite(), following_span.finite()
                        if (span.before_dash and not span.finite() and not following_span.finite()) or\
                                (not span.before_dash and (span.finite() or following_span.finite())):
                        """
                        # print span.before_dash, span.finite(), following_span.finite()
                        if (span.before_dash and not span.finite() and not following_span.finite()) or\
                                (not (span.finite() and following_span.finite())):
                            # print 1
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
                                    span.after_dash = True
                                    if span.tokens[0].lex not in myData.specificators:
                                        # print 1
                                        span.ellipsis = True

            # if following_span.base:
            #     break

            if span.finite() and switch:
                # print span.tokens[0].content, 888
                break

    def split_embedded(self):
        find = False
        for span in self.spans:
            # print span.basic, span.tokens[0].content
            self.new_spans.append(span)
            if span.embedded:
                # print span.embedded_type
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
                find_participle = False
                if span.embedded_type == u'participle':
                    # print span.participle_number()
                    if span.participle_number() > 1:
                        # print 1
                        for i, token in reversed(list(enumerate(span.tokens))):
                            if len(token.pos) > 2:
                                if token.pos[0] == u'V':
                                    if token.pos[2] == u'p':
                                        find_participle = True
                                        find += True
                            elif token.lex == u'и':
                                if find_participle:
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

            else:
                # print span.tokens[0].content
                find += self.find_coordination(span)

        if find:
            # print 1
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
            # print u'\n'.join([span.tokens[1].content for span in self.new_spans])
            self.spans = copy.deepcopy(self.new_spans)

    def split_spans(self, span, i, embedded_type=None):
        # print following_token.content
        new_span = copy.deepcopy(span)
        new_span.tokens = span.tokens[i::]
        new_span.shared_tokens = span.shared_tokens[i::]
        if embedded_type:
            new_span.embedded = True
            new_span.embedded_type = embedded_type
        span.tokens = span.tokens[:i:]
        span.shared_tokens = span.shared_tokens[:i:]
        self.new_spans.append(new_span)
        return True

    def find_coordination(self, span):
        # and_number = len([True for token in span.tokens if token.lex == u'и'])
        predicate_number = len([True for token in span.tokens if token.predicate()])
        infinitive_number = len([True for token in span.tokens if token.infinitive()])
        predicate_after_and = len([True for i, token in enumerate(span.tokens[:-1:]) if token.lex == u'и' and
                                   (span.tokens[i+1].predicate() or span.tokens[i+1].infinitive() or
                                    span.tokens[i+1].gerund_participle())])

        # Это для ФИНИТНЫХ ПРЕДИКАТОВ
        # print span.tokens[0].content, predicate_number, predicate_after_and
        if predicate_number > 1 or predicate_after_and:
            # # print 1
            # if and_number == 1 or predicate_after_and:
            #     # print 1
            #     for i, token in reversed(list(enumerate(span.tokens))):
            #         if token.lex == u'и':
            #             if i > 0:
            #                 for j, following_token in enumerate(span.tokens[i+1::], start=i+1):
            #                     # print following_token.content
            #                     if following_token.lex == u'который':
            #                         continue
            #                     if following_token.predicate():
            #                         return self.split_spans(span, i)
            #
            #                     # здесь написал continue т.к. есть случаи "это лишь опасения и он не придет"
            #                     elif following_token.pos[0] != u'R':
            #                         continue
            #                         # return False
            # elif and_number > 1:
            for i, token in reversed(list(enumerate(span.tokens))):
                if token.lex == u'и':
                    if i > 0 and i < len(span.tokens) - 1:
                        # print len(span.tokens) - 1
                        # print i
                        # print span.tokens[0].content, span.tokens[-1].content
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
                                    return self.split_spans(span, i)

                                # elif following_token.pos[0] != u'R':
                                #     return False

        # Это для ИНФИНИТИВОВ
        # print span.tokens[0].content, predicate_number
        if infinitive_number > 1 or (predicate_after_and and not span.finite() and infinitive_number < 2):
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
                                if following_token.infinitive():
                                    return self.split_spans(span, i)

                                # elif following_token.pos[0] != u'R':
                                #     return False

        # Это для ПРИЧАСТИЙ
        """
        Я себя хочу убить за такое рукожопие, но пока так
        """
        # print span.tokens[0].content, predicate_number, predicate_after_and
        if predicate_after_and:
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
                                if following_token.gerund_participle():
                                    return self.split_spans(span, i, embedded_type=u'participle')

                                # elif following_token.pos[0] != u'R':
                                #     return False

        return False

    def find_complimentizers(self):
        for i, token in enumerate(self.tokens):
            if token.content.lower() in myData.complex_complimentizers:
                # print token.content
                for item in myData.complex_complimentizers[token.content.lower()]:
                    end = i + item[1]
                    if len(self.tokens) > end + 1:
                        # print len(self.tokens), end + 1
                        new = [token]
                        j = i
                        while len(new) != item[1]:
                            j += 1
                            # try:
                            if u'COMMA' not in self.tokens[j].pos:
                                new.append(self.tokens[j])
                            # except:
                            # print u' '.join([token.content for token in self.tokens])
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
        self.quasi_embedded = False
        self.in_embedded = False
        self.embedded_type = None
        self.base = False
        self.in_base = False
        self.basic = False
        self.inserted = False
        self.indicative = False
        self.gerund = 0
        self.participle = 0
        self.relative = 0
        self.inside_quotes = False
        self.semicolon = False
        self.before_dash = False
        self.after_dash = False
        self.before_colon = False
        self.complement_type = None
        self.null_copula = False
        self.ellipsis = False
        self.entity_number = None
        # self.finite = False

    def incomplete(self):
        if self.embedded_type == u'complement' or self.embedded_type == u'relative':
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
                for token in reversed(self.shared_tokens):
                    if re.match(u'(N...n.)|(P....n.)|(M...[n-])', token.pos):
                        return False
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
        # for token in self.tokens:
        #     print token.content
        # print following_span.tokens
        if following_span.tokens[0].lex in myData.specificators:
            # print following_span.tokens[0].lex
            return True
        if self.before_dash or self.before_colon:
            return True
        for token in reversed(self.shared_tokens):
            # print token.content, 9000
            if following_span.tokens[0].lex == u'как':
                return True
            if token.predicate() or token.infinitive():
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
            if token_right.predicate() or token_right.infinitive():
                return False
            else:
                if token.pos[0] in u'ANP' and token_right.pos[0] in u'ANP':
                    # print token.content, token_right.content
                    # print token.case(), token_right.case()
                    if token.case() == token_right.case():
                        return True
                elif token.pos[0] == u'R' and token_right.pos[0] == u'R':
                    return True
                elif token.pos[0] == u'M' and token_right.pos[0] == u'M':
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
            elif self.tokens[0].lex == u'согласно':
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
                if self.tokens[0].content == u'несмотря на':
                    self.embedded_type = u'gerund'
                    return True
                # print self.tokens[0].content
                if self.tokens[0].lex in myData.complimentizers:
                    if self.tokens[0].lex in myData.conditional_complimentizers and len(self.tokens) > 1:
                        # print self.tokens[0].lex, self.tokens[1].lex
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

            if self.gerund > 0 and not self.finite():
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

        return False

    def accept_embedded(self, other):
        if self.inside_quotes is other.inside_quotes:
            if self.embedded_type == u'gerund' or self.embedded_type == u'participle':
                return not other.finite() and not other.nominative()
            elif self.embedded_type == u'relative' or self.embedded_type == u'complement':
                if self.incomplete():
                    return True
                # print self.finite(), other.finite(), 111, self.tokens[0].content, other.tokens[0].content
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

    def participle_number(self):
        for token in self.shared_tokens:
            if re.match(u'V.p.+', token.pos):
                # print token.content
                self.participle += 1
        return self.participle

    def finite(self):
        nominative = 0
        for i, token in enumerate(self.shared_tokens):
            # print u' '.join([token.content for token in self.shared_tokens])
            # print token.pos, token.content, 777, token.lex
            if token.predicate():
                return True
            elif token.infinitive() and self.shared_tokens[0].lex == u'и':
                return True
            # if re.match(u'(V.[imc].......)|(V.p....ps.)|(A.....s)', token.pos):
            #     # print u' '.join([token.content for token in self.shared_tokens])
            #     return True
            elif re.match(u'V.n.......', token.pos) and self.shared_tokens[0].lex in [u'чтобы', u'перед тем как']:
                # print self.shared_tokens[0].content
                return True
            # if token.lex in myData.predicates:
            #     # print self.shared_tokens[0].content
            #     return True
            if token.lex == u'—' or token.lex == u'-':
                # print 1
                # print u' '.join([token.content for token in self.shared_tokens]), token.content, token.lex
                if self.tokens[0].lex not in myData.specificators:
                    self.ellipsis = True
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
        if self.ellipsis:
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
            if self.pos[5] == u'n':
                return u'a'
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
        if re.match(u'(V.[cim].......)|(V.p....ps.)|(A.....s)', self.pos):
            # print self.pos, self.content
            return True
        if self.lex in myData.predicates:
            # print self.content
            return True
        return False

    def gerund_participle(self):
        if re.match(u'V.[gp].......', self.pos):
            # print self.pos, self.content
            return True

    def infinitive(self):
        if re.match(u'V.n.......', self.pos):
            return True
        return False

    def end_of_span(self):
        return self.pos == u'COMMA'

    def stupid_end_of_span(self):
        if self.pos == u'COMMA':
            return True
        elif self.pos == u'C':
            return True
        return False

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
