#!/usr/bin/env python
"""
Program: document_search_engine.py
Purpose: Used to create IDF dictionary of the docuemnts
Author:
       - Sharad Varshney                sharad.varshney@gmail
       - Jatin Sharma                   jatinsharma7@gmail.com
       - Guruprasad Ahobalarao          gahoba@gmail.com
       - Krishnanand Kuruppath
Created: June 16, 2020
"""
import pandas as pd
import numpy as np
import os
import re
import nltk
import json
import yaml
import pickle
from bs4 import BeautifulSoup
from nltk.stem import SnowballStemmer
from nltk.tokenize import sent_tokenize
from typing.re import Pattern

from nltk import flatten
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('stopwords')
nltk.download('wordnet')

CONFIG = os.path.join(os.path.dirname(__file__), 'config.yml')
with open(CONFIG) as cfg_file:
    cfg = yaml.load(cfg_file)
    cfg_file.close()

def readData(dirs, basepath):
    docs = []
    list1 = ["pdf_json", "pmc_json"]
    document_count = 0
    for dir_json in list1:
        pathVar = os.path.join(basepath, dir_json)
        print("Path pathVar : " + pathVar)
        for entry in os.listdir(pathVar):
            if os.path.isfile(os.path.join(pathVar, entry)):
                print(entry)
                with open(os.path.join(pathVar, entry), "r") as file:
                    doc = json.loads(file.read())
                    actual_body = ""
                    for body in doc["body_text"]:
                        if "text" in body:
                            actual_body = body["text"]
                            full_text = "".join(actual_body)
                    abstract = ""
                    title = ""
                    paper_id = ""
                    if ("abstract" in doc) and (doc["abstract"] is not None and len(doc["abstract"]) > 0):
                        abstract = doc["abstract"][0]["text"]
                    if ("paper_id" in doc) and (doc["paper_id"] is not None):
                        paper_id = doc["paper_id"]
                    if ("title" in doc["metadata"]) and (doc["metadata"]["title"] is not None):
                        title = doc["metadata"]["title"]
                    if ("authors" in doc["metadata"]) and (doc["metadata"]["authors"] is not None):
                        authors = doc["metadata"]["authors"]
                    docs.append([title, abstract, full_text])
    # Pandas Dataframe containing the title, abstract and body text
    papers_df = pd.DataFrame(docs, columns = ["title", "abstract", "full_text"])
    return papers_df

class Preprocessor(object):
    class CleanRegex(object):
        '''Regexes that can be passed to the `clean_regexes` parameter of Preprocessor.__init__().
        '''
        HexaDecimalNumber = r'0x[a-fA-F0-9]+' # e.g. 0x414548b0
        # e.g. /home/build/rs_110_64_24_RTM/usr.src/sys/netscaler/nsppe_utils.c, file://sjctaasfs01.citrite.net/upload/uploads/77549499
        FilePath = r'(^|\s|file:/)/[a-zA-Z0-9_./-]+'
        WindowsNetworkFilePath = r'\\\\[a-zA-Z0-9._\\-]+' # e.g. \\sjctaasfs01.citrite.net\upload\uploads\72809412
        DirectoryPermissionUnix = r'[d-][r-][w-][x-][r-][w-][x-][r-][w-][x-]' # e.g. drwxr-xr-x
        MonthName = r'\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b'
        Time12Hr = r'\b[0-9]?[0-9]:[0-9][0-9] (AM|PM)\b' # time with AM/PM, e.g. 8:43 AM, 12:46 PM
        DayNameShort = r'\b(Sun|Mon|Tue|Wed|Thu|Fri|Sat)\b'
        DayNameLong = r'\b(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\b'
        EmailHeader = r'(From|Sent|To|Date|Sent|Cc|Subject): '

    def __init__(self, include_domain_specific=True, include_chars='', min_word_len=2, clean_regexes=None):
        self.testFlag = True
        self.p_nonalnum = re.compile(r'[^a-zA-Z0-9{}]'.format(include_chars))
        self.p_nonalpha = re.compile(r'[^a-zA-Z{}]'.format(include_chars))
        self.p_whitespace = re.compile(r'\s+')
        self.p_url = re.compile(r'https?://[^\s`\'"]+')
        clean_regexes = clean_regexes if clean_regexes else []
        self.clean_patterns = []
        for regex in clean_regexes:
            if isinstance(regex, str):
                pattern = re.compile(regex)
            elif isinstance(regex, Pattern):
                pattern = regex
            else:
                raise TypeError(f'clean_regexes entry "{regex}" should be of type string or re.Pattern')
            self.clean_patterns.append(pattern)
        self.wordnetLemmatizer = WordNetLemmatizer()
        self.snowballStemmer = SnowballStemmer('english')
        self.min_word_len = min_word_len
        self.stopwords = self.get_stopwords(include_domain_specific)

    def get_stopwords(self, include_domain_specific=True):
        stop_words = []
        for sw in stopwords.words('english'):
            stop_words.extend(self.clean(sw).split())
        stop_words.extend(['please', 'use', 'may'])
        if include_domain_specific:
            stop_words.extend(['py', 'cisco'])
        return set(stop_words)

    def is_stop_word(self, word, min_len=2):
        return word in self.stopwords or len(word) < min_len

    def clean_using_patterns(self, text):
        for pattern in self.clean_patterns:
            text = pattern.sub(' ', text)
        return text

    def clean(self, text, remove_numbers=False, apply_clean_patterns=False):
        if apply_clean_patterns:
            text = self.clean_using_patterns(text)
        if remove_numbers:
            text = self.p_nonalpha.sub(' ', text)
        else:
            text = self.p_nonalnum.sub(' ', text)
        return self.p_whitespace.sub(' ', text).strip()

    def stem(self, term):
        return self.snowballStemmer.stem(term)

    def lemmatize(self, token):
        wnl = self.wordnetLemmatizer
        lemmas = [token]
        if len(token) >= 3:
            lemmas.append(wnl.lemmatize(token, pos=wordnet.NOUN))
            lemmas.append(wnl.lemmatize(token, pos=wordnet.VERB))
            lemmas.append(wnl.lemmatize(token, pos=wordnet.ADJ))
            lemmas.append(wnl.lemmatize(token, pos=wordnet.ADV))
            lemmas.append(wnl.lemmatize(token, pos=wordnet.ADJ_SAT))
        return min(lemmas, key=lambda x: len(x))

    def clean_and_tokenize(self,
                           text,
                           stop=True,
                           lowercase=True,
                           removeUrls=True,
                           remove_html=True,
                           lemmatize=True,
                           remove_numbers=False,
                           apply_clean_patterns=True,
                           tokenize=True):
        if not text:
            return []
        if apply_clean_patterns:
            text = self.clean_using_patterns(text)
        if remove_html:
            text = BeautifulSoup(text, 'lxml').text
        if removeUrls:
            text = self.p_url.sub(' ', text)
        if lowercase:
            text = text.lower()
        text = self.clean(text, remove_numbers)
        if tokenize:
            tokens = text.split()
            if stop:
                tokens = [token for token in tokens if not self.is_stop_word(token, self.min_word_len)]
            if lemmatize:
                tokens = [self.lemmatize(token) for token in tokens]
            return tokens
        return text

    def get_sentences_from_doc(self, doc, break_on_newline=False):
        '''Assumption: doc is a string/list/dict'''
        sents = []
        if isinstance(doc, str):
            try:
                struct_doc = json.loads(doc)
                sents = self.get_sentences_from_doc(struct_doc)
            except:
                sents = sent_tokenize(doc)
                if break_on_newline:
                    sents1 = []
                    for sent in sents:
                        for s in sent.split('\n'):
                            s = s.strip()
                            if s:
                                sents1.append(s)
                    sents = sents1
        elif isinstance(doc, list):
            sents = []
            for item in doc:
                sents.extend(self.get_sentences_from_doc(item))
        elif isinstance(doc, dict):
            sents = self.get_sentences_from_doc(list(doc.values()))
        elif doc:
            sents = [str(doc)]
        return sents

