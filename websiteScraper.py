from urllib.request import urlopen
from urllib.parse import urlsplit, urlunsplit, urljoin
import re
from bs4 import BeautifulSoup, SoupStrainer
from bs4.element import Comment
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import collections
import numpy as np
import string
wordnet_lemmatizer = WordNetLemmatizer()

class websiteObject(object):
    '''
    Author: Greg Strabel
    websiteObject is a class for scraping and analyzing html documents
    using BeautifulSoup
    '''
    def __init__(self):
        self.ngrams = {}
    
    def get_html(self,url):
        '''
        Get the html from the given url
        '''
        
        ## Clean the url
        splitResult = urlsplit(url)

        if splitResult.scheme == '':
            splitResult = [i for i in splitResult]
            splitResult[0] = 'http'

        url = urlunsplit(splitResult)
        url = re.sub(r"/{3,}",'//',url)
        ## Finish cleaning url
        self.url = url
        response = urlopen(url)
        info = response.info()
        html = response.read()
        response.close()
        self.info = info
        self.html = html
        try:
            self.html_utf8 = html.decode('utf-8')
        except Exception as e:
            self.html_utf8 = str(e)
            print(str(e))
        
    def get_soup(self):
        '''
        Convert html to soup
        '''
        try:
            self.soup = BeautifulSoup(self.html_utf8,"lxml")
        except Exception as e:
            self.soup = str(e)
            print(str(e))
            
    def get_links_from_soup(self):
        '''
        Get hyperlinks from soup
        '''
        try:
            top_level_links = []
            for link in self.soup.find_all('a', href=True):
                link_url = urljoin(self.url,link['href'])
                top_level_links.append(link_url)        
            top_level_links = list(set(top_level_links))
            self.top_level_links = top_level_links
        except Exception as e:
            self.top_level_links = str(e)
            print(str(e))
            
    def get_visible_text(self,
                            addntl_element_parent_names = None,
                            addntl_re_match_str = None,
                            addntl_elements = None):
        # element parent names to filter out
        element_parent_names = ['style', 'script',
                                '[document]', 'head', 'title']
        # elements to filter out
        filter_elements = [u'\n']
        # add additional element parent names to filter out
        if (addntl_element_parent_names is not None) and \
            (type(addntl_element_parent_names) == list):
            element_parent_names = element_parent_names +\
            addntl_element_parent_names
        # add additional elements to filter out
        if (addntl_elements is not None) and \
            (type(addntl_elements) == list):
                filter_elements = filter_elements + addntl_elements
        def visible_text_filter(element, **kwargs):
            if element.parent.name in element_parent_names:
                return False
            elif re.match(u'<!--.*-->', str(element)):
                return False
            elif addntl_re_match_str is not None:
                for s in addntl_re_match_str:
                    if re.match(s, str(element)):
                        return False
            elif element in filter_elements:
                return False
            elif isinstance(element, Comment):
                return False
            return True
        self.visible_text = [i for i in self.soup.findAll(text=True) if
                             visible_text_filter(i,
                             element_parent_names = element_parent_names,
                             addntl_re_match_str = addntl_re_match_str,
                             filter_elements = filter_elements)]
        
    def get_ngrams(self, n=2, remove_stopwords = True,
                   change_case = 'lower', WORDS_TO_REMOVE = [],
                    stemmer = None):
        # list to hold tokenized sentences
        tokenized_sent = []
        # append tokenized sentences
        for i in self.visible_text:
            try:
                tokenized_sent.append(nltk.sent_tokenize(i)[0])
            except:
                pass
        # list to hold ngrams
        text_ngrams = []
        for ts in tokenized_sent:
            sent_x_stopwords = []
            # apply case change
            if change_case == 'lower':
                ts = ts.lower()
            elif change_case == 'upper':
                ts = ts.upper()
            elif change_case is None:
                pass
            for w in nltk.word_tokenize(ts):
                w = w.rstrip(string.punctuation)
                if stemmer == 'Porter':
                    porter_stemmer = PorterStemmer()
                    w = porter_stemmer.stem(w)
                if w not in stopwords.words('english'):
                    sent_x_stopwords.append(w)
                else:
                    sent_x_stopwords.append(u'_STOPWORD_')
            ngrams_w_stopwords = nltk.ngrams(sent_x_stopwords,n)
            for b in ngrams_w_stopwords:
                if b[0] == u'_STOPWORD_' or b[1] == u'_STOPWORD_':
                    pass
                elif b[0] in string.punctuation or b[1] in string.punctuation:
                    pass
                elif b[0] in WORDS_TO_REMOVE or b[1] in WORDS_TO_REMOVE:
                    pass
                else:
                    text_ngrams.append(b)
        self.ngrams[str(n)] = text_ngrams
        
            
if __name__ == '__main__':
    x = websiteObject()
    domain = 'healthylawn.net/'
    x.get_html(domain)
    x.get_soup()
    x.get_visible_text()
    x.get_ngrams()
    x.get_links_from_soup()