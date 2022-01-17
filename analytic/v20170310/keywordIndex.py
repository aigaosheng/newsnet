# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 16:48:09 2017

class to build index from keyword, add dynamically new keywords and update index

Description:
    in keyword search, index all keywords as inverted invdex. index unit is 
    unicode
A) unicode list: 
word vocabulary list. Here word is unicode or word seperated by space in English
key: unicode_word
0: unknown
1: unicode_word_1
2: unicode_word_2
....

key: 0 reserved for OOV 
    
key              doc/keyword list            statistc of list
unicode_word_id   (keyword/doc_id, location)  (unicode_based_keyword_length(min,max), list)

B)
search:
    1. exact match: query sequence is exactly equal to keyword
    2. approximately match: no unicode location, like unigram method

@author: gao
"""

import json
import sys
import argparse
import codecs
import string, re
import numpy
import settings

#vocabulary: id=0, reserved for unknown, i.e. out-of-vocabulary, OOV
class keywordManager:
    def __init__(self, vocab = None):
        self.keywords = []
        if vocab is  None:
            self.vocab = {} #key-(word_id, frequency) 
            self.vocab_rev = {}            
        else:
            self.vocab_rev = dict()
            for w, id in enumerate(vocab):
                self.vocab_rev[id+1] = w
        #keyword dynamically added
        self.keyword_new_added = dict()
        #keyword index
        self.inverted_index = []
        #document indexed
        self.indexed_document = {}
    
    #unicode convert
    def unicode_converter(self, w):
        if not isinstance(w, unicode):
            w = unicode(w, encoding = 'utf-8')
        return w
            
    #load keyword & build vocabulary
    #keyword_list: keyword list, each entry is keyword, i.e. document
    #override: True: override loaded dictionary. False: append into
    def build_vocab(self, keyword_list = None, override = False):
        if override:
            print('Warning: override the current dictionary')
        else:
            print('Add new word into current dictionary')
        for kw in keyword_list:
            ukw = self.unicode_converter(kw)
            word_seq = self.keyword2unicode_seq(ukw)
            #incrementaly build dictionary
            for word in word_seq:
                if word in self.vocab:
                    self.vocab[word]['freq'] += 1
                else:
                    cur_wid = len(self.vocab) + 1 #0: reserved for OOV
                    self.vocab[word] = {'wid': cur_wid, 'freq': 1}
                    self.vocab_rev[cur_wid] = word
            self.vocab['UNKNOWN'] = 0
            self.vocab_rev[0] = 'UNKOWN'
    #build index
    #keyword_list: keyword as document                
    def build_index(self, keyword_list):
        self.inverted_index = [[]] * (len(self.vocab) + 1)
        for doc_id, doc_text in enumerate(keyword_list):
            doc_text = self.unicode_converter(doc_text)
            word_seq = self.keyword2unicode_seq(doc_text)
            self.indexed_document[doc_id] = (doc_text, word_seq)
            for loc, uwd in enumerate(word_seq):
                word_id = self.vocab[uwd]['wid']
                if len(self.inverted_index[word_id]):
                    self.inverted_index[word_id].append((doc_id, loc))
                else:
                    self.inverted_index[word_id] = [(doc_id, loc),]
                
    #convert unicode string into unicode word, seperate english with others 
    def keyword2unicode_seq(self, keyword):
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
    #check unicode word is in vocabuary
    def get_wordid(self, word):
        if not isinstance(word, unicode):
            word = unicode(word, encoding = 'utf-8')
        if word in self.vocab:
            return self.vocab[word]['wid']
        else:
            return 0 #return OOV
                
    #get word from word_id
    def get_word(self, word_id):
        return self.vocab_rev[word_id]
        
    #save index, indexed document & vocabulary
    def save(self, file_name):
        pass
    
    #save index
    def save_index(self, file_name, readable = False):
        try:
            if readable:
                with codecs.open(file_name, 'w', encoding = 'utf-8') as fi:
                    js_index = dict()
                    for id, cur_index in enumerate(self.inverted_index):
                        readable_index = []
                        for di in cur_index:
                            readable_index += [(self.indexed_document[di[0][0]], di[1])]
                    
                        js_index[self.get_word(id)] = readable_index
                    json.dump(js_index, fi, ensure_ascii=False, indent = 2)
            else:
                with open(file_name, 'w') as fi:
                    json.dump(self.inverted_index, fi, indent = 2)
                    '''
                    fi.write('[\n')
                    for id, cur_index in enumerate(self.inverted_index):
                        fi.write(json.dumps(cur_index))
                        if id < len(self.inverted_index) - 1:
                            fi.write(',\n')
                    fi.write('\n]')
                    '''
                    #json.dump('\\n', fi, ensure_ascii=False)
        except:
            print('Errors when save index into %s' % file_name)
    
    #query
    #query_stream: list of sentence
    #exact_match: true: if exact keyword found in query_stream. Otherwise, use approximate match
    def query(self, query_stream, match_type = 'exact'):
        #process sentence by sentence. here, sentence may be a query stream
        is_found = False
        matched_keyword = []
        matched_score = []
        for cur_query in query_stream:        
            ukw = self.unicode_converter(cur_query)
            query_seq = self.keyword2unicode_seq(ukw)
            matched_keyword, matched_score = self.exact_match(query_seq)
            if len(matched_keyword):
                is_found = True
                break
        #if is_found:
        return matched_keyword, matched_score
        #else:
        #    return None
            
    def exact_match(self, query_seq, threshold = 0.0):
        nn_query = len(query_seq)
        score = [0.0] * len(self.indexed_document)
        start_scanning = False
        start_loc = 0
        for loc, word in enumerate(query_seq):
            #get word id
            wordid = self.get_wordid(word)
            if wordid > 0:
                if not start_scanning:
                    start_scanning = True
                    start_loc = 0
                for docid, wordid_loc in self.inverted_index[wordid]:
                    if wordid_loc == start_loc:
                        score[docid] += 1. / len(self.indexed_document[docid][1])
                start_loc += 1                  
        
        score_order = numpy.argsort(score)
        '''
        for docid in score_order[::-1]:
            kword = self.indexed_document[docid][1]
            if score[docid] > 0.:
                score[docid] /= len(kword) #numpy.max([nn_query, len(kword)])
            else:
                break
        '''
        matched = []
        matched_score = []
        for k in score_order[::-1]:
            if score[k] > threshold:
                matched += [self.indexed_document[k][0]]
                matched_score += [score[k]]
            else:
                break
        return matched, matched_score
         
        
        
if __name__ == '__main__':
    print('test indexing')
    keyword_index = keywordManager()
    keyword_index.build_vocab(settings.TEST_KEYWORD)
    keyword_index.build_index(settings.TEST_KEYWORD)
    keyword_index.save_index('index.json', readable = False)
    matched_keywords, matched_score = keyword_index.query(['as 法lun **功asad'])
    if len(matched_keywords) == 0:
        print('Conten safe')
    else:
        print('Warning: top keywords detected:')
        for k in range(len(matched_keywords)):
            print('top %d %s %f' % (k+1, matched_keywords[k], matched_score[k]))
        
        #
        
        
            