class FieldNameCleaner(object):
    def __init__(self, cache_names=False):
        # match all except alnum, space, undescore
        self.alnum_space_underscore_pat = re.compile(r'[^0-9a-zA-Z_\s]')
        # white space
        self.whitespace_pat = re.compile(r'\s+')
        # camel case --- lower to upper transition
        self.camel_case_lower_to_upper_pat = re.compile(r'([a-z0-9])([A-Z])')
        # camel case --- upper to lower transition
        self.camel_case_upper_to_lower_pat = re.compile(r'([A-Z])([A-Z][a-z0-9])')
        self.cache_names = cache_names
        if cache_names:
            self.name_cache = {}

    def get_clean_name(self, name):
        if self.cache_names and name in self.name_cache:
            return self.name_cache[name]

        # clean to remove non-alnum, space, underscore
        cleaned_name = self.alnum_space_underscore_pat.sub(' ', name)
        # replace white space with underscore
        cleaned_name = self.whitespace_pat.sub('_', cleaned_name)
        # insert underscore in lower to upper transition
        cleaned_name = self.camel_case_lower_to_upper_pat.sub(r'\1_\2', cleaned_name)
        # insert underscore in upper to lower transition
        cleaned_name = self.camel_case_upper_to_lower_pat.sub(r'\1_\2', cleaned_name)
        # lower case
        cleaned_name = cleaned_name.lower()

        if self.cache_names:
            self.name_cache[name] = cleaned_name

        return cleaned_name

def save_obj(obj, name , fileType='pkl'):
            with open('/opt/code/COVID19/dictionary'+ name + '.'+ fileType, 'wb') as f:
                pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def main():
    papers_df = readData(["pdf_json", "pmc_json"], cfg["data_path"])
    papers_df["abstract_fullText"] = papers_df["abstract"] + papers_df["full_text"]
    papers_df.drop(columns=['title', 'abstract', 'full_text'], inplace=True)

    text_preprocessor = Preprocessor()
    papers_df['abstract_fullText_Cleaned'] = papers_df['abstract_fullText'].map(
        lambda text: text_preprocessor.clean_and_tokenize(text, stop=False, lowercase=True, removeUrls=False,
                                                          remove_html=False, lemmatize=False, remove_numbers=False,
                                                          tokenize=False))
    terms = papers_df['abstract_fullText_Cleaned'].map(
        lambda text: text_preprocessor.clean_and_tokenize(text, stop=True, lowercase=False, removeUrls=True,
                                                          remove_html=True, lemmatize=False, remove_numbers=True,
                                                          tokenize=True))

    arrayTerm = terms.ravel().tolist()
    flattenedTerms = flatten(arrayTerm)

    ## Create Vocabulary
    vocabulary = set(flattenedTerms)
    vocabulary = list(vocabulary)
    # Intializating the tfIdf model
    tfidf = TfidfVectorizer(vocabulary=vocabulary, dtype=np.float32, min_df=0, max_df=0.8, use_idf=True,
                            smooth_idf=True, sublinear_tf=True)
    # Fit the TfIdf model
    tfidf.fit(papers_df.abstract_fullText_Cleaned)
    dictIDF = dict(zip(tfidf.vocabulary_, tfidf.idf_))
    save_obj(dictIDF, "dictIDF", 'txt')
    print("Dictionary successfully created")

if __name__ == '__main__':
    main()

