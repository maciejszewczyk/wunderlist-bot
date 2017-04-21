#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

"""
Założenie 1 - wszystko może mieć liczbę:
"2 domestosy" mimo że zwykle wpisuje się na listę "domestos"
"2 kostki masła"
"2 jabłka"
"cytryny 5"
"banany 8"
"jogurty naturalne 5"


Założenie 2 - wszystko może być "x razy":
"2x domestos"
"2 x domestos"
"x2 domestos"
"x 2 domestos"
"domestos 2x"
"domestos 2 x"
"domestos x2"
"domestos x 2"


Zalożenie 3 - wszystko może mieć wagę:
"500 g krewetek"
"30 dkg sera"
"30dkg mozzarelli"
"500 g mascarpone"
"2kg mąki przennej"
"jabłek 2kg"
"pomidorów 3 kg"
"2kg marchewek"



Założenie 4 -
lower case and zamiana polskich diakrytycznych,
strip ze spacji z przodu i tylu ?

Założenie 5 -

"""
#


task_name1 = '30dkg sera żółtego'
task_name2 = 'chleb tostowy'
task_name3 = 'łosoś wędzony'
task_name4 = 'pasta do zębów'
task_name5 = 'papier toaletowy'
task_name6 = 'worki na śmieci'
task_name7 = '2kg mąki przennej tortowej'
task_name8 = 'pasta do butów'
task_name9 = 'papier do drukarki'
task_name10 = 'papier do pieczenia'
task_name11 = '2 kg jabłek'

extremal_name1 = "mleko kokosowe 2 puszki"
ex_name2 = '3 tabliczki czekolady białej'
ex_name3 = '2 opakowania ciastek'

tn = '  2x ajax  '

atuple = ('2x domestos',
          '2 x domestos',
          'x2 domestos',
          'x 2 domestos',
          'domestos 2x',
          'domestos 2 x',
          'domestos x2',
          'domestos x 2')

atuple1 = ('2x ajax',
          '2 x ajax',
          'x2 ajax',
          'x 2 ajax',
          'ajax 2x',
          'ajax 2 x',
          'ajax x2',
          'ajax x 2')

atuple = ('2x xenna',
          '2 x xenna',
          'x2 xenna',
          'x 2 xenna',
          'xenna 2x',
          'xenna 2 x',
          'xenna x2',
          'xenna x 2')

atuple = ('  500dkg jabłek  ',
          '  500 dkg jabłek  ',
          '  dkg500 jabłek  ',
          '  dkg 500 jabłek  ',
          '  jabłek 500dkg  ',
          '  jabłek 500 dkg  ',
          '  jabłek dkg500  ',
          '  jabłek dkg 500  ')

atuple = ('  500kg pomidorów  ',
          '  500 kg pomidorów  ',
          '  kg500 pomidorów  ',
          '  kg 500 pomidorów  ',
          '  pomidorów 500kg  ',
          '  pomidorów 500 kg  ',
          '  pomidorów kg500  ',
          '  pomidorów kg 500  ')

atuple = ('  500g krewetek  ',
          '  500 g krewetek  ',
          '  g500 krewetek  ',
          '  g 500 krewetek  ',
          '  krewetek 500g  ',
          '  krewetek 500 g  ',
          '  krewetek g500  ',
          '  krewetek g 500  ')

atuple = ('  500g grzybów  ',
          '  500 g grzybów  ',
          '  g500 grzybów  ',
          '  g 500 grzybów  ',
          '  grzybów 500g  ',
          '  grzybów 500 g  ',
          '  grzybów g500  ',
          '  grzybów g 500  ')


def normalize(tn):
    print "INPUT:%s" % (tn)

    #   0) stripowanie
    tn = tn.strip()
    print tn

    # 1) same liczby wylatują
    from string import digits
    tn = tn.translate(None, digits)
    print tn

    # 1a) znowu strip
    tn = tn.strip()
    print tn

    # 2) wylatują nadmiarowe spacje '  '

    tn = re.sub(' +',' ', tn)
    print tn

    # 3) usuwanie 'xspacja' i 'spacjax'
    tn = re.sub('^x ', '', tn)
    tn = re.sub(' x$', '', tn)
    print tn

    # 4) wylatuja dkg
    tn = tn.replace('dkg ', '').replace(' dkg', '')
    print tn

    # 5) wylatuja kg
    tn = tn.replace('kg ', '').replace(' kg', '')
    print tn

    # 6) wylatuja g (gramy)
    tn = re.sub('^g ', '', tn)
    tn = re.sub(' g$', '', tn)
    print tn

    # 7) usuwanie w,bez,na
    prepositions = ('bez', 'w', 'na')

    for prep in prepositions:
        tn = tn.replace(' ' + prep + ' ', '')


for element in atuple1:
    normalize(element)

#normalize(task_name11)