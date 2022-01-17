# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    get_coding = scrapy.Field()
    get_url = scrapy.Field()
    get_body = scrapy.Field()

    def process_item(self, item):
        #print(item)
        return item
