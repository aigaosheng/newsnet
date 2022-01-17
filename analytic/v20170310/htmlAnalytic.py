# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 12:57:53 2017

@author: gao
"""
import json
import sys
import argparse
import codecs, re
import scrapy
from scrapy.selector import Selector
import settings
import urllib3
import certifi


class htmlAnalytic:
    def __init__(self):
        #self.content_category = dict({'text':[], 'image':[], 'audio':[], 'video':[], 'link': []})
        pass
        #o_format_context = dict({'text':[], 'image':[], 'video':[], 'audio': []})
        
    #parse elements from html and categorize the element content to correspondint category
    # @classmethod    
    def content_parser(self, html_content):
        self.content_category = dict({'text':[], 'image':[], 'audio':[], 'video':[], 'link': []})
        #print(html_content)
        content_nodes = Selector(text = html_content).xpath("//body//*[not(self::script or self::style or self::br)]") #text()[normalize-space(.)]")
        #//*[not(self::script or self::style)]/text()[normalize-space(.)]
        #link = Selector(text = html_content).xpath("//body//*[not(self::script)]") #text()[normalize-space(.)]")
        for i_node in content_nodes:
            text_list = i_node.xpath('./text()').extract()
            word_seq = u''
            for w in text_list:
                word_seq += w.strip()
            word_seq = self.strip_control_chars(word_seq)
            #get node name
            node_name = i_node.xpath('name(.)').extract()
            #print('-------')
            #print(i_node)
            #print(word_seq)
            #print(node_name[0])
            #attr_name = []
            #attr_value = []
            attr = {}
            for index, attribute in enumerate(i_node.xpath('@*'), start=1):
                attr_name = i_node.xpath('name(@*[%d])' % index).extract_first()
                attr_value = i_node.xpath('@*[%d]' % index).extract_first()
                attr[attr_name] = attr_value
            
            #node content classification                
            ctype = self.content_classifier(node_name[0], attr)
            if ctype is 'text':
                if len(word_seq) > 0:
                    self.content_category[ctype] += [word_seq]
                    #print(' '.join(self.content_category[ctype]))
            elif ctype is 'link':
                self.content_category[ctype] += [attr[settings.LINK_TRIGGER['a']]]
                #print(self.content_category[ctype])
            elif ctype is 'image':
                self.content_category[ctype] += [attr[settings.IMAGE_TRIGGER['img']]]
                    #print(self.content_category[ctype])
            else:
                pass
        #print('-- TEXT --')
        #print('\n'.join(self.content_category['text']))             
        '''print('-- IMAGE --')
        print(' '.join(self.content_category['image']))
        print('-- LINK --')
        print(' '.join(self.content_category['link']))'''
        return self.content_category['text']
          
                #print(ch_count)
    #classify content into different category
    #@classmethod
    def content_classifier(self, node_name, attr):
        #print(node_name in settings.LINK_TRIGGER)
        #print(set(settings.LINK_TRIGGER.keys()))
        #print(set(attr.keys()))
        #print(attr)
        
        content_type = None
        if node_name in settings.TEXT_TRIGGER:
            content_type = 'text'
        elif node_name in settings.LINK_TRIGGER and \
            len(set.intersection(set(settings.LINK_TRIGGER.values()), set(attr.keys()))) > 0:
            content_type = 'link'
        elif node_name in settings.IMAGE_TRIGGER and \
            len(set.intersection(set(settings.IMAGE_TRIGGER.values()), set(attr.keys()))) > 0:
            content_type = 'image'
        else:
            content_type = None
        return content_type
        
    #remove unicode control character
    def strip_control_chars(self, inseq):    
        if inseq:
            inseq = re.sub(settings.UNICODE_CONTROL_CHARSET, "", inseq)
            # ascii control characters
            inseq = re.sub(r"[\x01-\x1F\x7F]", "", inseq)
        return inseq
    
    #remove unicode control character
    def craw_url(self, url):
        htpp = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())
        get_page = htpp.request('GET', url)
        if get_page.status == 200:
            return get_page.data
        else:
            return None
            
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', action='store', nargs='+', help='html document corpus')
    parser.add_argument('--ofile', action='store', nargs=1, help='output file to save clear data')
    test_data='''
        <html>
        <head>
        <base href='http://example.com/' />
        <title>Example website</title>
        </head>
        <body>
        <div id='images'>
        <a href='image1.html'>Name: My image 1 <br /><img src='image1_thumb.jpg' /></a>
        <a href='image2.html'>Name: My image 2 <br /><img src='image2_thumb.jpg' /></a>
        <a href='image3.html'>Name: My image 3 <br /><img src='image3_thumb.jpg' /></a>
        <a href='image4.html'>Name: My image 4 <br /><img src='image4_thumb.jpg' /></a>
        <a href='image5.html'>Name: My image 5 <br /><img src='image5_thumb.jpg' /></a>
        </div>
        </body>
        </html>
    '''
    try:
        args = parser.parse_args(sys.argv[1:])
        html_parser = htmlAnalytic()
        samples = []
        #print(args.infile)
        #print(args.ofile)
        for fname in args.infile:
            print(fname.startswith('http'))
            if fname.startswith('http'):
                htmlcontent = html_parser.craw_url(fname)
                s = html_parser.content_parser(htmlcontent)
            else:
                #with codecs.open(fname, 'r', encoding='utf-8', errors = 'ignore') as fi:
                with open(fname, 'r') as fi:
                    for inst in fi:
                        #inst = fi.read()
                        page_data = json.loads(inst)
                        #print(page_data['get_url'])
                        #print(len(inst))
                        cc += 1
                        #
                        htmlcontent = page_data['get_body']
                        s = html_parser.content_parser(htmlcontent)
                        #s.extractor()
                        if cc>=1:
                            break
                        sys.stdout.write('\n\n****\n'+str(cc)+'\n')
                        print(cc)
                    
        #with open(args.ofile[0], 'w') as fo:
        #    json.dump(samples, fo, indent = 0)
    except:
        parser.print_help()