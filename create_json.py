# -*- coding:utf-8 -*-

import codecs
import json

prep = {}
comp = []

with codecs.open(u'complimentizers.csv', u'r', u'utf-8') as f:
    for line in f:
        line = line.rstrip()
        comp.append(line)
        # prep[line[0]] = line[1].split(u',')

w = codecs.open(u'complimentizers.json', u'w', u'utf-8')
json.dump(comp, w, ensure_ascii=False, indent=2)
w.close()
