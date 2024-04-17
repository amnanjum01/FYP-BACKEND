from flask import Flask, request, jsonify
from project_secrets import MONGODB_ATLAS_URI
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np
from numpy.linalg import norm
from classificationClasses.ClothClasses import ClothClasses
from classificationClasses.JewelryClasses import JewelryClasses
from classificationClasses.ShoesClasses import ShoesClasses
import random
import string

#date time
from datetime import datetime
from bson import ObjectId
from bson import json_util

#schemas
from models.products import products
from models.users import users
from models.orders import orders

#embeddings generator
from imgbeddings import imgbeddings

#setting up mongo db
from flask_pymongo import PyMongo
from pymongo.errors import CollectionInvalid
from pymongo import DESCENDING

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

#config of db is done here
app.config["MONGO_URI"] = MONGODB_ATLAS_URI
mongo = PyMongo(app) 

#models to be used
clothingModel = YOLO(r'C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\clothing_items.pt')
jewerlyModel = YOLO(r"C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\jewelry.pt")
shoeModel = YOLO(r"C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\shoes_items.pt")

#instances of the model
clothClasses = ClothClasses()
jewelryClasses = JewelryClasses()
shoeClasses = ShoesClasses()

#check existence of the products collection
collection_name = 'Products'
if collection_name not in mongo.db.list_collection_names():
    mongo.db.create_collection(collection_name, validator=products)
else:
    print(f"Collection '{collection_name}' already exists.")
    
#check existence of the products collection
collection_name = 'Users'
if collection_name not in mongo.db.list_collection_names():
    mongo.db.create_collection(collection_name, validator=users)
else:
    print(f"Collection '{collection_name}' already exists.")

#check existence of the products collection
collection_name = 'Orders'
if collection_name not in mongo.db.list_collection_names():
    mongo.db.create_collection(collection_name, validator=orders)
else:
    print(f"Collection '{collection_name}' already exists.")
    


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))
    
@app.route("/detect", methods=["POST"])
def detectClothingItem():
    if request.method == 'POST':
        imageInput = request.files["image"]
        imageInput2 = Image.open(BytesIO(imageInput.read()))
        imageEmbedding = ibed.to_embeddings(imageInput2)
        arr_list = imageEmbedding.tolist() #embedding. To return, type arr = arr_arr_list
        predictionResultClothes = clothingModel(imageInput2)
        predictionResultJewelry = jewerlyModel(imageInput2)
        predictionResultShoes = shoeClasses(imageInput2)
        inferences = predictionResultJewelry[0].boxes.data.numpy()
        print(inferences)
        inferences1 = predictionResultClothes[0].boxes.data.numpy()
        print(inferences1)
        inferences2 = predictionResultShoes[0].boxes.data.numpy()
        print(inferences2)
        val = []
        for inference in inferences:
            val.append(inference[5])
        products_ref = db.collection('products').where('label', 'in', jewelryClasses.getClassLabels(val)).stream()
        finalResult = []
        for doc in products_ref:
            docDict = doc.to_dict()
            A = np.reshape(np.array(eval(docDict.get("vector"))), (1, 768))
            cosine_similarity =  np.dot(A, imageEmbedding.T) / (np.linalg.norm(A) * np.linalg.norm(imageEmbedding))
            docDict["cosineSimilarity"] = cosine_similarity.tolist()
            finalResult.append(docDict)
        finalResultSorted = sorted(finalResult, key= lambda d: d['cosineSimilarity'], reverse=True)  # Sort in descending order of cosine similarity
        retrievedClass = {"hello": finalResultSorted, "hi": inferences1}
        return jsonify(retrievedClass)

@app.route("/connectmongo", methods=["GET"])
def getMongoData():
    try:
      if request.method == 'GET':
        mongo.db.Product.insert_one({"a": ']'})
        data = {"message":"Data Fetched Successfully"}
        return jsonify(data)
    except Exception as e:
      return jsonify({"message : ", str(e)})

@app.route("/products/all-products", methods=["GET"])
def getProducts():
    try:
      if request.method == "GET":
        allProducts = mongo.db.Product.find()
        data = {"products": []}
        for product in allProducts:
            product["_id"] = str(product["_id"])  # Convert ObjectId to string
            data["products"].append(product)
        return jsonify(data)
    except Exception as e:
      return jsonify({"message : ", str(e)})
      

@app.route("/products/category/<category_name>", methods = ["GET"])
def getProductByCategory(category_name):
  try:
    if request.method == "GET":
        allProducts = mongo.db.Products.find({"category": category_name})
        data = {"products": []}
        for product in allProducts:
            product["_id"] = str(product["_id"])  # Convert ObjectId to string
            data["products"].append(product)
        return jsonify(data)
  except Exception as e:
      return jsonify({"message : ", str(e)})
    

@app.route("/products/delete/<id>", methods = ["DELETE"])
def deleteProductById(id):
  try:
    if request.method == "DELETE":
          mongo.db.Products.delete_one({"sku": id})
          data = {"products": "successfully deleted"}
          return jsonify(data)
  except Exception as e:
    return jsonify({"message : ", str(e)})

@app.route("/products/find-product/<id>", methods = ["GET"])
def getProductById(id):
  try:
    if request.method == "GET":
        product = mongo.db.Products.find_one({"sku": id})
        if product:
            product["_id"] = str(product["_id"])  # Convert ObjectId to string
            return jsonify(product)
        else:
            return jsonify({"message": "Product not found"}), 404
  except Exception as e:
    return jsonify({"message : ", str(e)})
          
