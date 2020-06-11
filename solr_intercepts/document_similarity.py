import tensorflow_hub as hub
import pandas as pd
import json
import tensorflow as tf
tf.disable_v2_behavior()
from sklearn.metrics.pairwise import cosine_similarity

# init
init = tf.global_variables_initializer()
init2 = tf.tables_initializer()


class Document_Similarity:

    def __init__(self):
        self.module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/3"

    def getDescription(self,jsonInput):
        description = ""
        if (jsonInput is not None):
            jsonInput = json.loads(jsonInput)
            data = pd.DataFrame(jsonInput['raw_response']['response']['docs'])
            # filteredDF = data.loc[:,["paperid", "body"]]
        else:
            return ("")
        return (data)

    def getEmbeddings(self,session, messages):
        # Import the Universal Sentence Encoder's TF Hub module
        embed = hub.Module(self.module_url)
        message_embeddings = session.run(embed(messages))
        return message_embeddings

    def getSimilarityRanking(self, query, documents):
        print("Query  == ",query)
        documentDF = self.getDescription(documents)
        messages_docs = list(documentDF['body'])

        with tf.Session() as session:
            session.run([tf.global_variables_initializer(), tf.tables_initializer()])
            embed = hub.Module(self.module_url)
            taskEmbeddings = session.run(embed([query]))
            docsEmbeddings = session.run(embed(messages_docs))
            #taskEmbeddings = self.getEmbeddings(session, [query])
            #docsEmbeddings = self.getEmbeddings(session, messages_docs)

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
        return documentDF
