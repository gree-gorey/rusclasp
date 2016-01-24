# -*- coding:utf-8 -*-

import codecs
import json

prep = {}

with codecs.open(u'prepositions.csv', u'r', u'utf-8') as f:
    for line in f:
        line = line.rstrip().split(u'\t')
        prep[line[0]] = line[1].split(u',')

w = codecs.open(u'prepositions.json', u'w', u'utf-8')
json.dump(prep, w, ensure_ascii=False, indent=2)
w.close()
