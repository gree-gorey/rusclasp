# -*- coding:utf-8 -*-

from rusclasp import rusclasp
import time

__author__ = 'gree-gorey'

t1 = time.time()

s = rusclasp.Splitter()

sentence = u'Вы можете, введя свое предложение, проверить работу программы.'

result = s.split(sentence)

t2 = time.time()

print result[u'text']

print t2 - t1
