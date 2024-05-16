from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_bcrypt import check_password_hash
from project_secrets import MONGODB_ATLAS_URI, JWT_SECRET, EMAIL_PASSWORD, EMAIL
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np
from numpy.linalg import norm
from classificationClasses.ClothClasses import ClothClasses
from classificationClasses.JewelryClasses import JewelryClasses
from classificationClasses.ShoesClasses import ShoesClasses

#date time
from datetime import datetime

#jwt web token for authentication of the app
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

#schemas
from models.products import products
from models.users import users
from models.orders import orders

#embeddings generator
from imgbeddings import imgbeddings

#date parser
from dateutil import parser

#setting up mongo db
from flask_pymongo import PyMongo
from pymongo.errors import CollectionInvalid
from pymongo import DESCENDING

#image imbedding object 
ibed = imgbeddings()

#repititive functions import
from Functions import *

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

#config of jwt token done here
app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400
jwt = JWTManager(app)

#config of db is done here
app.config["MONGO_URI"] = MONGODB_ATLAS_URI
mongo = PyMongo(app) 

#models to be used
clothingModel = YOLO(r'C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\clothes_new.pt')
jewerlyModel = YOLO(r"C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\jewellery_new.pt")
shoeModel = YOLO(r"C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\shoes_new.pt")

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
    
    

@app.route("/products/all-products", methods=["GET"])
def getProducts():
    try:
      if request.method == "GET":
        allProducts = mongo.db.Products.find()
        data = resultsStringIdConverter(allProducts)
        return jsonify(data)
    except Exception as e:
      return jsonify({"message : ", str(e)})
      

@app.route("/products/category/<category_name>", methods = ["GET"])
def getProductByCategory(category_name):
  try:
    if request.method == "GET":
        allProducts = mongo.db.Products.find({"category": category_name})
        data = resultsStringIdConverter(allProducts)
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
            product["_id"] = str(product["_id"])  
            return jsonify(product)
        else:
            return jsonify({"message": "Product not found"}), 404
  except Exception as e:
    return jsonify({"message : ", str(e)})
          
@app.route("/products/label/<label>", methods = ["GET"])
def getProductByLabel(label):
  try:
    if request.method == "GET":
          allProducts = mongo.db.Products.find({"labels": {"$in": [label]}})
          data = resultsStringIdConverter(allProducts)
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
      
@app.route("/products/category-wise-labels/<category>", methods=["GET"])
def getCategoryWiseLabels(category):
  try:
    if request.method == "GET":
      products = mongo.db.Products.find({"category":category})
      labels = []
      for product in products:
        for label in product["labels"]:
          if label not in labels:
            labels.append({"name":label})
      return jsonify({
        "title":category,
        "items": labels
      })
  except Exception as e:
    return jsonify({"Message":str(e)})
  
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

@app.route("/products/detect", methods=["POST"])
def productsDetect():
    try:
      if request.method == 'POST':
        imageInput = request.files["image"]
        imageInput2 = Image.open(BytesIO(imageInput.read()))
        imageEmbedding = ibed.to_embeddings(imageInput2)
        arr_list = imageEmbedding.tolist() 
        predictionResultClothes = clothingModel(imageInput2)
        predictionResultJewelry = jewerlyModel(imageInput2)
        predictionResultShoes = shoeModel(imageInput2)
        inferences = predictionResultShoes[0].boxes.data.numpy()
        inferences1 = predictionResultClothes[0].boxes.data.numpy()
        inferences2 = predictionResultJewelry[0].boxes.data.numpy()
        
        last_elements_within = [int(element[-1]) for element in inferences]
        shoes = ShoesClasses.getClassLabels(last_elements_within)
        
        last_elements_within_clothes = [int(element[-1]) for element in inferences1]
        cloth = ClothClasses.getClassLabels(last_elements_within_clothes)
        
        last_elements_within_jewelry = [int(element[-1]) for element in inferences2]
        jewelry = JewelryClasses.getClassLabels(last_elements_within_jewelry)
        
        totalClasses = jewelry + cloth + shoes
        
        if(len(totalClasses)==0):
          allItems = mongo.db.Products.find()
          data = resultsStringIdConverter(allItems)
          result = [
            {
              "detection": "no detection",
              "products": data["products"]
            } 
          ]
          return jsonify(result)
          
        
        products_ref = mongo.db.Products.find({"labels":{ "$in": shoes}})
        products_list_shoes = cursorConverter(cursor=products_ref)
        finalResultSorted_shoes = embeddingComparerAndSort(imageEmbeddings=imageEmbedding, productList= products_list_shoes)
        
        products_cloth = mongo.db.Products.find({"labels":{ "$in": cloth}})
        products_list_cloth = cursorConverter(cursor=products_cloth)
        finalResultSorted_cloth = embeddingComparerAndSort(imageEmbeddings=imageEmbedding, productList=products_list_cloth)
        
        products_jewelry = mongo.db.Products.find({"labels":{ "$in": jewelry}})
        products_list_jewelry = cursorConverter(cursor=products_jewelry)
        finalResultSorted_jewelry= embeddingComparerAndSort(imageEmbeddings=imageEmbedding, productList=products_list_jewelry)
        
        # print(finalResultSorted_cloth)
        # print(finalResultSorted_jewelry)
        # print(finalResultSorted_shoes)
        
        finalResultSorted = finalResultSorted_cloth + finalResultSorted_jewelry + finalResultSorted_shoes
        data = resultsStringIdConverter(finalResultSorted)
        
        prods = data["products"]
        finalArray = []
        
        for classItem in totalClasses:
          arr = []
          for product in prods:
            if classItem in product["labels"]:
              arr.append(product)
          finalSet = {
            "detection":classItem,
            "products":arr
          }
          finalArray.append(finalSet)
          
        return jsonify({"products":finalArray})
      
    except Exception as e:
      return jsonify({"message : ", str(e)})
      
