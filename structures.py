# -*- coding:utf-8 -*-

import os
import re
import copy
import json
import codecs
import shutil
import treetaggerwrapper
# from pymystem3 import Mystem

__author__ = u'Gree-gorey'

t = treetaggerwrapper.TreeTagger(TAGLANG=u'ru')
# m = Mystem(grammar_info=True, disambiguation=True, entire_input=True)

prepositions = json.load(codecs.open(u'./data/prepositions.json', u'r', u'utf-8'))
complimentizers = json.load(codecs.open(u'./data/complimentizers.json', u'r', u'utf-8'))
inserted = json.load(codecs.open(u'./data/inserted.json', u'r', u'utf-8'))
predicates = json.load(codecs.open(u'./data/predicates.json', u'r', u'utf-8'))
inserted_evidence = json.load(codecs.open(u'./data/inserted_evidence.json', u'r', u'utf-8'))
complex_complimentizers = json.load(codecs.open(u'./data/complex_complimentizers.json', u'r', u'utf-8'))


class Corpus:
    def __init__(self, path):
        self.path = path

    def texts(self, extension):
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if extension in filename:
                    open_name = self.path + filename
                    f = codecs.open(open_name, u'r', u'utf-8')
                    if extension == u'json':
                        result = json.load(f)
                    else:
                        result = f.read()
                    f.close()
                    yield Text(result, open_name)

# /home/gree-gorey/Corpus/
# /opt/brat-v1.3_Crunchy_Frog/data/right/


