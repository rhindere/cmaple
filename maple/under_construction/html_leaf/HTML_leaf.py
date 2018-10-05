'''
Created on Mar 18, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

import re
from bs4 import BeautifulSoup
import logging
from autologging import logged, traced

# Create a logger tree.fmc...
logger = logging.getLogger(re.sub('\.[^.]+$','',__name__))

@logged(logger)
@traced(logger)
class HTML():
    """
    Under construction...
    """
    def __init__(self,maple_parent,name=None):
        
        logger.info('Initializing new HTML instance named %s' % (name))
        self.maple_parent = maple_parent
        self.name = name
        self.soup = None
        self.raw_text = None

    def load_soup(self,file=None):
        self.soup = BeautifulSoup(self.raw_text, 'html_leaf.parser')
        return self.soup

    def load_raw_text(self,file=None):
        self.raw_text = open(file,'r',encoding="utf8").read()
        return self.raw_text

    def soup_find_all(self,find_str=None):
        find_str = 'section&document-exe-dropped~strong&SHA256:'
        finds = find_str.split('~')
        this_soup = self.soup
        results = None
        for find in finds:
            find_args = find.split('&')
            if not results:
                results = this_soup.find_all(find_args)
            else:
                for result in results:
                    this_result = this_soup.find_all(find_args)
        return this_result

    def regex_findall(self,regex=None,raw_text=None,text_only=False):

        print(regex)
        if raw_text is None:
            raw_text = self.raw_text

        print(raw_text)

        results = re.findall(regex,raw_text,re.MULTILINE)
        print(results)
        text = ''
        if text_only:
            for result in results:
                text += result
            results = text

        print(results)
        return results