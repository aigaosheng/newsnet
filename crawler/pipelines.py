# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter
from crawler.settings import CUSTOMER_SETTING
import os

class CrawlerPipeline(object):
    def __init__(self):
        self.files = {}
        self.data_path = CUSTOMER_SETTING['SAVE_CRAWL_DATA_PATH'] #'/Users/gaosheng/Work/project/data'

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        #file = open(os.path.join(self.data_path, spider.name+'.json'), 'w+b')
        file = open(os.path.join(self.data_path, CUSTOMER_SETTING['SAVE_FILE_NAME']), 'w+b')
        self.files[spider] = file
        self.exporter = JsonLinesItemExporter(file, ensure_ascii=False)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
        
