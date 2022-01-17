import scrapy
from crawler.items import CrawlerItem
from crawler.settings import CUSTOMER_SETTING
import chardet
import re

class PageSpider(scrapy.Spider):
    name = "pages"
    link_depth = 0 #start_urls is depth 0, its link is depth 1, link of link is depth 2 ....
    
    start_urls = [
                #'http://news.6park.com/newspark/index.php?app=news&act=view&nid=',
                #'http://www.6park.com/sg.shtml',
                #'http://www.epochtimes.com/gb',
                #'http://www.zaobao.com.sg/',
                #'http://www.voachinese.com/',
                #'www.dajiyuan.com/gb/',
                'http://edition.cnn.com/china',
                'http://edition.cnn.com/opinions',
                'http://edition.cnn.com/asia',
                #'http://www.creaders.net/',
                #'http://www.peacehall.com/'
                '''
                'http://news.boxun.com/news/gb/china/page', #1.shtml',
                'http://news.boxun.com/news/gb/intl/page', #1.shtml',
                'http://news.boxun.com/news/gb/taiwan/page', #1.shtml',
                'http://news.boxun.com/news/gb/pubvp/page', #1.shtml',
                'http://news.boxun.com/news/gb/party/page', #1.shtml',
                'http://news.boxun.com/news/gb/religion/page', #1.shtml',
                'http://news.boxun.com/news/gb/yuanqing/page', #1.shtml',
                '''
                #'http://www.voanews.com/',
                
    ]

    def start_requests(self):
        for url in self.start_urls:
            self.link_depth = 0
            yield scrapy.Request(url=url, callback=self.get_link)
            #for i in range(1, 21):
                #yield scrapy.Request(url=url+str(i)+'.shtml', callback=self.get_link)
                #yield scrapy.Request(url=url+str(i)+'.shtml', callback=self.parse)

    def parse(self, response):
        #print('****** DDD 2 *********************')
        pitem = CrawlerItem()
        charcoding = self.get_codeset(response)
        pitem['get_coding'] = charcoding
        pitem['get_url'] = response.url
        pitem['get_body'] = response.body
        if charcoding is not 'utf-8':
            pitem['get_url'] = pitem['get_url'].decode(charcoding, 'ignore').encode('utf-8')
            pitem['get_body'] = pitem['get_body'].decode(charcoding, 'ignore').encode('utf-8')
        #print('****** DDD *********************')
        #print(pitem['get_body'])
        pitem.process_item(pitem)
        yield  pitem
 
    #get codeset of html
    def get_codeset(self, response):
        #typeEncode = sys.getfilesystemencoding()
        metainfo = response.xpath('//head/meta').extract() 
        charcoding = ''
        for ifo in metainfo:
            charcoding2 = re.findall('charset=(.+)', ifo) #.replace('>', ''))
            if len(charcoding2):
                charcoding = charcoding2[0].encode('utf-8').strip('\'\">')
                break
        if charcoding == '':
            charcoding = chardet.detect(response.body).get('encoding', 'utf-8')
        return charcoding
        
    #link extractor
    def get_link(self, response):
        link_counter = 0
        link_list = response.xpath('//a/@href')
        #link_list = response.xpath('//div[@class="content"]/a/@href') #voa
        #link_list = response.xpath('//li/a/@href') #peacehall
        #print(link_list)
        for lk in link_list:
            link = lk.extract()
            #ifound = re.search(u'http://www.epochtimes.com/gb', link)
            #ifound = re.search(u'/a', link) #voa
            #ifound = re.search(u'/news', link) #voa
            ifound = re.search(u'^/20', link) #cnn
            if ifound is not None:
                print(lk.extract())
                next_page = response.urljoin(link)
                yield scrapy.Request(next_page, callback=self.parse)
                link_counter += 1
                if link_counter >= CUSTOMER_SETTING['MAX_DOWNLOAD_LINKS_PER_SITE']:
                    break
        