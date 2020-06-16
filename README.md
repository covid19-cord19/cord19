# Welcome to CORD-19 solution

# Approach

We attempted to solve the CORD-19 research challenge by applying two main techniques - 

 1. Reducing the **search space !**
 2. Surface documents based on **similarity rankings**
 3. Use **Sentence vector embeddings from tensorflow hub**
 4. Complete code at Public Github repository with Apache License v2: https://github.com/covid19-cord19/cord19
 5. Step by step process to run the code can be found at : https://github.com/covid19-cord19/cord19/blob/master/solr_intercepts/README.md

## Reducing search space

Our solution uses a search engine to crawl and ingest all the 138,000 scholarly articles including 68,000 research articles and associated relevant metadata attributes with the document - title, abstract and body. We selected Solr with Lucene indexes as the search engine to help us reduce 138k search space to top 100 documents using tf-idf and idf boosting technique.

### Why Solr?

Solr is an open source search platform, that provides many advanced searching capabilities. We found the following capabilities such as fielded search, Boolean queries, phrase queries, fuzzy queries, spell check, wildcards, joins, and grouping extremely useful for our solution.

Solr follows a 3-step process that involves indexing, querying, and finally, ranking the results – all in near real-time while working with huge volumes of data.

More specifically, here’s how Solr performs the following operations in a sequence to search for a document:

 1. **Indexing** : As the Cord19 files are already in JSON format, we can upload them directly to Solr by calling the index request handler (or simply index handler). 
 
Solr uses Lucene to create an inverted index because it inverts a page-centric data structure (documents ⇒ words) to a keyword-centric structure (word ⇒ documents). It’s like the index you see at the end of any book where you can find where certain words occur in the book. Similarly, the Solr index is a list that holds the mapping of words, terms or phrases and their corresponding places in the documents stored.

Solr uses fields to index a document. However, before being added to the index, data goes through a field analyzer, where Solr uses char filters, tokenizers, and token filters to make data searchable. Char filters can make changes to the string as a whole. Then, tokenizers break field data into lexical units or tokens that then pass through filters which decide to keep, transform (e.g. setting all the data to lowercase, removing word stems) or discard them, or create new ones. These final tokens are added to the index or searched at query time. 

 2. **Querying** : We can search for various terms such as keywords, images or geolocation data, for instance. When you send a query, Solr processes it with a query request handles (or simply query handler) that works similarly to the index handler, only that is used to return documents from the Solr index instead of uploading them.  
 
