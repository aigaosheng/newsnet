#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 10:00:17 2017

@author: gao
"""
import numpy 

class node:
    def __init__(self, word_pos_doc, score, nskip, islast):
        self._value = {'score': 0., 'nskip': 0, 'islast': False}
        self._key = word_pos_doc
        self.set_value(word_pos_doc, score, nskip, islast)
    
    #when expand node, update its value if indicator is true
    #because it is count, each call incrementally add 1
    def update(self, score, nskip, islast):
        self._value['score'] = score 
        self._value['nskip'] = nskip 
        self._value['islast'] = islast 
        
    def set_value(self, word_pos_doc, score, nskip, islast):
        self._value['score'] = score
        self._value['nskip'] = nskip
        self._value['islast'] = islast
        self._key = word_pos_doc
        
    def get_score(self):
        return self._value['score']
    
    def get_nskip(self):
        return self._value['nskip']
    
    def get_islast(self):
        return self._value['islast']
    
    def get_value(self):
        return self._value
            
    def get_key(self):
        return self._key
    
class stackSearch:
    def __init__(self, n_tolerant_unmatched_word, unk_id):
        #stack to control expanansion of node
        self._stack = {}
        self._n_tolerant_unmatched_word = n_tolerant_unmatched_word
        self._found_keyword = []
        self._unk = unk_id
        
    #from word_pos key, check if exist in stack
    def has_node(self, word_pos_doc):
        return True if word_pos_doc in self._stack else False
    
    #return node if found in stack
    def get_node(self, word_pos_doc):
        return self._stack[word_pos_doc] if word_pos_doc in self._stack else None
    
    #expanded node into stack    
    def expand(self, wordid, wordid_loc = None, docid = None, is_last = None):        
        #if wordid is UNK, no extention, only increment 1 of nskip
        if wordid == self._unk:
            for ik in self._stack.keys():
                self._stack[ik]['nskip'] += 1
        else:            
            #check whether word_pos can be found satisfying continuous condition
            #in the node of stack
            word_pos = self.word_pos_key(wordid, wordid_loc, docid)
            if wordid_loc - self._n_tolerant_unmatched_word <= 0:
                #it is first matched word, so it is expanded node
                sc = 1.
                nskip = 0
                nd = node(word_pos, sc, nskip, is_last)
                if self.has_node(word_pos):
                    if self._stack[word_pos].get_score() < nd.get_score():
                        #update if new node is better than old
                        self._stack[word_pos] = nd.get_value()
                else:
                    #expand wdpos, into mew node
                    self._stack[word_pos] = nd.get_value()            
            else: 
                #check if there is node statify constrain of continuous
                first_pos = max(0, wordid_loc - 1 - self._n_tolerant_unmatched_word)
                for pre_loc in range(first_pos, wordid_loc):
                    wdpos = self.word_pos_key(wordid, pre_loc, docid)
                    if self.has_node(wdpos):
                        #continuous satisfy
                        sc = self._stack[wdpos]['score'] + 1
                        nskip = wordid_loc - 1 - first_pos
                        nd = node(word_pos, sc, nskip, is_last)
                        #check the ready expanded node is already in stack
                        if self.has_node(word_pos):
                            if self._stack[word_pos]['score'] < nd.get_score():
                                #update if new node is better than old
                                self._stack[word_pos] = nd.get_value()
                        else:
                            #expand wdpos, into mew node
                            self._stack[word_pos] = nd.get_value()
                            #remove old one
                            del self._stack[wdpos]
    #check stack if there is keyword found
    def update_found_keyword(self):
        for word_pos, value in self._stack.items():
            if value['islast']:
                pos, docid = self.rev_word_pos_key(word_pos)
                self._found_keyword += [(docid, value['score'])]
            #check drop off
            if value['nskip'] > self._n_tolerant_unmatched_word:
                del self._stack[word_pos]
            
    def get_found_keywords(self):
        return self._found_keyword
    
    def word_pos_key(self, word, pos, docid):
        return (pos, docid) #(word, pos, docid)
    
    def rev_word_pos_key(self, word_pos):
        return word_pos[0], word_pos[1]
        
    
    def get_top_matched(self, index_document, threshold):
        matched = {}
        if len(self._found_keyword) == 0:
            return matched
            
        gdocid, gscore = zip(*self._found_keyword)
        score_order = numpy.argsort(gscore)
        for k in score_order[::-1]:
            doc_id = gdocid[k]
            if gscore[k] > threshold:
                wd = index_document[doc_id][0]
                #exact match
                if wd in matched:
                    if gscore[k] > matched[wd][0]:
                        matched[wd][0] = gscore[k]
                    matched[wd][1] += 1
                else:
                    matched[wd] = [gscore[k], 1]
        
        return matched
