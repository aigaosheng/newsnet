# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 17:01:35 2017

@author: gao
"""

import json
import sys
import argparse
import codecs, re
import scrapy
from scrapy.selector import Selector
import settings
import urllib3
import certifi
from htmlAnalytic import htmlAnalytic
from keywordIndex import keywordManager
import pickle

from goose import Goose

parser = argparse.ArgumentParser()
parser.add_argument('--infile', action='store', nargs='+', help='html document corpus')

try:
    #load index
    keyword_index = keywordManager()
    keyword_index.build_vocab(settings.TEST_KEYWORD)
    keyword_index.build_index(settings.TEST_KEYWORD)
    keyword_index.save_index('index.json', readable = False)
    #    
    args = parser.parse_args(sys.argv[1:])
    html_parser = htmlAnalytic()
    samples = []
    for fname in args.infile:
        print(fname.startswith('http'))
        if fname.startswith('http'):
            htmlcontent = html_parser.craw_url(fname)
            #text_content = html_parser.content_parser(htmlcontent)
            print(htmlcontent)
            
            #url = 'https://www.w3schools.com/tags/tag_time.asp'
            g = Goose()
            #url=raw_input('url:')
            article = g.extract(raw_html=htmlcontent)
            print(article.title)
            print(article.cleaned_text)

            
        else:
            with open(fname, 'r') as fi:
                cc = 0
                for inst in fi:
                    page_data = json.loads(inst)
                    cc += 1
                    htmlcontent = page_data['get_body']
                    text_content = html_parser.content_parser(htmlcontent)
                    #s.extractor()
                    
                    g = Goose()
                    #url=raw_input('url:')
                    article = g.extract(raw_html=htmlcontent)
                    print(article.title)
                    print(article.cleaned_text)
                    
                    if cc>=1:
                        break
                    sys.stdout.write('\n\n****\n'+str(cc)+'\n')
                    
        #start detection
        '''
        matched_keywords, matched_score = keyword_index.query(text_content)
        if matched_keywords is None:
            print('Conten safe')
        else:
            print('Warning: top keywords detected:')
            for k in range(len(matched_keywords)):
                print('top %d %s %f' % (k+1, matched_keywords[k], matched_score[k]))
5        '''          
except:
    parser.print_help()