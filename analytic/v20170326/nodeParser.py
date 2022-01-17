#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 16:55:39 2017

@author: gao
"""

from scrapy.selector import Selector
from nodeClassify import NodeClassify
import settings
from htmlAnalytic import htmlAnalytic
import argparse, sys
from utils import get_charset, smart_encoding, replace_with,count_words, get_charset_me
from text import text
from image import image
from link import link
import json
import codecs
import urllib3, urllib, urlparse, certifi


#IGNORE_TAGS = 'not(self::script or self::style or self::br or self::iframe or \
#                   self::noscript or self::noframe or self::legend\
#                   )'

IGNORE_ATTRIB = [
        'script'+'-GAOS'+'javascript',
        'script'+'-GAOS'+'text/javascript',
        '' + '-GAOS'+'menubar',
        '' + '-GAOS'+'menu',
        '' + '-GAOS'+'mainmenu',
        '' + '-GAOS'+'submenu',
        '' + '-GAOS'+'time'
        
        
        ]
IGNORE_TAGS = ['script', 'style', 'iframe', 'noframe',\
                 'legend', 'input', 'font']
IGNORE_TAGS_PATH = 'not(' + ' or '.join(map(lambda x:'self::'+' ' + x, IGNORE_TAGS)) + ')'

MIN_WORD_PER_SEG = 3
LINK_TEXT_SEG_RATIO = 0.5

class NodeParser(object):
    def __init__(self): #, html_doc = None):
        '''
        self.html_doc = html_doc
        if isinstance(self.html_doc, basestring):
            if isinstance(self.html_doc, str):
                self.html_doc = unicode(self.html_doc, encoding = 'utf-8')
        #define for output
        self.parsed_doc = {'text': [], 'image': [], 'link': [], 'other': []}
        self.base_url = u''
        #self.charset_code = u'utf-8'
        '''
        
    @classmethod
    def craw_url(self, url):
        htpp = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())
        get_page = htpp.request('GET', url)
        if get_page.status == 200:
            charcode = get_charset_me(get_page.data)
            content = get_page.data.decode(charcode, errors='ignore')
            return content
        else:
            return None
        
    def get_charcode(self):
        return self.charset_code
    
    def get_html_doc(self):
        return self.html_doc
    
    @classmethod
    def parser(self, input_html_doc, url=None):
        self.parsed_doc = {'text': [], 'image': [], 'link': [], 'other': []}
        
        if input_html_doc.startswith('http'):
            self.base_url = input_html_doc
            input_html_doc = self.craw_url(input_html_doc)
        else:
            self.base_url = url if url != None else u''
                
        self.charset_code, self.html_doc = smart_encoding(input_html_doc)
        #parse document
        root_node = Selector(text = self.html_doc)#self.html_doc)
        #parse meta part
        meta_sel = root_node.xpath('//head')[0]
        #parse body part
        next_nodes = root_node.xpath('//body')                
        sys.stdout.write('---- processing homepage ----\n')
        while len(next_nodes):
            #print('******')
            #sys.stdout.write(str(len(next_nodes)) + ' ')
            stack_nodes = []
            sys.stdout.write('.')
            for node in next_nodes:
                #parse single node
                node_type = NodeClassify.classifier(node)
                #print(node.root.tag)
                if any(node_type.values()):
                    if node_type['text']:
                        self.text_node_handler(node)
                    #check if there is link
                    if node_type['image']:
                        is_valid, img_p = self.image_node_handler(node)
                        if is_valid:
                            self.parsed_doc['image'] += [img_p]
                        #stack_nodes += self.node_expand(node)
                    if node_type['link']:
                        is_valid, link_p = self.link_node_handler(node)
                        if is_valid:
                            self.parsed_doc['link'] += [link_p]
                        #stack_nodes += self.node_expand(node)
                    #if node_type['text']:
                    #continue
                else:
                    #get child nodes
                    stack_nodes += self.node_expand(node)
            next_nodes = stack_nodes
        sys.stdout.write('\n--- end of homepage processing ---\n')
    @classmethod
    def node_expand(self, node):
        ex_node = []
        pth = 'child::*[%s]' % IGNORE_TAGS_PATH
        for ch_node in node.xpath(pth):
            attr_val = ch_node.root.attrib
            tag = ch_node.root.tag.lower()
            is_ignore = False
            if len(attr_val):
                for aa, vv in attr_val.items():
                    att_key = tag + '-GAOS' + vv.lower()
                    if att_key in IGNORE_ATTRIB:
                        is_ignore = True
                        break
            if not is_ignore:
                ex_node += [ch_node]
        return ex_node
    
    @classmethod
    def text_node_handler(self, node):
        #drop tag
        dropnodes = node.xpath('.//br')
        for dn in dropnodes:
            dn.root.drop_tag()
        #check if there are image in its descendent
        linktext = []
        linktext_count = 0
        link_count = 0
        img_select = '|'.join(settings.IMAGE_TRIGGER.keys())
        img_nodes = node.xpath('.//'+img_select)
        link_count += len(img_nodes)
        for nd in img_nodes:
            is_valid, ob = self.image_node_handler(nd)
            linktext += ob.image['desc']
            cc, ignore_return = count_words(ob.image['desc'])
            linktext_count += cc
            if is_valid:
                self.parsed_doc['image'] += [ob]
            #nd.root.drop_tag()
                        
        #check if there are links in its descendent
        link_select = '|'.join(settings.LINK_TRIGGER.keys())
        link_nodes = node.xpath('.//'+link_select)
        link_count += len(link_nodes)
        for nd in link_nodes:
            is_valid, ob = self.link_node_handler(nd)
            linktext += ob.link['desc']
            cc, ignore_return = count_words(ob.link['desc'])
            linktext_count += cc
            if is_valid:
                self.parsed_doc['link'] += [ob]
            #nd.root.drop_tag()
        link_density = 0.
        #for nd in img_nodes+link_nodes:
        #    nd.root.drop_tag()
        #density of link
        if link_count > 0:
            link_density = float(linktext_count) / link_count
                        
        #
        pth = 'descendant-or-self::*[%s]/text()' % IGNORE_TAGS_PATH
        #pth = 'descendant-or-self::*[%s]' % IGNORE_TAGS_PATH
        
        '''textlist = []
        for tnd in node.xpath(pth):
            if tnd.root.tag not in ['font']:
                    textlist += tnd.xpath('./text()').extract()
        '''
        textlist = node.xpath(pth).extract()
        textword_count, textlist = count_words(textlist)
        text_seg_count = len(textlist) - link_count
        textword_count_only = textword_count - linktext_count
        if text_seg_count > 0:
            text_density = float(textword_count_only) / text_seg_count 
            #if textword_count_only > 0 and float(textword_count_only) / text_seg_count >= MIN_WORD_PER_SEG:
            if text_density > max(link_density, 2.0) and len(textlist) > 2:
                #if remove link text
                if float(link_count) > text_seg_count * LINK_TEXT_SEG_RATIO:
                    #remove link text
                    #for nd in img_nodes+link_nodes:
                    #    nd.root.drop_tree()
                    for ln in textlist:
                        if ln not in linktext:
                            self.parsed_doc['text'] += [ln]
                else:
                    #for nd in img_nodes+link_nodes:
                    #    nd.root.drop_tag()                    
                    self.parsed_doc['text'] += textlist #node.xpath(pth).extract()
                            
    @classmethod
    def format_text(self):
        readable_text = ''
        for s in self.parsed_doc['text']:
            s = s.strip()
            if len(s):
                readable_text += s + '\n'

        return readable_text

    @classmethod
    def get_text(self):
        return self.parsed_doc['text']
    

    @classmethod
    def format_link_info(self):
        readable_text = ''
        for lk in self.parsed_doc['link']:
            lk_info = lk.get_link()
            lk_info += ' ' + lk.get_desc()
            lk_info += ' ' + lk.get_feature()
            readable_text += lk_info + '\n'
        return readable_text
            
    @classmethod
    def format_image_info(self):
        readable_text = ''
        for lk in self.parsed_doc['image']:
            lk_info = lk.get_link()
            lk_info += ' ' + lk.get_desc()
            lk_info += ' ' + lk.get_feature()
            readable_text += lk_info + '\n'
        return readable_text
    
    @classmethod
    def image_node_handler(self, node):
        img_box = image()
        #get attribute-value
        attr_val = self.get_node_attr(node)
        img_box.image['feature'] = {}
        for xa, xv in attr_val.items():
            ele_feat = self.generate_feature_key(xa, xv)
            if ele_feat in img_box.image['feature']:
                img_box.image['feature'][ele_feat] += 1
            else:
                img_box.image['feature'][ele_feat] = 1            
            #get src for image link
            if xa in settings.IMAGE_TRIGGER.values():
                #contruct actual URL address
                xv = urlparse.urljoin(self.base_url, xv)
                img_box.image['addr'] += [xv] 
        img_box.image['tag'] = node.root.tag
        img_box.image['desc'] = node.xpath('./text()').extract()
        #assert(len(img_box.image['addr']) == 1)
        none_count = 0
        for xvid in range(len(img_box.image['addr'])):
            xv = img_box.image['addr'][xvid]
            if not img_box.validate_image(xv):
                img_box.image['addr'][xvid] = None
                none_count += 1
        if none_count < len(img_box.image['addr']):
            return True, img_box
        else:
            return False, img_box
    
    @classmethod    
    def link_node_handler(self, node):
        link_box = link()
        attr_val = self.get_node_attr(node)
        link_box.link['feature'] = {}
        for xa, xv in attr_val.items():
            ele_feat = self.generate_feature_key(xa, xv)
            if ele_feat in link_box.link['feature']:
                link_box.link['feature'][ele_feat] += 1
            else:
                link_box.link['feature'][ele_feat] = 1
            #get src for image link
            if xa in settings.LINK_TRIGGER.values():
                #contruct actual URL address
                xv = urlparse.urljoin(self.base_url, xv)
                link_box.link['addr'] += [xv]
        link_box.link['tag'] = node.xpath('name()').extract()
        link_box.link['desc'] = node.xpath('./text()').extract()
        none_count = 0
        for xvid in range(len(link_box.link['addr'])):
            xv = link_box.link['addr'][xvid]
            if not link_box.validate_link(xv):
                link_box.link['addr'][xvid]
                none_count += 1
        if none_count < len(link_box.link['addr']):
            return True, link_box
        else:
            return False, link_box

    @classmethod
    def generate_feature_key(self, xa, xv):
        return xa+'/'+xv
    
    #get attribute-value pair, return dict{}
    @classmethod
    def get_node_attr(self, node):
        return node.root.attrib
    
        
    @classmethod
    def validate_link(self, src):
        return src
    
    def save_text2html(self, doc_content, file_name, charset):
        with codecs.open(file_name, 'w', encoding = 'utf-8') as fi:
            if isinstance(doc_content, list):
                doc_content = '<br>'.join(doc_content)
            fi.write(u''' <html>\n <head>\n <title>Clean HTML </title>\n </head>\n''')
            fi.write(u'''<body>%s</body>\n</html>'''%doc_content)


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
        #output file
        fo = codecs.open(args.ofile[0], 'w', encoding = 'utf-8', errors = 'ignore')
        
        html_parser =  NodeParser()
        #htmlana = htmlAnalytic()
        samples = []
        #print(args.ofile)
        for fname in args.infile:
            if fname.startswith('http'):
                s = html_parser.parser(fname)
                text = html_parser.format_text()
                fo.write('----- Text ----\n')
                #print(text)
                fo.write(text + '\n')
                link_info = html_parser.format_link_info()
                fo.write('----- Link ----\n')
                #print(link_info)
                fo.write(link_info+'\n')
                image_info = html_parser.format_image_info()
                fo.write('----- image ----\n')
                fo.write(image_info)
                #print(image_info)
                #sys.stdout.write(text)
            else:
                #with codecs.open(fname, 'r', encoding='utf-8', errors = 'ignore') as fi:
                with open(fname, 'r') as fi:
                    cc=0
                    for inst in fi:
                        #inst = fi.read()
                        page_data = json.loads(inst)
                        #print(page_data['get_url'])
                        #print(len(inst))
                        cc += 1
                        #
                        htmlcontent = page_data['get_body']
                        s = html_parser.parser(htmlcontent, url = page_data['get_url'])
                        text = html_parser.format_text()
                        #print(text)
                        fo.write('----- Text ----\n')
                        fo.write(text + '\n')
                        link_info = html_parser.format_link_info()
                        fo.write('----- Link ----\n')
                        #print(link_info)
                        fo.write(link_info+'\n')
                        image_info = html_parser.format_image_info()
                        fo.write('----- image ----\n')
                        fo.write(image_info)
                        #s.extractor()
                        if cc>=1:
                            break
                        sys.stdout.write('\n\n****\n'+str(cc)+'\n')
                        print(cc)
                    
        #with open(args.ofile[0], 'w') as fo:
        #    json.dump(samples, fo, indent = 0)
        fo.close()
    except:
        parser.print_help()
    
                

        
        
        