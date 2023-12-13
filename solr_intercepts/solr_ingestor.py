#!/usr/bin/env python
"""
Program: solr_ingestor.py
Purpose: Used for ingesting documents to solr
Created: Apr 12, 2020
Author:
       - Sharad Varshney                sharad.varshney@gmail.com
       - Jatin Sharma                   jatinsharma7@gmail.com
       - Guruprasad Ahobalarao          gahoba@gmail.com
"""
import os
import argparse
import json
from pathlib import Path
import pysolr

#from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

config = {
    "solr_url" : "http://localhost:8983/solr/covid19",
    "solr_url_dev" : "http://localhost:8983/solr/covid19_dev",
    "solr_url_prod" : "http://localhost:8983/solr/covid19"
}

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


def main(basepath, env):
    print("Path : " + basepath)
    list1 = ["pdf_json", "pmc_json"]
    document_count = 0
    for dir_json in list1:
        pathVar = os.path.join(basepath, dir_json)
        print("Path pathVar : " + pathVar)
        for entry in os.listdir(pathVar) :
            if os.path.isfile(os.path.join(pathVar, entry)):
                print(entry)
                with open(os.path.join(pathVar, entry), "r") as file:
                    doc = json.loads(file.read())
                    actual_body = ""
                    for body in doc["body_text"]:
                        if "text" in body:
                            actual_body = body["text"]
                            actual_body = "".join(actual_body)
                    print(actual_body)
                    abstract = ""
                    title=""
                    paper_id=""
                    if ("abstract" in doc) and (doc["abstract"] is not None and len(doc["abstract"]) > 0):
                        abstract = doc["abstract"][0]["text"]
                    if ("paper_id" in doc) and (doc["paper_id"] is not None):
                        paper_id = doc["paper_id"]
                    if ("title" in doc["metadata"]) and (doc["metadata"]["title"] is not None):
                        title = doc["metadata"]["title"]
                    if ("authors" in doc["metadata"]) and (doc["metadata"]["authors"] is not None):
                        authors = doc["metadata"]["authors"]
                    map1 = {"id": paper_id,
                            "authors": authors,
                            "title": title,
                            "abstract": abstract,
                            "body": actual_body
                            }
                    print(map1)
                    document_count = document_count + 1
                send_for_solr_indexing([map1], env)
    print("Total numner of documents ingested : " , str(document_count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--azure", help="Whether to read from Azure Blob",
                        type=str,
                        choices=["./CORD-19-research-challenge/"],
                        default="./CORD-19-research-challenge/")
    parser.add_argument("-p", "--path", help="Path of the dir",
                        type=str,
                        default="./CORD-19-research-challenge/")
    parser.add_argument("-e", "--env", help="Env of the dir",
                        type=str,
                        default="dev")
    args = parser.parse_args()

    main(args.path, args.env)

