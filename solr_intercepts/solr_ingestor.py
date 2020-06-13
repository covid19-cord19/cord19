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

#def get_blob_client():
    # Create the BlobServiceClient object which will be used to create a container client
#    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#    container_name = config["container_name"]
#    local_file_name = "datafiles"
    # Create a blob client using the local file name as the name for the blob
#    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
#    return blob_client

#def get_files_from_blob():
#    connect_str = config['AZURE_STORAGE_CONNECTION_STRING']
#    container_client = ContainerClient.from_connection_string(connect_str, container_name="data")

    # List the blobs in the container
#    blob_list = container_client.list_blobs()
#    for blob in blob_list:
#        print("\t" + blob.name)
#        print(blob)
        # print(data)

def send_for_solr_indexing(doc, env):
    # post to solr for indexing
    if(env):
        solr = pysolr.Solr(config["solr_url"+"_"+env], timeout=10)
    else:
        solr = pysolr.Solr(config["solr_url"], timeout=10)
    # How you'd index data.
    solr.add(doc)

    # You can optimize the index when it gets fragmented, for better speed.
    solr.optimize()  # Optimize also do commit 'solr/clst5/update/?commit=true' (post) with body '<optimize '


'''
def solr_indexing_optimization():
    # post to solr for indexing
    solr = pysolr.Solr(config["solr_url"], timeout=10)
    # You can optimize the index when it gets fragmented, for better speed.
    solr.optimize()  # Optimize also do commit 'solr/clst5/update/?commit=true' (post) with body '<optimize '
    '''




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


def main_old(basepath, env):
    print("Path : " + basepath)
    for entry in os.listdir(basepath):
        if os.path.isdir(os.path.join(basepath, entry)):
            #pathVar = os.path.join(basepath, entry) + "/pdf_json"
            pathVar = os.path.join(basepath, entry)+ "/" + entry
            for entry in os.listdir(pathVar):
                if os.path.isfile(os.path.join(pathVar, entry)):
                    print(entry)
                    with open(os.path.join(pathVar, entry), "r") as file:
                        doc = json.loads(file.read())
                        actual_body = ""
                        for body in doc["body_text"]:
                            actual_body = body["text"]
                            actual_body = "".join(actual_body)
                        print(actual_body)
                        abstract = ""
                        if doc["abstract"] is not None:
                            if len(doc["abstract"]) > 0:
                                abstract = doc["abstract"][0]["text"]
                        map1 = {"id": doc["paper_id"],
                                "title": doc["metadata"]["title"],
                                "abstract": abstract,
                                "body": actual_body
                                }
                        print(map1)
                    send_for_solr_indexing([map1], env)

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

