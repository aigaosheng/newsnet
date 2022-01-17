#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 11:06:19 2017

@author: gao
"""
from scrapy.selector import Selector
from nodeClassify import NodeClassify
import settings
from htmlAnalytic import htmlAnalytic
import argparse, sys
from nodeParser import NodeParser

print('a')
parser = argparse.ArgumentParser()
parser.add_argument('--infile', action='store', nargs='+', help='html document corpus')
parser.add_argument('--ofile', action='store', nargs=1, help='output file to save clear data')

args = parser.parse_args(sys.argv[1:])
html_parser =  NodeParser()
for fname in args.infile:
        print(fname.startswith('http'))
        if fname.startswith('http'):
            htmlcontent = htmlAnalytic.craw_url(fname)
            s = html_parser.parser(htmlcontent)
            text = html_parser.format_text()
            print(text)