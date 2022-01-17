#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 19:01:18 2017

@author: gaosheng

define a text class container to encapulate extracted text for each node
and its post-processing
 
"""
import urllib
import os

class image(object):
    '''
    feature: use to identify a node type. a feature element is tag name (tag/name)
    attribute-value pair. combine 
    '''
    def __init__(self):
        self.image = {            
            'feature':{},
            'tag': [], 
            'desc': '',
            'addr': [],
            'name':[],
                }
        self._image_extention = ['.tif', '.tiff', '.gif',
                        '.jpeg', '.jpg', '.jif', '.jfif',
                        '.jp2', '.jpx', '.j2k', '.j2c',
                        '.fpx', '.pcd', '.png',
                        '.bmp', '.img', '.jbg', '.jpe', 
                        '.pbm', '.pgm'
                        ]
        
    def get_link(self):
        return 'link:' +  ' '.join(self.image['addr'])
    
    def get_desc(self):
        return 'desc:' + ' '.join(self.image['desc'])
    
    def get_feature(self):
        return 'feature:' + ' '.join(self.image['feature'].keys())
    
    def get_image_name(self, img_url):
        name = img_url.split('/')[-1]
        return name
        
    def download_image(self, save_path):
        for img_url in self.image['addr']:
            if img_url != None:
                urllib.urlretrieve(img_url, os.path.join(save_path, self.get_image_name(img_url)))
        
    def validate_image(self, img_url):
        if img_url == None:
            return False
        name = img_url.split('/')[-1]
        basename, ext = os.path.splitext(name)
        if ext in self._image_extention:
            return True
        else:
            return False
        
        
    