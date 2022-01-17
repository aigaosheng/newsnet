#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 19:01:18 2017

@author: gaosheng

define a text class container to encapulate extracted text for each node
and its post-processing
 
"""

class text(object):
    '''
    feature: use to identify a node type. a feature element is tag name (tag/name)
    attribute-value pair. combine 
    '''
    def __init__(self):
        self.text = {            
            'feature':{},
            'tag': u'', 
            'title': u'',
            'text': u'',
                }
        
    def clean(self):
        return self.text
        
    