@app.route("/products/label/<label>", methods = ["GET"])
def getProductByLabel(label):
  try:
    if request.method == "GET":
          allProducts = mongo.db.Products.find({"labels":label})
          data = {"products": []}
          for product in allProducts:
              product["_id"] = str(product["_id"])  # Convert ObjectId to string
              data["products"].append(product)
          return jsonify(data)
  except Exception as e:
    return jsonify({"message : ", str(e)})

@app.route("/products/add-new-product", methods = ["POST"])
def addNewProduct():
  try:
    if request.method == "POST":
        req_data = request.get_json()
        mongo.db.Products.insert_one(req_data)
        return jsonify({"Message":"Data successfully added"})
  except Exception as e:
    return jsonify({"message : ", str(e)})
      
@app.route("/products/update-product/<id>", methods = ["PUT"])
def updateProductById(id):
  try:
    if request.method == "PUT":
          update_data = request.get_json()
          mongo.db.Products.find_one_and_update({"sku":id}, {'$set': update_data}, return_document=True)
          return jsonify({"Message":"product updated"})
  except Exception as e:
    return jsonify({"message : ", str(e)})
      
@app.route("/products/like/<id>", methods = ["PUT"])
def likeById(id):
  try:
    if request.method == "PUT":
          mongo.db.Products.find_one_and_update({"sku":id}, {'$set': {"likes":+1}}, return_document=True)
          return jsonify({"Message":"product updated"})
  except Exception as e:
    return jsonify({"message : ", str(e)})

@app.route("/products/unlike/<id>", methods = ["PUT"])
def unlikeById(id):
  try:
    if request.method == "PUT":
          mongo.db.Products.find_one_and_update({"sku":id}, {'$inc': {"likes":-1}}, return_document=True)
          return jsonify({"Message":"product updated"})
  except Exception as e:
    return jsonify({"message : ", str(e)})
      
@app.route("/products/product-rating/<id>", methods = ["GET"])
def getRatingById(id):
  try:
    if request.method == "GET":
          product = mongo.db.Products.find_one({"sku":id})
          count = 0
          rating = 0
          for review in product["reviews"]:
            rating += review["rating"]
            count += 1
          averageRating = rating/count
          return jsonify({"message":averageRating})
  except Exception as e:
    return jsonify({"message : ", str(e)})

@app.route("/products/review-rate/<id>", methods = ["PUT"])
def rateProduct(id):
  try:
    if request.method == "PUT":
      update_operation = {'$push':{'reviews':request.get_json()}}
      mongo.db.Products.find_one_and_update({'sku':id}, update_operation)
      return jsonify({"message":"Comment added!"})
  except Exception as e:
    return jsonify({'message :', str(e)})
      
@app.route("/orders/create-order", methods=["POST"])
def createOrder():
    try:
        if request.method == "POST":
            keys = ["userId", "products", "totalPrice", "orderDate", "status"]
            for key in keys:
                if key in request.get_json():
                    continue
                else:
                    return jsonify({'message': 'userId, products, totalPrice, orderDate, and status are required'})
            newRecord = request.get_json()
            order_id = newRecord["userId"] + generate_random_string(4)
            newRecord["orderId"] = order_id
            presentDate = newRecord["orderDate"].split('-')
            newRecord["orderDate"] = datetime(int(presentDate[0]), int(presentDate[1]), int(presentDate[2]))
            mongo.db.Orders.insert_one(newRecord)
            return jsonify({'message': order_id})
    except Exception as e:
        return jsonify({"message": str(e)})
      
@app.route("/orders/order-details/<id>", methods = ["GET"])
def getOrderDetails(id):
  try:
    if request.method == "GET":
      order = mongo.db.Orders.find_one({"orderId":id})
      if order:
        order["_id"] = str(order["_id"])  # Convert ObjectId to string
        return jsonify(order)
      else:
        return jsonify({"message": "Product not found"}), 404
  except Exception as e:
    return jsonify({"message": str(e)})

@app.route("/orders/delete-order/<id>", methods=["DELETE"])
def deleteOrder(id):
  try:
    if request.method == ["DELETE"]:
      mongo.db.Orders.find_one_and_delete({'orderId':id})
      return jsonify({"message":"deleted order"})
  except Exception as e:
    return jsonify({"message": str(e)})
  
@app.route("/orders/cancel-order/<id>", methods = ["PUT"])
def cancelOrder(id):
  try:
    if request.method == ["PUT"]:
      order = mongo.db.Orders.find_one({"orderId": id})
      if order["status"] in ["received", "dispatched"]:
        mongo.db.Orders.find_one_and_update({"orderId":id}, {'$set':{"status":"cancelled"}})
      else:
        return jsonify({"message":"Order cannot be cancelled."})
  except Exception as e:
    return jsonify({"message":str(e)})

@app.route("/orders/dispatch-order/<id>", methods=["PUT"])
def dispatchOrder(id):
  try:
    if request.method == ["PUT"]:
      order = mongo.db.Orders.find_one({"orderId":id})
      if order["status"] == "received":
        mongo.db.Orders.find_one_and_update({"orderId":id}, {"$set":{"status":"dispatched"}})
      else:
        return jsonify({"message":"Order cannot be dispatched right now."})
  except Exception as e:
    return jsonify({"message":str(e)})
  
@app.route("/orders/mark-delivered/<id>", methods = ["PUT"])
def markDelivered(id):
  try:
    if request.method == ["PUT"]:
      order = mongo.db.Orders.find_one({"orderId":id})
      if order["status"] == "dispatched":
        mongo.db.Orders.find_one_and_update({"orderId":id}, {"$set":{"status":"delivered"}})
      else:
        return jsonify({"message":"Cannot be delivered yet. Check present status."})
  except Exception as e:
    return jsonify({"message : ", str(e)})
#received,(received) dispatched, (received and dispatch = cancelled) , (dispatched) delivered