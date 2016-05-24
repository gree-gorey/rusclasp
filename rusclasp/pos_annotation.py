# -*- coding:utf-8 -*-

import time
from splitter import Corpus

__author__ = u'gree-gorey'


def main():
    t1 = time.time()

    # new_corpus = Corpus(u'/home/gree-gorey/CorpusTemp/')
    new_corpus = Corpus(u'/home/gree-gorey/CorpusClean/')
    # new_corpus = Corpus(u'/home/gree-gorey/stupid/')
    # new_corpus = Corpus(u'/home/gree-gorey/tested_tested/')

    for text in new_corpus.texts(u'txt'):
        # text.mystem_analyzer()
        text.normalize(mode=u'write')
        text.treetagger_analyzer()
        text.write_pos_ann()

    t2 = time.time()

    print t2 - t1


if __name__ == '__main__':
    main()