@app.route("/orders/create-order", methods=["POST"])
def createOrder():
    try:
        if request.method == "POST":
            keys = ["userId", "products", "totalPrice", "orderDate", "status"]
            for key in keys:
                if key not in request.get_json():
                    return jsonify({'message': 'userId, products, totalPrice, orderDate, and status are required'})
            newRecord = request.get_json()
            for record in newRecord["products"]:
              prod = mongo.db.Products.find_one({"sku":record["sku"]})
              quantity = 0
              if "size" in record:
                updated_sizes = []
                for size in prod['sizes']:
                    if size['sizeVal'] == record["size"]:
                      size['quantity'] = size['quantity'] - record["quantity"]
                      quantity = quantity + record["quantity"]
                      updatedProductQuantity = prod["quantity"] - quantity
                    updated_sizes.append(size)
                mongo.db.Products.update_one({'sku': record["sku"]}, {'$set': {'sizes': updated_sizes, "quantity": updatedProductQuantity}})
              else:
                updatedProductQuantityWithoutSize = prod["quantity"]-record["quantity"]
                mongo.db.Products.update_one({'sku': record["sku"]}, {'$set': {"quantity": updatedProductQuantityWithoutSize}})
            order_id = newRecord["userId"] + generate_random_string(4)
            newRecord["orderId"] = order_id
            newRecord["orderDate"]=  parser.isoparse(newRecord["orderDate"])
            print(newRecord["orderDate"])
            mongo.db.Orders.insert_one(newRecord)
            return jsonify({'message': newRecord["orderId"]})
    except Exception as e:
        return jsonify({"error message": str(e)})
      
@app.route("/orders/order-details/<id>", methods = ["GET"])
def getOrderDetails(id):
  try:
    if request.method == "GET":
      order = mongo.db.Orders.find_one({"orderId":id})
      if order:
        order["_id"] = str(order["_id"])  
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
  
@app.route("/users/create-user", methods = ["POST"])
def createUser():
  try:
    if request.method == "POST":
      user = request.get_json()
      keys = ["username", "password", "email", "firstName", "lastName","address", "phoneNumber"]
      for key in keys:
        if key not in request.get_json():
          return jsonify ({"Following key is required":"Key missing."}) 
      addressKeys = ["street", "city", "state", "country", "zip"]
      for addressKey in addressKeys:
        if addressKey not in user["address"]:
          return jsonify({"message":"Following address keys are required: street, city, state, country and zip."})
      user["userId"] = user["username"] + generate_random_string(7)
      user["password"] = bcrypt.generate_password_hash(user["password"], rounds=16).decode('utf-8')
      mongo.db.Users.insert_one(user)
      message = f"User {user['userId']} created"
      return jsonify({"message": message})
  except Exception as e:
    return jsonify({"message : ", str(e)})
  
@app.route("/users/login", methods = ["POST"])
def userLogin():
  try:
    if request.method == "POST":
      user = request.get_json()
      keys = ["email","password"]
      for key in keys:
        if key not in user:
          return jsonify({"message":"Need email and password."})
      exists = mongo.db.Users.find_one({"email":user["email"]})
      if exists is None:
        return jsonify({"message":"Wrong email or password."})
      currPassword = exists["password"].encode('utf-8')
      if bcrypt.check_password_hash(currPassword, user["password"]) == True:
        accessToken = create_access_token(identity=user["email"])
        return jsonify({"message":accessToken})
      else:
        return jsonify({"message":"Wrong password."})
  except Exception as e:
    return jsonify({"message : ", str(e)})
  
@app.route("/users/reset-password/<email>", methods = ["PUT"])
def resetPassword(email):
  try:
    if request.method == "PUT":
      exists = mongo.db.Users.find_one({"email":email})
      if exists is None:
        return jsonify({"message":"User does not exists"})
      else:
        newPassword = request.get_json()
        for key in ["newPassword", "confirmedPassword"]:
          if key not in newPassword:
            return jsonify({"message":"missing new or confirmed password"})
        hashedPassword = bcrypt.generate_password_hash(newPassword["newPassword"], rounds=16)
        if check_password_hash(hashedPassword, newPassword["confirmedPassword"]) != True:
          return jsonify({"Message":"Passwords don't match."})
        hashedPassword = hashedPassword.decode('utf-8')
        mongo.db.Users.find_one_and_update(filter={"email":email}, update={"$set":{"password":hashedPassword}})
        return jsonify({"Message":"Password updated."})
  except Exception as e:
    return jsonify({"Error message : ": str(e)})
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)