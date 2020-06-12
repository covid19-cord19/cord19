"""
Program: app.py for Flask Server
Purpose: Main app for running Flask server for AI based APIs
Author: 
       - Sharad Varshney                sharad.varshney@gmail.com
       - Jatin Sharma                   jatinsharma7@gmail.com
       - Guruprasad Ahobalarao          gahoba@gmail.com
       - Krishnanand Kuruppath
"""
import os
import sys

import yaml
import argparse
from flask import Flask
from flask import request
import pysolr
import json
import tensorflow as tf
#tf.executing_eagerly()
tf.disable_v2_behavior()
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow_hub as hub
import pandas as pd

import imp
intercept = imp.load_source('Intercept', './solr_intercepts/solr_intercept.py')
text_preprocessor = imp.load_source('Preprocessor', './text/preprocessor.py')
#document_similarity = imp.load_source('Sentence_Similarity', './solr_intercepts/document_similarity.py')
#from util import Intercept
#from text.preprocessor import Preprocessor

CONFIG = os.path.join(os.path.dirname(__file__), 'config.yml')
with open(CONFIG) as cfg_file:
    cfg = yaml.load(cfg_file)
    cfg_file.close()

#text_preprocessor = Preprocessor


app = Flask(__name__)

# init
#init = tf.global_variables_initializer()
#init2 = tf.tables_initializer()

def getDescription(jsonInput):
    description = ""
    if (jsonInput is not None):
        jsonInput = json.loads(jsonInput)
        data = pd.DataFrame(jsonInput['raw_response']['response']['docs'])
        # filteredDF = data.loc[:,["paperid", "body"]]
    else:
        return ("")
    return (data)

def getMetadata():
    pd.set_option('display.max_colwidth', -1)
    metadata = pd.read_csv("../../data/metadata.csv", encoding="utf-8", low_memory=False)
    metadata = metadata[["sha", "pmcid", "url"]]
    return metadata

def findURL(documentDF, metadataDF):
    documentDF["url"] = documentDF["id"].map(lambda x : metadataDF[metadataDF["pmcid"] == x]["url"] if(x.startswith("PMC")) else metadataDF[metadataDF["sha"] == x]["url"])
    return documentDF


#def getEmbeddings(self, session, messages):
    # Import the Universal Sentence Encoder's TF Hub module
#    embed = hub.Module(self.module_url)
#    message_embeddings = session.run(embed(messages))
#    return message_embeddings

@app.route('/search', methods=['POST'])
def search():
    req = request.get_json()
    print(req)
    #query = req['task'] + req['sub-task']
    query = req['task']
    # do regular search
    print(query)
    terms = text_preprocessor.Preprocessor().clean_and_tokenize(query, stop=True, lowercase=True, removeUrls=False,
                                                 remove_html=False, lemmatize=False, remove_numbers=False)
    print(terms)
    final_query = process_request_for_custom_idf(terms)
    # assemble search parameters
    search_params = {
        'q': final_query,
        'fq': ' '.join(['{0}:{1}'.format("body", term,) for term in cfg['fq_list'].split(',')]),
        'start': 0,
        'rows': 10
    }

    solr = pysolr.Solr(cfg['solr_url'], timeout=60)
    results = solr.search(**search_params)

    print("Query  == ", query)
    documentDF = getDescription(toJSON(results))
    messages_docs = list(documentDF['body'])

    embed = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-large/3")
    with tf.Session() as session:
         session.run([tf.global_variables_initializer(), tf.tables_initializer()])
         taskEmbeddings = session.run(embed([query]))
         docsEmbeddings = session.run(embed(messages_docs))
    
    # Find similarity for Query vs all documents
    score = []
    i = 0
    for task in range(0, len(taskEmbeddings)):
         j = 1
         for doc in range(0, len(docsEmbeddings)):
             cos_sim = cosine_similarity(taskEmbeddings[task].reshape(1, -1), docsEmbeddings[doc].reshape(1, -1))
             score.append(round(cos_sim[0][0], 3))
             print('Cosine similarity: Task {0} Document {1} = {2}'.format(i, j, round(cos_sim[0][0], 3)))
             j = j + 1
         i = i + 1
    documentDF['score'] = score
    documentDF.sort_values(by=['score'], ascending=False, inplace=True)

    metadataDF = getMetadata()
    documentDF = findURL(documentDF, metadataDF)

    #final_result = document_similarity.Document_Similarity().getSimilarityRanking(query, toJSON(results))

    #return toJSON(query)
    return documentDF.to_json(orient='records')

def process_request_for_custom_idf(terms):
    query = intercept.Intercept().process_request(terms)
    return query

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__,
                      sort_keys=True, indent=4)


def main(log_level, port, env):
    # TODO add arg parsing and make solr url optional
    #if len(args) < 1:
    #    print('Usage: python app.py <log level> <port> <env>')
    #    sys.exit(1)

    #log_level, port = args
    # ------- start app server
    app.run(debug=True, host='0.0.0.0', port=int(port), use_reloader=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--loglevel", help="Log level",
                        type=str,
                        default="info")
    parser.add_argument("-p", "--port", help="Log level",
                        type=int,
                        default=4004)
    parser.add_argument("-e", "--env", help="Env of the dir",
                        type=str,
                        default="dev")
    args = parser.parse_args()

    main(args.loglevel, args.port, args.env)