class Text:
    def __init__(self, result, path):
        self.result = result
        self.path = path
        self.sentences = []
        self.sentence = False
        self.analysis = None

    def mystem_analyzer(self):
        self.result = self.result.replace(u' ', u' ')
        self.analysis = m.analyze(self.result)
        position = 0
        if self.analysis[-1][u'text'] == u'\n':
            del self.analysis[-1]
        for token in self.analysis:
            token[u'begin'] = position
            position += len(token[u'text'])
            token[u'end'] = position

    def treetagger_analyzer(self):
        self.result = self.result.replace(u' ', u' ')
        self.analysis = t.tag_text(self.result, tagblanks=True)
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
            self.add_token(result) if i == len(self.result)-1 else self.add_token(result, self.result[i+1])
            if self.end_of_sentence():
                self.sentence_off()
        self.sentence_off()

    def end_of_sentence(self):
        if self.sentences[-1].tokens[-1].pos == u'PERIOD':  # if it is a period
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

    def add_punctuation(self, token, next_token):
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
            elif token[u'lex'] in u'"':
                self.sentences[-1].tokens[-1].pos = u'QUOTE'
            else:
                self.sentences[-1].tokens[-1].pos = u'UNKNOWN'
                self.sentences[-1].tokens[-1].lex = token[u'lex']
        elif token[u'gr'] == u'SENT':
            self.add_period(next_token)

    def add_period(self, next_token):
        self.sentences[-1].tokens[-1].pos = u'PERIOD'
        if self.sentences[-1].after_abbreviation:
            self.sentences[-1].tokens[-1].after_abbreviation = True
        if next_token is not None:
            if next_token[u'text'].istitle() or next_token[u'text'] == u'\"':
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

    def add_token(self, token, next_token=None):
        self.sentences[-1].tokens.append(Token())
        self.sentences[-1].tokens[-1].begin = token[u'begin']
        self.sentences[-1].tokens[-1].end = token[u'end']
        self.sentences[-1].tokens[-1].content = token[u'text']
        if token[u'gr'][0].isalpha() and token[u'gr'] != u'SENT':
            self.add_word(token, next_token)
        else:
            self.add_punctuation(token, next_token)
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
        self.result = self.result.replace(u'\r\n', u' ')
        self.result = self.result.replace(u'\n', u' ')
        self.result = self.result.replace(u'…', u'...')
        self.result = re.sub(u'( |^)[A-Za-z]+?\.[A-Za-z].*?( |$)', u'\\1"Английское название"\\2', self.result,
                             flags=re.U)
        self.result = re.sub(u' +', u' ', self.result, flags=re.U)
        self.result = re.sub(u' $', u'', self.result, flags=re.U)
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
            self.span = False
            if self.spans[-1].tokens[-1].content in u';()':
                self.spans[-1].semicolon = True
            elif self.spans[-1].tokens[-1].content == u'—':
                self.spans[-1].before_dash = True
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
                self.span_off()
            # elif token.content != u'\"':
            #     self.span_on()
        self.span_off()

    def eliminate_pair_comma(self):
        predicate = False
        begin = {u'—': False, u'|': False}
        end = False
        left = right = None
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
                    new_span = Span()
                    new_span.tokens += span.tokens[:1:]
                    span.tokens.pop(0)
                    new.append(new_span)
            new.append(span)
        self.spans = copy.deepcopy(new)

    def restore_embedded(self):
        for i, span in reversed(list(enumerate(self.spans))):
            if span.embedded:
                if not span.semicolon:
                    last_added = i
                    last_connected = i
                    last_connected_verb = i
                    for j, following_span in enumerate(self.spans[i+1::], start=i+1):
                        # print u' '.join([token.content for token in span.tokens])
                        if not following_span.embedded and not following_span.in_embedded and not following_span.inserted:

                            if span.predicate_coordination(following_span):
                                # print following_span.tokens[0].content
                                # print last_connected, j
                                following_span.embedded = True
                                following_span.embedded_type = span.embedded_type
                                self.verb_relations.append((last_connected_verb, j))
                                last_connected_verb = j

                            else:

                                # если это НЕ непосредственно следующий за последним поглощённым спаном
                                if j != last_added + 1:

                                    # если это НЕ непосредственно следующий за последним присоединённым спаном
                                    if j != last_connected + 1:
                                        if span.accept_embedded(following_span):
                                            span.shared_tokens += following_span.tokens
                                            following_span.embedded = True
                                            following_span.embedded_type = span.embedded_type
                                            self.relations.append((last_connected, j))
                                            last_connected = j
                                            # span.semicolon = following_span.semicolon
                                        else:
                                            break

                                    else:
                                        # print span.tokens[0], 888
                                        # проверка на сочинение!
                                        if span.accept_embedded(following_span):
                                            self.spans[last_connected].tokens += following_span.tokens
                                            following_span.in_embedded = True
                                            last_added = j
                                            # span.semicolon = following_span.semicolon
                                        else:
                                            break

                                else:
                                    # print following_span.tokens[0].content, 777
                                    # проверка на сочинение!
                                    # print span.accept_embedded(following_span), span.coordinate(following_span)
                                    if span.accept_embedded(following_span) and span.coordinate(following_span):
                                        span.tokens += following_span.tokens
                                        span.shared_tokens += following_span.tokens
                                        following_span.in_embedded = True
                                        last_added = j
                                        # span.semicolon = following_span.semicolon
                                    else:
                                        break

                        if following_span.semicolon:
                            break

    def restore_base(self):
        for i, span in reversed(list(enumerate(self.spans))):
            if not span.embedded and not span.in_embedded and not span.in_base and not span.inserted:
                span.basic = True
                if not span.finite():
                    continue
                else:
                    span.base = True
                    span.in_base = True
                    last_added = i
                    last_connected = i
                    for j, following_span in enumerate(self.spans[i+1::], start=i+1):
                        if following_span.basic and not following_span.in_base and not following_span.base:
                            if j != last_added + 1:

                                # если это НЕ непосредственно следующий за последним присоединённым спаном
                                if j != last_connected + 1:
                                    span.shared_tokens += following_span.tokens
                                    following_span.in_base = True
                                    self.relations.append((last_connected, j))
                                    last_connected = j

                                else:
                                    self.spans[last_connected].tokens += following_span.tokens
                                    following_span.in_base = True

                            else:
                                span.tokens += following_span.tokens
                                span.shared_tokens += following_span.tokens
                                following_span.in_base = True
                                last_added = j

                        elif following_span.base:
                            break

    def split_embedded(self):
        new_spans = []
        for span in self.spans:
            new_spans.append(span)
            find_coordination = False
            if span.embedded:
                if span.embedded_type == u'gerund' or span.embedded_type == u'relative':
                    if span.gerund > 1 or span.relative > 0:
                        for i, token in reversed(list(enumerate(span.tokens))):
                            if len(token.pos) > 2:
                                if token.pos[0] == u'V':
                                    if token.pos[2] == u'g':
                                        find_coordination = True
                                elif token.lex == u'который':
                                    find_coordination = True
                            elif token.lex == u'и':
                                if find_coordination:
                                    if i > 0:
                                        new_span = Span()
                                        new_span.embedded = True
                                        new_span.embedded_type = span.embedded_type
                                        for following_token in span.tokens[i::]:
                                            new_span.tokens.append(following_token)
                                        new_spans[-1].tokens = span.tokens[:i:]
                                        new_spans.append(new_span)
                                        break
        self.spans = copy.deepcopy(new_spans)

    def find_complimentizers(self):
        for i, token in enumerate(self.tokens):
            if token.content.lower() in complex_complimentizers:
                # print token.lex
                end = i + complex_complimentizers[token.lex][1]
                if len(self.tokens) >= end + 1:
                    new = [token]
                    j = i
                    while len(new) != complex_complimentizers[token.content.lower()][1]:
                        j += 1
                        if u'COMMA' not in self.tokens[j].pos:
                            new.append(self.tokens[j])
                    new_complimentizer = u' '.join([next_token.content.lower() for next_token in new])
                    # print new_complimentizer_lex, 2
                    if new_complimentizer == complex_complimentizers[token.lex][0]:
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
        # self.finite = False

    def predicate_coordination(self, following_span):
        for token in self.shared_tokens:
            if token.predicate():
                for other_token in following_span.tokens:
                    if token.pos[0] == u'V' and other_token.pos[0] == u'V':
                        # print token.content
                        if token.coordinate(other_token):
                            # print token.content
                            return True

    def coordinate(self, following_span):
        if self.before_dash:
            return True
        for token in reversed(self.shared_tokens):
            if token.predicate():
                return False
            else:
                if following_span.find_right(token):
                    return True
                if token.lex == u'такой' and following_span.tokens[0].lex == u'как':
                    return True

    def find_right(self, token_left):
        # print u'******************'
        for token in self.shared_tokens:
            # print token.content, token_left.content
            if token.predicate():
                return False
            else:
                if len(token.pos) > 4 and len(token_left.pos) > 4:
                    if token.pos[0] == u'N' and token_left.pos[0] == u'N':
                        if token.pos[4] == token_left.pos[4]:
                            # print token.content, token_left.content
                            return True
                    elif token.pos[0] == u'A' and token_left.pos[0] == u'A':
                        if token.pos[5] == token_left.pos[5]:
                            return True


    def type(self):
        if self.is_inserted():
            self.inserted = True
        if self.is_embedded():
            self.embedded = True

    def is_inserted(self):
        if len(self.tokens) < 10:
            if self.tokens[0].lex == u'по':
                if len(self.tokens) > 2:
                    if self.tokens[1].content in inserted_evidence or self.tokens[2].content in inserted_evidence:
                        return True
            if self.tokens[0].content.lower() in inserted:
                # print self.tokens[0].content.lower()
                content = u''
                for token in self.tokens:
                    content += token.content.lower()
                    content += u' '
                for var in inserted[self.tokens[0].content.lower()]:
                    if var == content[:-1:]:
                        return True

    def is_embedded(self):
        if not self.inserted:
            if self.tokens[0].pos[0] in u'CP':
                # print self.tokens[0].content
                if self.tokens[0].lex in complimentizers:
                    if self.tokens[0].lex == u'как':
                        if self.finite():
                            return True
                    else:
                        self.embedded_type = u'complement'
                        return True
            elif re.match(u'V.p.......', self.tokens[0].pos):
                if not self.finite():
                    self.embedded_type = u'participle'
                    return True
            elif self.tokens[0].pos in u'QR' and len(self.tokens) > 1:
                if re.match(u'V.p.......', self.tokens[1].pos):
                    if not self.finite():
                        self.embedded_type = u'participle'
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
            if self.gerund > 0 and not self.indicative:
                self.embedded_type = u'gerund'
                return True
            elif self.relative > 0:
                self.embedded_type = u'relative'
                return True

    def accept_embedded(self, other):
        # if self.inside_quotes is other.inside_quotes:
        if self.embedded_type == u'gerund' or self.embedded_type == u'participle':
            return not other.finite() and not other.nominative()
        elif self.embedded_type == u'relative' or self.embedded_type == u'complement':
            # print self.finite(), other.finite(), 111, other.tokens[0].content
            if not(self.finite() and other.finite()):
                return not other.begin_with_and()
            else:
                return False
        # else:
        #     return False

    def begin_with_and(self):
        return self.tokens[0].lex == u'и'

    def nominative(self):
        for token in self.shared_tokens:
            if re.match(u'(N...n.)|(P....n.)', token.pos):
                return True
        return False

    def finite(self):
        for token in self.shared_tokens:
            if re.match(u'(V.[imc].......)|(V.p....ps.)|(A.....s)', token.pos):
                return True
            if token.lex in predicates:
                return True
        return False

    def accept_base(self):
        for token in self.tokens:
            if u'V' in token.pos:
                return True

    def get_boundaries(self):
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

    def coordinate(self, other):
        pos = zip(self.pos, other.pos)[1:3:] + zip(self.pos, other.pos)[4:7:]
        # print pos
        for item in pos:
            if u'-' in item:
                pass
            else:
                if item[0] != item[1]:
                    return False
        return True

    def predicate(self):
        if re.match(u'(V.*)|(A.....s)', self.pos):
            return True
        if self.lex in predicates:
            return True
        return False

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


def write_brat_ann(path):  # text, path):
    name = path[:-3:] + u'ann'
    w = codecs.open(name, u'w', u'utf-8')
    # i = 1
    # for sent in text.sentences:
    #     for pp in sent.pp:
    #         w.write(u'T' + str(i) + u'\tSpan ' + str(sent.tokens[pp[0]].begin) + u' ' + str(sent.tokens[pp[1]].end) +
    #                 u'\n')
    #         i += 1
    #     for np in sent.np:
    #         w.write(u'T' + str(i) + u'\tSpan ' + str(sent.tokens[np[0]].begin) + u' ' + str(sent.tokens[np[1]].end) +
    #                 u'\n')
    #         i += 1
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

