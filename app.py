from flask import Flask, request, jsonify
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np
from classificationClasses.ClothClasses import ClothClasses
app = Flask(__name__)
predictionModel = YOLO(r'C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\clothing_items.pt')
#only one instance of cloth class
clothClasses = ClothClasses()

@app.route("/detect", methods=["POST"])
def detectClothingItem():
    if request.method == 'POST':
        imageInput = request.files["image"]
        imageInput2 = Image.open(BytesIO(imageInput.read()))
        predictionResult = predictionModel(imageInput2)
        inferences = predictionResult[0].boxes.data.numpy()
        val = []
        for inference in inferences:
            val.append(inference[5])
        retirevedClasses = {"results": clothClasses.getClassLabels(val)}
        return jsonify(retirevedClasses)
        
