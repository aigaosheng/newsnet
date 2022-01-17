#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 19:01:18 2017

@author: gaosheng

define a text class container to encapulate extracted text for each node
and its post-processing
 
"""

class link(object):
    '''
    feature: use to identify a node type. a feature element is tag name (tag/name)
    attribute-value pair. combine 
    '''
    def __init__(self):
        self.link = {            
            'feature':{},
            'tag': [], 
            'desc': '',
            'addr': [],
                }
        
    def get_link(self):
        return 'link:' + ' '.join(self.link['addr'])
    
    def get_desc(self):
        return 'desc:' +  ' '.join(self.link['desc'])
    
    def get_feature(self):
        return 'feature:' + ' '.join(self.link['feature'].keys())
   
    def validate_link(self, link_url):
        return True
        
    