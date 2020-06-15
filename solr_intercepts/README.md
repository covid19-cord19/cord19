# Step by step process to run solution:

## Pre-requisites:
    1. Solr server should be setup and ready to use.
        - Kaggle dataset is downloaded and unzipped to solr VM folder /opt/data/
        - All the code present in repository is chekedout to /opt/code

**1)  Data Ingestion - solr_ingestor.py**
  solr_ingestor.py file is used to ingest and index COVID-19 kaggle dataset to Solr. Use below script to start ingestion process.
  
    python3 /opt/code/COVID19/solr_intercepts/solr_ingestor.py -p /opt/data/document_parses/ -e prod
  
  _Note : This step assumes that kaggle dataset is present in /opt/data/_ 
  
**2) IDF Computation - document_search_engine.py**
  document_search_engine.py file is used to compute the Inverse document frequency for the full corpus.
  
    python3 /opt/code/COVID19/document_search/document_search_engine.py

**3) Start COVID-19 server - app.py**
  app.py file is the starting point for running the API. Below script will start the flask server and expose a REST endpoint POST /search to allow users to search for queries related to COVID-19. Below is the functionality of this API:
  1) Clean data - stop word removal, convert to lowercase, tokenize
  2) Lookup query tokens from IDF dictionary and find IDF values
 for each token.
 3) Search boosted query in Solr - REST API call to Solr interface.
 4) Get results from Solr and create sentence embeddings for results body text and query.
 5) Find similarity score between Query and documents.
 6) Rank documents as per the similarity score.
 
 Here is the script to start the server:
 
    python3 /opt/code/COVID19/app.py
  
**4) Send queries to COVID-19 server**
  Use any tool to send REST API call to Solr Server (Postman etc..). Here is the curl command to be used from command line interface:
  
    curl http://localhost:8080/search --header "Content-Type: application/json" --request POST --data '{
	"task": "What do we know about vaccines and therapeutics? What has been published concerning research and development and evaluation efforts of vaccines and therapeutics?",
	"sub-task": "Effectiveness of drugs being developed and tried to treat COVID-19 patients.Clinical and bench trials to investigate less common viral inhibitors against COVID-19 such as naproxen, clarithromycin, and minocyclinethat that may exert effects on viral replication."
}'
