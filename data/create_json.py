# -*- coding:utf-8 -*-

import codecs
import json


def create(type_of):
    var = [u'predicates',
           u'inserted',
           u'complimentizers',
           u'prepositions']
    result = None
    with codecs.open(var[type_of] + u'.csv', u'r', u'utf-8') as f:
        if type_of == 1:
            result = {}
            for line in f:
                line = line.rstrip()
                words = line.split(u' ')
                if words[0] in result:
                    result[words[0]].append(line)
                else:
                    result[words[0]] = [line]
        elif type_of == 2 or type_of == 0:
            result = []
            for line in f:
                line = line.rstrip()
                result.append(line)
        elif type_of == 3:
            result = {}
            for line in f:
                line = line.rstrip()
                result[line[0]] = line[1].split(u',')
    return var[type_of] + u'.json', result

name, res = create(0)

w = codecs.open(name, u'w', u'utf-8')
json.dump(res, w, ensure_ascii=False, indent=2)
w.close()
