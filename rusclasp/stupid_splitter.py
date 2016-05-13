# -*- coding:utf-8 -*-

import time
from structures import Corpus

__author__ = u'gree-gorey'


def main():
    t1 = time.time()

    new_corpus = Corpus(u'/home/gree-gorey/stupid/')

    spans = 0

    for text in new_corpus.texts(u'json'):
        text.sentence_splitter()
        for sentence in text.sentences:

            sentence.stupid_span_splitter()

            spans += len(sentence.spans)

            for span in sentence.spans:
                span.get_boundaries()

        text.write_stupid_clause_ann()

        text.copy_into_brat(u'/opt/brat-v1.3_Crunchy_Frog/data/stupid/')

    print spans

    t2 = time.time()

    print t2 - t1


if __name__ == '__main__':
    main()
