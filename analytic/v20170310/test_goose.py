#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 20:37:12 2017

@author: gaosheng
"""

from goose import Goose
url = 'https://www.w3schools.com/tags/tag_time.asp'
g = Goose()
#url=raw_input('url:')
article = g.extract(url=url)
print(article.title)
print(article.cleaned_text)
