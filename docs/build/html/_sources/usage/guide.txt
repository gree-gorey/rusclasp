========================
Руководство пользователя
========================

Установка из PyPI
-----------------

Для установки используйте pip:

.. code-block:: python

   $ pip install rusclasp
   
Dependencies
~~~~~~~~~~~~

Для работы rusclasp необходим `TreeTagger <http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/>`__ (вместе с `Russian parameter file <http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/russian-par-linux-3.2-utf8.bin.gz>`__) а также
`treetaggerwrapper <https://packages.debian.org/sid/libicu-dev>`__, treetaggerwrapper может быть установлен следующей командой:

.. code:: python

    $ pip install treetaggerwrapper


Разбиение предикаций
--------------------

Разбиение на предикации представляет собой разбиение текста на отрезки, содержащие один финитный предикат (возможно, нулевой) и его зависимые. При этом предикации, разорванные вложением, восстанавливаются.

Разбиение происходит следующим образом:

.. code-block:: python

   import rusclasp

   s = rusclasp.Splitter()

   sentence = u'Вы можете, введя свое предложение, проверить работу программы.'

   result = s.split(sentence)

У метода :code:`split` есть необязательный аргумент :code:`mode`, значение которого по умолчанию :code:`mode='json'`. В таком режиме он возвращает в переменную :code:`result` словарь со следующей схемой:

.. code-block:: python

   { 'text': "Текст, который вы разбиваете.",
     'entities': [
                    ['T1', 'Span', [[0, 2]]],
                    ['T2', 'Span', [[4, 8]]],
                    ['T3', 'Span', [[10, 15]]]
                 ],
     'relations': [
                     ['R1', 'Split', [['LeftSpan', 'T1'], ['RightSpan', 'T3']]]
                  ]
    }

