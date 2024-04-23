import numpy as np
import random
import string

def embeddingComparerAndSort(imageEmbeddings, productList):
    finalResult = []
    for doc in productList:
        A = np.reshape(np.array(eval(doc["vector"])), (1, 768))
        cosine_similarity =  np.dot(A, imageEmbeddings.T) / (np.linalg.norm(A) * np.linalg.norm(imageEmbeddings))
        doc["cosineSimilarity"] = cosine_similarity.tolist()
        finalResult.append(doc)
    finalResultSorted = sorted(finalResult, key= lambda d: d['cosineSimilarity'], reverse=True)
    return finalResultSorted

def cursorConverter(cursor):
    products_list = []
    for document in cursor:
        products_list.append(document)
    return products_list
        
def resultsStringIdConverter(cursor):
    data = {"products": []}
    for product in cursor:
        product["_id"] = str(product["_id"])  
        if "vector" in product:
            del product["vector"]
        data["products"].append(product)
        
    return data

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))