# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 12:17:19 2016

Description: parsing the dbGaP dieseases from the xml files. 

@author: Yingquan Li
"""

import os
from xml.dom import minidom
from xml.parsers.expat import ExpatError
import glob
import re

# Master data structure
master = []
name_list = glob.glob('*.xml')

#xmldoc = minidom.parse('items.xml')
#itemlist = xmldoc.getElementsByTagName('item')
#print(len(itemlist))
#print(itemlist[0].attributes['name'].value)
#for s in itemlist:
#    print(s.attributes['name'].value)

#xmldoc = minidom.parse('GapExchange_phs000001.v3.p1.xml')
#itemlist = xmldoc.getElementsByTagName('Disease')
#print(len(itemlist))
#print(itemlist[0].attributes['vocab_term'].value)
#for s in itemlist:
#    print(s.attributes['vocab_term'].value)

for name in name_list:  
    try: 
        xmldoc = minidom.parse(name)
        itemlist = xmldoc.getElementsByTagName('Disease')
        for s in itemlist:
            print(s.attributes['vocab_term'].value)
            master.append(s.attributes['vocab_term'].value)
    except ExpatError:
        pass

master = set(master)
master = list(master)

f = open('dbGaP_diesease.txt', 'w')
for item in master:
    f.write("%s\n" % item)
f.close()
