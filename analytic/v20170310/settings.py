#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 21:06:05 2017

@author: gaosheng
"""

#define feature for content category detection
h_tag = []
for i in range(1, 7):
    h_tag += ['h%d'%i]
TEXT_TRIGGER = set(['b', 'i', 'tt', 'pre','cite', 'em', 'strong', \
                #'font',
                'p', \
                'blockquote',
                'dl', 'dt', 'dd', #definition term
                'ol', 'ul', 'li',  #list
                'table', 'tr', 'td', 'th', #table
                'span',
                #'frameset', 'frame', 'noframes', 
                #'div',
                ] \
                + h_tag
                )
                
#define feature for image
IMAGE_TRIGGER = {u'img':u'src'}

#define feature for link
LINK_TRIGGER = {u'a':u'href'}

#unicode control characters
UNICODE_CONTROL_CHARSET = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                         u'|' + \
                         u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                          (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                           )
                


#test keyword
TEST_KEYWORD = ['中国政F', 'tai du','藏独','西藏独立', '台独', 'Tibet free',\
                '胡锦涛', '温家宝', '温云松', '64学运', '64学潮', '89运动', \
                '共惨党', '李洪志', '大纪元', '习近平', '6-4tianwang', \
                'chinaliberal', 'freechina','法lun功', '法輪大法', '9评共产党',\
                '九评共产党', '习禁评', '习包子','习特勒', '纪念六四', '习核心'
                ]