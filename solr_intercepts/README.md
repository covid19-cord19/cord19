# Step by step process to run the solution:

## Pre-requisites:
    1. Solr server should be setup and ready for use.  Ensure the following directories are setup as outlined below
        - /opt/data - This folder should have the Kaggle dataset downloaded and unzipped.
        - /opt/code - This folder should have all the application code.

**1)  Data Ingestion - solr_ingestor.py**<br/>
  Use this file to ingest and index COVID-19 kaggle dataset to Solr. Below script will start the ingestion process.
  
    python3 /opt/code/COVID19/solr_intercepts/solr_ingestor.py -p /opt/data/document_parses/ -e prod
  
  
**2) IDF Computation - document_search_engine.py**<br/>
  Use this file to compute the Inverse document frequency (IDF) for the full document corpus.
  
    python3 /opt/code/COVID19/document_search/document_search_engine.py
    
  _Note: IDF dictionary is already generated and is available as part of the code repository. If IDF dictionary is to be calculated for some other dataset that this file should be used to regenerate IDF dictionary and save it at /opt/code/COVID19/dictionary/

**3) Start COVID-19 server - app.py**<br/>
  This file is the starting point for running the API. Below script will start the flask server and expose a REST endpoint POST /search to allow users to search for queries related to COVID-19. This API will:
  1) Clean data - Parse the input search string to remove stop words, convert to lowercase and tokenize
  2) For the tokens, perform IDF dictionary Lookups to retrieve IDF values and generate Solr search query with appropriate Boost parameters
  3) Call Solr REST API interface to perform document search operation.
  4) Get results from Solr and generate sentence embeddings .
  5) Find similarity score between Query and documents.
  6) Rank documents as per the similarity score.
 
 Here is the script to start the server:
 
    python3 /opt/code/COVID19/app.py
  
**4) How to Send queries to COVID-19 server**
  Use any tool to send REST API call to Solr Server (Postman etc..). Here is the curl command to be used from command line interface:
  
    curl http://localhost:8080/search --header "Content-Type: application/json" --request POST --data '{
	"task": "What do we know about vaccines and therapeutics? What has been published concerning research and development and evaluation efforts of vaccines and therapeutics?",
	"sub-task": "Effectiveness of drugs being developed and tried to treat COVID-19 patients.Clinical and bench trials to investigate less common viral inhibitors against COVID-19 such as naproxen, clarithromycin, and minocyclinethat that may exert effects on viral replication."
}'
