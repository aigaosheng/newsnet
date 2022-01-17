#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:54:10 2017

@author: gao
"""
from scrapy.selector import Selector
import settings
import re

KNOWN_ARTICLE_CONTENT_TAGS = [
    {'attr': 'itemprop', 'value': 'articleBody'},
    {'attr': 'class', 'value': 'post-content'},
    {'attr': 'class', 'value': 'article'},
    {'tag': 'article'},
]
IGNORE_TEXT_ATTR = [
        {'attr': 'class', 'value': 'navigation'}
        ]

class NodeClassify(object):
    def __init__(self):
        pass
    
    #node: selector type
    @classmethod
    def classifier(self, node):
        if not isinstance(node, Selector):
            print('node type must be scrapy.selector')
            return None
        node_type = {'text':False, 'image':False, 'link':False}
        ele_node = node.root
        node_name = ele_node.tag
        attr_value = ele_node.attrib
        #if it is leaf node, it is text 
        #if ele_node.text != None and len(ele_node.text.strip()):
        node_type['text'] = self.isTextNode(node_name, attr_value)
        node_type['image'] = self.isImageNode(node_name, attr_value)
        node_type['link'] = self.isLinkNode(node_name, attr_value)
        
        return node_type
    
    #if text
    @classmethod
    def isTextNode(self, name, attr_value):        
        if name in settings.TEXT_TRIGGER:
            return True
        else:
            for item in KNOWN_ARTICLE_CONTENT_TAGS:
                if 'attr' in item and 'value' in item:
                    if item['attr'] in attr_value and item['value'] == attr_value[item['attr']]:
                        return True
                if 'tag' in item:
                    if item['tag'] == name:
                        return True
                
        return False
    
    #if Link
    @classmethod
    def isLinkNode(self, name, attr_value):
        if name in settings.LINK_TRIGGER and \
            len(set.intersection(set(settings.LINK_TRIGGER.values()), set(attr_value.keys()))) > 0:
                return True
        return False

    @classmethod
    def isImageNode(self, name, attr_value):
        if name in settings.IMAGE_TRIGGER and \
            len(set.intersection(set(settings.IMAGE_TRIGGER.values()), set(attr_value.keys()))) > 0:
                return True
        return False
            
        