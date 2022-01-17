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
from utils import keyword2unicode_seq, unicode_converter
import pickle
from stackSearch import stackSearch

#vocabulary: id=0, reserved for unknown, i.e. out-of-vocabulary, OOV
class keywordManager():
    def __init__(self, keyword_list = None, keyword_file = None):
        self._unk = (0, 'UNK')
        self._index_word_size = 0
        self._new_added_index_word_size = 0
        self._keywords = []
        self._keyword_new_added = []   #keyword dynamically added
        self._vocab = {} #key-(word_id, frequency) 
        self._vocab_rev = {}                    
        #keyword index
        self._inverted_index = []
        #document indexed
        self._indexed_document = {}
        #set tolerant unknow words
        self._tolerant_unk_size = 1
        self._is_index_loaded = False #indicate: index is in memory, 
        self._location_sensitity = 1 #query and keyword difference
        
        #if give keyword_file or list, add into interal keywords list
        if keyword_file != None:
            self._keyword_new_added = list(self.load_keyword(keyword_file))
        if keyword_list is not None:
            if isinstance(keyword_list, list):
                self._keyword_new_added += keyword_list
            else:
                print('input keyword_list must be list')
                return
        

    def load_keyword(self, keyword_file):
        if not isinstance(keyword_file, list):
            keyword_file = [keyword_file]
        words_list = set()    
        for name in keyword_file:
            with open(name, 'r') as fp:
                for ll in fp:
                    word = ll.strip()
                    if word not in self._keywords:
                        words_list.add(word)
        return words_list
    
    #only for newly index    
    def index(self, keyword_list = None, keyword_file = None):
        is_append = False
        self.build_vocab(keyword_list, keyword_file, is_append)
        self.build_index(is_append)
        
    #update index for append new words
    def index_update(self, keyword_list = None, keyword_file = None):
        is_append = True
        self.build_vocab(keyword_list, keyword_file, is_append)
        self.build_index(is_append)   
    
    #load keyword & build vocabulary
    #keyword_list: keyword list, each entry is keyword, i.e. document
    #index 0: reserved for unknown words
    def build_vocab(self, keyword_list = None, keyword_file = None, is_append = False):
        if keyword_list == None and keyword_file == None:
            print('Input keyword list or keyword file must be given at least 1')
            return False
        #if give keyword_file or list
        added_words = []
        if keyword_file != None:
            added_words = list(self.load_keyword(keyword_file))
        if keyword_list is not None:
            if isinstance(keyword_list, list):
                added_words += keyword_list
            else:
                print('input keyword_list must be list')
                return False
        #verify duplicate keywords
        self._keyword_new_added = []
        for w in added_words:
            if w not in self._keywords:
                self._keyword_new_added += [w]                

        #if add new words into existing vocab
        if is_append:
            if not self._is_index_loaded:
                print('No indexed loaded. Please use False')
            else:
                print('Append into existing dictionary')
                
        if not is_append:
            self._index_word_size = 0
            self._vocab[self._unk[1]] = self._unk[0]
            self._vocab_rev[self._unk[0]] = self._unk[1]
            self._index_word_size += 1
            self._indexed_document = {}
        self._new_added_index_word_size = 0    
        
        for kw in self._keyword_new_added:
            ukw = unicode_converter(kw)
            word_seq = keyword2unicode_seq(ukw)
            #incrementaly build dictionary
            for word in word_seq:
                if word in self._vocab:
                    self._vocab[word]['freq'] += 1
                else:
                    self._vocab[word] = {'wid': self._index_word_size + self._new_added_index_word_size, 'freq': 1}
                    self._vocab_rev[self._index_word_size + self._new_added_index_word_size] = word
                    self._new_added_index_word_size += 1
                    
        self._index_word_size += self._new_added_index_word_size
        #update keywords
        self._keywords += self._keyword_new_added
        return True
    #build index
    #keyword_list: keyword as document                
    def build_index(self, is_append):
        if is_append:
            self._inverted_index = self._inverted_index + [[]] * self._new_added_index_word_size
            keyword_list = self._keyword_new_added
            first_docid = len(self._indexed_document)
        else:
            #rebuild new index
            self._inverted_index = [[]] * (self._index_word_size)
            keyword_list = self._keywords
            first_docid = 0
            
        for doc_id2, doc_text in enumerate(keyword_list):
            doc_id = doc_id2 + first_docid
            doc_text = unicode_converter(doc_text)
            word_seq = keyword2unicode_seq(doc_text)
            self._indexed_document[doc_id] = (doc_text, word_seq)
            is_last_word = False
            for loc, uwd in enumerate(word_seq):
                if loc == len(word_seq) - 1:
                    is_last_word = True
                word_id = self._vocab[uwd]['wid']
                if len(self._inverted_index[word_id]):
                    self._inverted_index[word_id].append((doc_id, loc, is_last_word))
                else:
                    self._inverted_index[word_id] = [(doc_id, loc, is_last_word)]
        #update keyworwords
        self._is_index_loaded = True
                
    #check unicode word is in vocabuary
    def get_wordid(self, word):
        if not isinstance(word, unicode):
            word = unicode(word, encoding = 'utf-8')
        if word in self._vocab:
            return self._vocab[word]['wid']
        else:
            return 0 #return OOV
                
    #get word from word_id
    def get_word(self, word_id):
        return self._vocab_rev[word_id]
        
    #save index, indexed document & vocabulary
    def save(self, file_name):
        pass
    
    #save index
    def save_index(self, file_name, readable = False):
        try:
            if readable:
                with codecs.open(file_name, 'w', encoding = 'utf-8') as fi:
                    js_index = dict()
                    for id, cur_index in enumerate(self._inverted_index):
                        readable_index = []
                        for di in cur_index:
                            readable_index += [(self._indexed_document[di[0][0]], di[1])]
                    
                        js_index[self.get_word(id)] = readable_index
                    json.dump(js_index, fi, ensure_ascii=False, indent = 2)
            else:
                with open(file_name, 'w') as fi:
                    #json.dump({'inverted_index'}: self._inverted_index, fi)
                    dump_data = {'_index_word_size':self._index_word_size,
                                 '_keywords': self._keywords,
                                 '_vocab': self._vocab,
                                 '_inverted_index': self._inverted_index,
                                 '_indexed_document': self._indexed_document,
                                 '_tolerant_unk_size': self._tolerant_unk_size,
                                 
                                 }
                    pickle.dump(dump_data, fi)
                    
                    
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
    
    def load_index(self, index_file):
        with open(index_file, 'r') as fi:
            dump_data = pickle.load(fi)
            self._index_word_size = dump_data['_index_word_size']
            self._keywords = dump_data['_keywords']
            self._vocab = dump_data['_vocab']
            self._inverted_index = dump_data['_inverted_index']
            self._indexed_document = dump_data['_indexed_document']
            self._tolerant_unk_size = dump_data['_tolerant_unk_size']
            self._is_index_loaded = True
            return True
        return False
        
    
    #query
    #query_stream: list of sentence, each sentence as input to be checked
    #exact_match: true: if exact keyword found in query_stream. Otherwise, use approximate match
    def query(self, query_stream, match_type = 'exact', is_show_all = True):
        #process sentence by sentence. here, sentence may be a query stream
        is_found = False
        matched_keyword = []
        matched_score = []
        for cur_query in query_stream:        
            ukw = unicode_converter(cur_query)
            query_seq = keyword2unicode_seq(ukw)
            #found_keyword, found_score = self.exact_match(query_seq, is_show_all)
            found_keyword, found_score = self.stack_match(query_seq, self._tolerant_unk_size, 0)
            if len(matched_keyword):
                is_found = True
            if is_found and not is_show_all:    
                break
            matched_keyword += found_keyword
            matched_score += found_score
        #if is_found:
        return matched_keyword, matched_score
        #else:
        #    return None
        
    #exact match:
    #keyword exactly occurs in input query sequence, i.e. word-location sensitive
    #sequently scanning input from start untill find first token in keywords
    def exact_match(self, query_seq, threshold = 1.0e-5, is_show_all = True):
        found_keyword_score =[]
        found_keyword_id =[]
        partial_found_keyword_score = [0.0] * len(self._indexed_document)
        partial_found_keyword_id =[]
        score = [0.0] * len(self._indexed_document)
        isfound = [False] * len(self._indexed_document)
        start_scanning = False
        start_loc = 0
        n_unk_found = 0
        is_stop_search = False
        for loc, word in enumerate(query_seq):
            #get word id
            wordid = self.get_wordid(word)
            if wordid != self._unk[0]:
                if not start_scanning:
                    start_scanning = True
                    start_loc = 0
                #seach in keywords with wordid as first
                is_broken_search = True
                for docid, wordid_loc, is_last in self._inverted_index[wordid]:
                    #if wordid_loc == start_loc:
                    #if (wordid_loc - start_loc) <= self._location_sensitity:
                    if wordid_loc == start_loc:
                            
                        score[docid] += 1.# / len(self._indexed_document[docid][1])
                        isfound[docid] = is_last
                        is_broken_search = False
                #start_loc += 1
            else:
                n_unk_found += 1
                is_broken_search = False
                if n_unk_found > self._tolerant_unk_size:
                    is_broken_search = True

            if any(isfound) or loc == len(query_seq)-1 or is_broken_search:
                for ik in range(len(score)):
                    if isfound[ik]:
                        found_keyword_score += [score[ik]]
                        found_keyword_id += [ik]
                        #reset
                        score[ik] = 0
                        isfound[ik] = False
                        
                if any(isfound) or loc == len(query_seq)-1:
                    is_stop_search = True
                    score = [0.0] * len(self._indexed_document)
                    isfound = [False] * len(self._indexed_document)
                    start_scanning = False
                    start_loc = 0
                if is_broken_search:
                    score = [0.0] * len(self._indexed_document)
                    isfound = [False] * len(self._indexed_document)
                    start_scanning = False
                    start_loc = 0
                    n_unk_found = 0
                else:
                    score = [0.0] * len(self._indexed_document)
                    isfound = [False] * len(self._indexed_document)
                    start_scanning = False
                    start_loc = 0
                    n_unk_found = 0
            else:
                start_loc += 1
            
                   
            if not is_show_all:
                if is_stop_search:
                    break
         #check if found anyone
        '''if any(isfound):
           for ik in range(len(score)):
               if isfound[ik]:
                   found_keyword_score += [score[ik]]
                   found_keyword_id += [ik]
        '''        
        matched = self.get_top_matched(found_keyword_score, found_keyword_id, 1)
        
        #partial_found_keyword_id = range(len(partial_found_keyword_score))
        #mch, mch_score = self.get_top_matched(partial_found_keyword_score, partial_found_keyword_id, 0)
        #matched += mch
        #matched_score += mch_score

        match_words =[]
        matched_score = []
        for w, sc in sorted(matched.items(), key=lambda x:x[1][0]):
            match_words += [w]
            matched_score += [sc]
        
        return match_words[::-1], matched_score[::-1]
    

    def get_top_matched(self, score, score_id, threshold):
        score_order = numpy.argsort(score)
        matched = {}
        for k in score_order[::-1]:
            doc_id = score_id[k]
            if score[k] > threshold:
                wd = self._indexed_document[doc_id][0]
                #exact match
                if score[k] >= len(wd):                    
                    if wd in matched:
                        if score[k] > matched[wd][0]:
                            matched[wd][0] = score[k]
                        matched[wd][1] += 1
                    else:
                        matched[wd] = [score[k], 1]
            else:
                break            
        #sort
        #sorted(matched.items(), key=lambda x:x[1][0])
        #matched_score = matched.values()
        
        return matched
    
    #this is stack based search
    #n_tolerant_unmatched_word: how many maximal unmatched word is allowed
    def stack_match(self, query_seq, n_tolerant_unmatched_word, threshold_score = 1.0e-5, is_show_all = True):
        stack_monitor = stackSearch(n_tolerant_unmatched_word, self._unk[0])
        for loc, word in enumerate(query_seq):
            #get word id
            wordid = self.get_wordid(word)
            if wordid != self._unk[0]:
                for docid, wordid_loc, is_last in self._inverted_index[wordid]:
                    stack_monitor.expand(wordid, wordid_loc, docid, is_last)
            else:
               stack_monitor.expand(wordid)
            #get keyword
            stack_monitor.update_found_keyword()
        #
        matched = stack_monitor.get_top_matched(self._indexed_document, threshold_score)
        
        match_words =[]
        matched_score = []
        for w, sc in sorted(matched.items(), key=lambda x:x[1][0]):
            match_words += [w]
            matched_score += [sc]
        
        return match_words[::-1], matched_score[::-1]
    
    def show_keywords(self):
        for w in self._keywords:
            sys.stdout.write(w + ', ')
            
    def show_vocab(self):
        for w, v in self._vocab.items():
            sys.stdout.write(w + ':' + str(v) + '\n')
            #print(v['freq'])
    def get_keywords(self):
        return self._keywords
        
if __name__ == '__main__':
    print('test indexing')
    keyword_index = keywordManager()
    keyword_index.index(settings.TEST_KEYWORD)
    keyword_index.save_index('index.json', readable = False)
    #keyword_index.load_index('index.json')
    #keyword_index.show_vocab()
    #keyword_index.show_keywords()
    #keyword_index.index_update(['asad大法'])
    #keyword_index.save_index('index.json', readable = False)
    matched_keywords, matched_score = keyword_index.query(['fada共上惨党yuan'], is_show_all = True)
    if len(matched_keywords) == 0:
        print('Conten safe')
    else:
        print('Warning: top keywords detected:')
        for k in range(len(matched_keywords)):
            print('top %d %s %f' % (k+1, matched_keywords[k], matched_score[k][0]))
        
        #
        
        
            