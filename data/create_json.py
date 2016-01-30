# -*- coding:utf-8 -*-

import codecs
import json

# prep = {}
# comp = []
ins = {}

with codecs.open(u'inserted.csv', u'r', u'utf-8') as f:
    for line in f:
        line = line.rstrip()
        words = line.split(u' ')
        if words[0] in ins:
            ins[words[0]].append(line)
        else:
            ins[words[0]] = [line]
        # comp.append(line)
        # prep[line[0]] = line[1].split(u',')

w = codecs.open(u'inserted.json', u'w', u'utf-8')
json.dump(ins, w, ensure_ascii=False, indent=2)
w.close()
