# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 17:01:35 2017

@author: gao
"""

import json
import sys, os
import argparse
import codecs, re
from scrapy.selector import Selector
import settings
from keywordIndex import keywordManager
from nodeParser import NodeParser
import random
import webbrowser 
from utils import visual_html, color_me



def start_detect(html_parser, htmlcontent, url_address):
    s = html_parser.parser(htmlcontent, url=url_address)
    text_content = html_parser.format_text()
    #link_info = html_parser.format_link_info()
    #image_info = html_parser.format_image_info()
    #start detection
    matched_keywords, matched_score = keyword_index.query([text_content]) #html_parser.get_text())
    if len(matched_keywords) == 0:
         print(color_me('Conten safe', color_text='green', color_bk='black'))
    else:
        print(color_me('Warning: top keywords detected:', color_text='blue', color_bk='white') + '\n')
        for k in range(len(matched_keywords)):
            stx = '%d %s %f %d' % (k+1, matched_keywords[k], matched_score[k][0],matched_score[k][1])
            stx = color_me(stx, color_text='white', color_bk='black')
            print('top %s\n' % stx)
            
def explore_html(html_parser):
    htmlcontent = html_parser.get_html_doc()
    charcode = html_parser.get_charcode()
    #
    raw_html_file = 'raw_html.html'
    #print(test_sample)
    with codecs.open(raw_html_file, 'w', encoding = charcode) as fi:
    #with codecs.open(raw_html_file, 'w') as fi:
        #htmlcontent = htmlcontent.decode('utf-8').encode(charcode, 'ignore')
        fi.write(htmlcontent)
    clean_html_file = 'clean_html.html'
    #print(html_parser.parsed_doc['text'])
    html_parser.save_text2html(html_parser.get_text(), clean_html_file, charcode)
    cwd = os.getcwd()
    visual_html(os.path.join(cwd, raw_html_file))
    visual_html(os.path.join(cwd, clean_html_file))
    
def add_keywords(keyword_index):
    add_words = raw_input('add keywords: ')
    add_words = add_words.split(';')
    keyword_index.index_update(add_words)
    

''' main program '''    

parser = argparse.ArgumentParser()
#parser.add_argument('--infile', action='store', nargs='+', help='html document corpus')
parser.add_argument('--keyword', action='store', nargs='+', help='keyword file')

#database file
html_database = ['/home/gao/WORK/project/data/peacehall_topic.json',
                 ]

try:
    #load index
    keyword_index = keywordManager()
   # keyword_index.index(settings.TEST_KEYWORD)
    keyword_index.index(keyword_file = 'words.list') #settings.TEST_KEYWORD)
    keyword_index.save_index('index.json', readable = False)
    
    '''with open('raw_html.html', 'r') as fi:
       html_tmp = fi.read()
       html_parser =  NodeParser()
       start_detect(html_parser, html_tmp, "https://docs.python.org/2/library/webbrowser.html")
       sys.exit(1)
    '''     

        
    args = parser.parse_args(sys.argv[1:])
    #html_parser = htmlAnalytic()
    html_parser =  NodeParser()
    data_samples = []
    for fname in html_database:
       with open(fname, 'r') as fi:
           for inst in fi:
               page_data = json.loads(inst)
               data_samples += [page_data]
    #randomly
    while True:
        itm = [color_me('Q', color_text='red',style=1, color_bk='white') + ' :<quit>']
        itm += [color_me('U', color_text='red',style=1, color_bk='white') + ' :<url>']
        itm += [color_me('N', color_text='red',style=1, color_bk='white') + ' :<random from html database>']
        itm += [color_me('A', color_text='red',style=1, color_bk='white') + ' :<add keywords,split by ";">']
        itm += [color_me('V', color_text='red',style=1, color_bk='white') + ' :<view result in html>']
        itm += [color_me('K', color_text='red',style=1, color_bk='white') + ' :<view keywords in html>']
        menuitem = ' '.join(itm)+'\n\n'
        x = raw_input(menuitem)
        x = x.lower()
        if x == 'q':
            break
        elif x == 'u':
            url_address = raw_input('Input URL: ')
            if url_address.startswith('http'):
                htmlcontent = html_parser.craw_url(url_address)
                start_detect(html_parser, htmlcontent, url_address)                
            else:
                print('Wrong url address')
                
        elif x == 'n':
            test_sample = random.sample(data_samples, 1)[0]
            htmlcontent = test_sample['get_body']
            url_address = test_sample['get_url']
            start_detect(html_parser, htmlcontent, url_address)
        elif x == 'v':
            explore_html(html_parser)
        elif x == 'k':
            vocab_html_file = 'vocab.html'
            with open(vocab_html_file, 'w') as fi:
                for ss in keyword_index.get_keywords():
                    fi.write(ss + '<br>')
                
            #html_parser.save_text2html(keyword_index.get_keywords(), vocab_html_file, 'utf-8')
            cwd = os.getcwd()
            visual_html(os.path.join(cwd, vocab_html_file))

        elif x == 'a':
            add_keywords(keyword_index)
        else:
            pass
except:
    parser.print_help()
    
