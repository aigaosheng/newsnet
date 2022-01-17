#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 12:11:59 2017

@author: gao
"""
import chardet
import re
import string
import platform
import webbrowser


#get codeset of html
def get_charset_me(html_doc):
    charcoding = ''
    #charcoding = re.findall('charset=[\'\"]*(.+)[\'\"]', html_doc, re.I)[0]
    charcoding_str = re.findall('charset=(.+)', html_doc, re.I)[0].split()[0]
    charcoding = charcoding_str.strip('\'\"><')
    '''
    metainfo = sel.xpath('//head/meta').extract()     
    for ifo in metainfo:
        charcoding2 = re.findall('charset=(.+)', ifo) #.replace('>', ''))
        if len(charcoding2):
            charcoding = charcoding2[0].encode('utf-8').strip('\'\">')
            break
    '''
    if len(charcoding) == 0 or charcoding == '':    
        charcoding = chardet.detect(html_doc).get('encoding', 'utf-8')
    return charcoding

def get_charset(html_doc):
    charcoding = chardet.detect(html_doc).get('encoding', 'utf-8')
    return charcoding

#unicode encoding (utf-8).
def smart_encoding(html_doc):
    charset_code = get_charset_me(html_doc)
    if isinstance(html_doc, unicode):
        return charset_code, html_doc
    if isinstance(html_doc, str):
        if charset_code != 'utf-8':
            html_doc = html_doc.decode(charset_code, 'ignore').encode('utf-8')
    else:
        print('input must be string')
        exit(-1)
                    
    return charset_code, html_doc

#replace sequence
def replace_with(pattern, seq):
    if not isinstance(seq, list):
        seq = [seq]
    for k in range(len(seq)):
        for p in pattern:
            seq[k] = re.sub(p[0], p[1], seq[k])

#count words in list sequence
def count_words(seqs):
    assert(isinstance(seqs, list))
    count = 0
    out_seqs = []
    for seq in seqs:
        seq = seq.strip(u'.-· ')
        wd = keyword2unicode_seq(seq) # seq.split()
        if len(wd):
            count += len(wd)
            out_seqs += [seq]
    return count, out_seqs

#convert to unicode sequence
def keyword2unicode_seq(keyword):
    assert(isinstance(keyword, unicode))
    seq = []
    asccii_word_mark = False
    asccii_word = ''
    unicode_word = ''
    for ch in keyword:            
        if ord(ch) < 256: 
            asccii_word += ch
        else: 
            unicode_word = ch
            asccii_word_mark = True
        if asccii_word_mark:
            if asccii_word != '':
                seq += asccii_word.lower().strip(string.punctuation).split()
                #seq += asccii_word.lower().strip().split()
            seq += unicode_word
            #reset mark
            asccii_word = ''
            unicode_word = ''
            asccii_word_mark = False
    #if asccii_word_mark:
    if asccii_word != '':
        seq += asccii_word.lower().strip(string.punctuation).split()
    if unicode_word != '':
        seq += unicode_word
    return seq

#unicode convert
def unicode_converter(w):
    if not isinstance(w, unicode):
        w = unicode(w, encoding = 'utf-8')
    return w


def visual_html(filename):
    if filename.startswith('http'):
        urlname = filename
    else:
        urlname = 'file://%s' % filename
    osname = platform.system().lower()
    if osname == 'darwin':
        browser = webbrowser.get("open -a /Applications/Google\ Chrome.app %s")
        browser.open(urlname)
    else:
        webbrowser.open(urlname)
        
def color_me(text, color_text='black', style='bold', color_bk='white'):
    color_text_dict = {'black':30, 'red':31, 'green': 32, 'yellow':33, 'blue':34,
                  'purple':35, 'cyan':36, 'white':37}
    style_dict = {'normal':0, 'bold':1, 'underline':2, 'negative1':3, 'negative2':5}
    color_bkground_dict = {'black':40, 'red':41, 'green': 42, 'yellow':43, 'blue':44,
                  'purple':45, 'cyan':46, 'white':47}
    
    if isinstance(text, basestring):
        if color_text in color_text_dict:
            tcode = color_text_dict[color_text]
        else:
            tcode = 30
        if style in style_dict:
            scode = style_dict[style]
        else:
            scode = 1
        if color_bk in color_bkground_dict:
            bcode = color_bkground_dict[color_bk]
        else:
            bcode = 47
            
        color_text_str = '\033[%d;%d;%dm%s\033[0m'%(tcode,scode,bcode,text)
    return color_text_str
        
    