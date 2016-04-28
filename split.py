# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = u'gree-gorey'


def main():
    t1 = time.time()

    new_corpus = Corpus(u'/home/gree-gorey/CorpusTemp/')
    # new_corpus = Corpus(u'/home/gree-gorey/tested/')
    # new_corpus = Corpus(u'/home/gree-gorey/tested_tested/')

    for text in new_corpus.texts(u'json'):
        text.sentence_splitter()
        # print len(text.sentences)
        for sentence in text.sentences:
            # print sentence.tokens[0].content

            # for token in sentence.tokens:
            #     print token.pos, token.content, token.lex
            # print u'***************'

            # sentence.find_pp()

            # sentence.find_coordination()

            sentence.find_complimentizers()

            sentence.find_names()

            sentence.eliminate_pair_comma()

            # for token in sentence.tokens:
            #     print token.pos, token.content
            # print u'***************'
            # print

            sentence.span_splitter()

            sentence.get_shared_tokens()  # loop through all the spans 1

            sentence.split_double_complimentizers()  # loop through all the spans 2

            for span in sentence.spans:  # loop through all the spans 3

                # decide whether span is inserted or embedded or neither
                span.type()
                # print span.tokens[0].content, span.embedded_type

            # split embedded span if it contains > 1 predicate
            sentence.split_embedded()

            # for span in sentence.spans:
            #     print span.shared_tokens[0].content, span.tokens[0].content

            # walk through spans and join whenever possible
            sentence.restore_embedded()

            sentence.split_base()

            # for span in sentence.spans:
            #     print span.shared_tokens[0].content, span.tokens[0].content, span.finite()

            sentence.restore_base()

            # for span in sentence.spans:
            #     print span.shared_tokens[0].content, span.tokens[0].content, span.finite()

            for span in sentence.spans:
                span.get_boundaries()
                # print span.quasi_embedded, span.tokens[0].content

        text.write_clause_ann()

        text.copy_into_brat(u'/opt/brat-v1.3_Crunchy_Frog/data/right/')

    t2 = time.time()

    print t2 - t1


if __name__ == '__main__':
    main()
