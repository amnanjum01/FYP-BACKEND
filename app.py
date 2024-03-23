from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np
from numpy.linalg import norm
from classificationClasses.ClothClasses import ClothClasses

#embeddings generator
from imgbeddings import imgbeddings

#imports for the database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db

#fetching service account key content
cred = credentials.Certificate('bagsearch-firebase.json')

#initialize the application
firebase_admin.initialize_app(cred)

#firestore client
db = firestore.client()

#image imbedding object 
ibed = imgbeddings()

app = Flask(__name__)
predictionModel = YOLO(r'C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\clothing_items.pt')

clothClasses = ClothClasses()

@app.route("/detect", methods=["POST"])
def detectClothingItem():
    if request.method == 'POST':
        imageInput = request.files["image"]
        imageInput2 = Image.open(BytesIO(imageInput.read()))
        imageEmbedding = ibed.to_embeddings(imageInput2)
        arr_list = imageEmbedding.tolist() #embedding. To return, type arr = arr_arr_list
        predictionResult = predictionModel(imageInput2)
        inferences = predictionResult[0].boxes.data.numpy()
        val = []
        for inference in inferences:
            val.append(inference[5])
        products_ref = db.collection('products').where('label', 'in', clothClasses.getClassLabels(val)).stream()
        finalResult = []
        for doc in products_ref:
            docDict = doc.to_dict()
            A = np.reshape(np.array(eval(docDict.get("vector"))), (1, 768))
            cosine_similarity =  np.dot(A, imageEmbedding.T) / (np.linalg.norm(A) * np.linalg.norm(imageEmbedding))
            docDict["cosineSimilarity"] = cosine_similarity.tolist()
            finalResult.append(docDict)
        
        finalResultSorted = sorted(finalResult, key= lambda d: d['cosineSimilarity'], reverse=False)
        retrievedClass = {"results": finalResultSorted}
        return jsonify(retrievedClass)
    
@app.route("/testing-db", methods=["GET"])
def getData():
    if request.method == 'GET':
        db = firestore.client()
        cities_ref = db.collection("products")
        docs = cities_ref.stream()
        cities = []
        for doc in docs:
            cities.append({doc.id: doc.to_dict()})
        return jsonify(cities)
    
    
    

# retirevedClasses = {"results": clothClasses.getClassLabels(val)}