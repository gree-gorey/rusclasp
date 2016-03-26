# -*- coding:utf-8 -*-

import time
from structures import PairCorpora

__author__ = u'gree-gorey'


def main():
    t1 = time.time()

    new_pair_corpora = PairCorpora(u'/opt/brat-v1.3_Crunchy_Frog/data/gold/', u'/home/gree-gorey/tested/')
    # new_pair_corpora = PairCorpora(u'/opt/brat-v1.3_Crunchy_Frog/data/gold/', u'/home/gree-gorey/stupid/')

    for evaluated_text in new_pair_corpora.annotations():
        evaluated_text.get_spans()

        evaluated_text.get_relations()
        evaluated_text.restore_split()

        evaluated_text.count_match()

        # for span in evaluated_text.spans_gold:
        #     print u' '.join(span.tokens)
        # print u'**********'
        #
        # for span in evaluated_text.spans_tested:
        #     print u' '.join(span.tokens)
        # print u'**********'

        new_pair_corpora.texts.append(evaluated_text)

    new_pair_corpora.evaluate()

    print u'Precision: ', new_pair_corpora.precision
    print u'Recall: ', new_pair_corpora.recall
    print u'F-value: ', new_pair_corpora.f_value

    t2 = time.time()

    print t2 - t1

if __name__ == '__main__':
    main()