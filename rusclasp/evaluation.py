# -*- coding:utf-8 -*-

import time
from splitter import PairCorpora, Corpus

__author__ = u'gree-gorey'


def evaluate():

    # new_pair_corpora = PairCorpora(u'/home/gree-gorey/CorpusTemp/', u'/home/gree-gorey/CorpusTemp/')
    new_pair_corpora = PairCorpora(u'/opt/brat-v1.3_Crunchy_Frog/data/gold/', u'/home/gree-gorey/tested/')
    # new_pair_corpora = PairCorpora(u'/opt/brat-v1.3_Crunchy_Frog/data/gold/', u'/home/gree-gorey/stupid/')
    # new_pair_corpora = PairCorpora(u'/opt/brat-v1.3_Crunchy_Frog/data/gold_training/', u'/home/gree-gorey/tested_tested/')

    for evaluated_text in new_pair_corpora.annotations():

        # evaluated_text.get_boundaries()
        # evaluated_text.count_match_boundaries()

        # evaluated_text.get_spans()
        # evaluated_text.get_relations()
        # evaluated_text.restore_split()
        # evaluated_text.count_match()

        evaluated_text.get_boundaries()
        evaluated_text.count_match_window_diff()

        new_pair_corpora.texts.append(evaluated_text)

    # new_pair_corpora.evaluate()
    # new_pair_corpora.evaluate_boundaries()
    # new_pair_corpora.mean_span_size()
    new_pair_corpora.evaluate_window()

    print u'Precision: ', new_pair_corpora.precision
    print u'Recall: ', new_pair_corpora.recall
    print u'F-value: ', new_pair_corpora.f_value


def get_size():

    new_corpus = Corpus(u'/home/gree-gorey/CorpusClean/')

    print new_corpus.size()
    print new_corpus.count_sentences()


def main():
    t1 = time.time()

    # get_size()

    evaluate()

    t2 = time.time()

    print t2 - t1

if __name__ == '__main__':
    main()
