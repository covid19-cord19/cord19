"""
Purpose: build custom inverse document frequency and use that to boost the terms before sending to solr for querying.
Author: Sharad Varshney
"""
import pickle

class Intercept:

    '''
    def __init__(self):
        self.collections_map = {"cuid": 0.98,
                                "assignment": 0.32,
                                "api": 0.1,
                                "prod": 0.55,
                                "unknown": 0.99,
                                "collection": 0.44}
     '''
    def load_dictionary(self, path, fileName):
        with open(path+ "/"+ fileName,'rb') as f:
            return pickle.load(f)

    def process_request(self, terms):
        self.dictionary = self.load_dictionary("./dictionary", "dictIDF.txt")
        term_weights = {}
        for term in terms:
            try:
                if term in self.dictionary:
                    term_weights[term]  = self.dictionary[term]
                else:
                    term_weights[term]  = 1.0
            except:
                pass
        solr_query = ' '.join(['{0}:{3}^{4} {1}:{3}^{4} {2}:{3}^{4}'.format("body", "abstract", "title", term, term_weights[term]) for term in terms])
        print(solr_query)
        return solr_query
