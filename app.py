from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
from ultralytics import YOLO


app = Flask(__name__)
predictionModel = YOLO(r'C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\clothing_items.pt')

@app.route("/detect", methods=["POST"])
def detect_clothing_item():
    if request.method == 'POST':
        imageInput = request.files["image"]
        imageInput2 = Image.open(BytesIO(imageInput.read()))
        prediction = predictionModel(imageInput2)
        finalOutput = {"result": prediction[0].boxes.data}
        print(finalOutput)
        return "Hello!"
        