Data indexed in Solr is organized in fields, which are  defined in the Solr Schema [https://lucene.apache.org/solr/guide/8_5/defining-fields.html#defining-fields](https://lucene.apache.org/solr/guide/8_5/defining-fields.html#defining-fields). Searches can take advantage of fields to add precision to queries. For example, you can search for a term only in a specific field, such as a title field. You can specify a different field or a combination of fields in a query.

Solr provides flexibility to boost and control the relevance of a document by boosting the Term. The higher the boost factor, the more relevant the term will be. To boost a term use the caret symbol ^ with a boost factor (a number) at the end of the term you are searching.

For example, if you are searching for, "Impact of Smoking on COVID" and you want the term "Smoking" to be more relevant, you can boost it by adding the ^ symbol along with the boost factor immediately after the term. you could type.

                                               
![Scoring within Solr using Lucene](https://github.com/covid19-cord19/cord19/blob/master/images/Lucene_scoring.png)

```python
def send_for_solr_indexing(doc, env):
    """
     Sends the text document for indexing
     params:
     doc: text document to be indexed
     env: dev or prod
    """
    if(env):
        solr = pysolr.Solr(config["solr_url"+"_"+env], timeout=10)
    else:
        solr = pysolr.Solr(config["solr_url"], timeout=10)
   
    solr.add(doc)
    solr.optimize()  

```

**Code snippet**
To fine tune Solr search to return right subset of documents, we need to identify the right query terms to boost.  This is done by using term’s inverse document frequency (idf), which decreases the weight for commonly used words and increases the weight for words that are not used very much in a collection of documents.
During the document ingestion process we generate the idf dictionary for the entire document corpus that serves as a look up to identify boost parameter values.


```python
def process_request(self, term):
    """
     Process request for re-computed inverse document frequency so we can boost query terms.
     
     params:
     term: new terms to be added
    """
    self.dictionary = self.load_dictionary("./dictionary", "dictIDF.txt")
    term_weights = {}
    for term in terms:
        try:
            if term in self.dictionary:
                term_weights[term]  = self.dictionary[term]
            else:
                term_weights[term]  = 5.0
        except:
            pass
    solr_query = ' '.join(['{0}:{3}^{4} {1}:{3}^{4} {2}:{3}^{4}'.format("body", "abstract", "title", term, term_weights[term]) for term in terms])
    print(solr_query)
    return solr_query
```

 3. **Ranking the Results** : As it matches indexed documents to a query, Solr ranks the results by their relevance score – the most relevant hits appear at the top of the matched documents


![Custom solution](https://github.com/covid19-cord19/cord19/blob/master/images/covid19_2.png)


  
## Sentence vector embeddings from tensorflow hub

Semantic similarity is a measure of the degree to which two pieces of text carry the same meaning. This is broadly useful in obtaining good coverage over the numerous ways that a thought can be expressed using language without needing to manually enumerate them.

![Sentence Semantic Similarity](https://github.com/covid19-cord19/cord19/blob/master/images/sentence_embedding.png)

We use Tensorflow hub module for universal-sentence-encoder, The Universal Sentence Encoder encodes text into high-dimensional vectors that can be used for text classification, semantic similarity, clustering and other natural language tasks.The model is trained and optimized for greater-than-word length text, such as sentences, phrases or short paragraphs. It is trained on a variety of data sources and a variety of tasks with the aim of dynamically accommodating a wide variety of natural language understanding tasks. The input is variable length English text and the output is a 512 dimensional vector.

One of the example use case:

```python
import tensorflow_hub as hub

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/3")
embeddings = embed([
    "The quick brown fox jumps over the lazy dog.",
    "I am a sentence for which I would like to get its embedding"])["outputs"]

print(embeddings)

# The following are example embedding output of 512 dimensions per sentence
# Embedding for: The quick brown fox jumps over the lazy dog.
# [-0.03133016 -0.06338634 -0.01607501, ...]
# Embedding for: I am a sentence for which I would like to get its embedding.
# [0.05080863 -0.0165243   0.01573782, ...]

```
Typical model pipeline for sentence-encoder in google based flow looks like: 

![Sentence Semantic Similarity solution](https://github.com/covid19-cord19/cord19/blob/master/images/Tf-hub_sentence_semantic_similarity.png)

## Document similarity 

Document similarity (or distance between documents) is a one of the central themes in Information Retrieval. How humans usually define how similar are documents? Usually documents treated as similar if they are semantically close and describe similar concepts. 
Classical approach from computational linguistics is to measure similarity based on the content overlap between documents. For this we will represent documents as sentence embeddings (vectors) , so each document will be a sparse vector. And define measure of overlap as angle between vectors

Similarity (doc1, doc2) = Cos(θ) = (doc1 . doc2) / (||doc1|| . ||doc2||)

	Where doc1 and doc2 are task and document embedding vectors

The resulting similarity ranges from −1 meaning exactly opposite, to 1 meaning exactly the same, with 0 indicating orthogonality or decorrelation, while in-between values indicate intermediate similarity or dissimilarity.

![Cosine Similarity](https://github.com/covid19-cord19/cord19/blob/master/images/cosine_similarity.png)

Subset of documents (result from Solr search) is used to similarity check and rank them in descending order of similarity score

```python

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

```


