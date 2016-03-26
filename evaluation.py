# -*- coding:utf-8 -*-

import time
from structures import PairCorpora, Span

__author__ = u'gree-gorey'


def main():
    t1 = time.time()

    new_pair_corpora = PairCorpora(u'/opt/brat-v1.3_Crunchy_Frog/data/gold/', u'/home/gree-gorey/tested/')

    for evaluated_text in new_pair_corpora.annotations():
        evaluated_text.get_spans()
        evaluated_text.evaluate()

        # for span in evaluated_text.spans_gold:
        #     print u' '.join(span.tokens)
        # print u'**********'
        #
        # for span in evaluated_text.spans_tested:
        #     print u' '.join(span.tokens)
        # print u'**********'

        print u'Precision: ', evaluated_text.precision
        print u'Recall: ', evaluated_text.recall

    t2 = time.time()

    print t2 - t1

if __name__ == '__main__':
    main()
