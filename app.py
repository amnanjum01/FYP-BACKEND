from flask import Flask, request, jsonify
from project_secrets import MONGODB_ATLAS_URI
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np
from numpy.linalg import norm
from classificationClasses.ClothClasses import ClothClasses
from classificationClasses.JewelryClasses import JewelryClasses

#embeddings generator
from imgbeddings import imgbeddings

#setting up mongo db
from flask_pymongo import PyMongo

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
jewerlyModel = YOLO(r"C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\jewelry_items.pt")
shoeModel = YOLO(r"C:\Users\Ammna\Documents\GitHub\FYP-BACKEND\weights\shoes_items.pt")

#instances of the model
clothClasses = ClothClasses()
jewelryClasses = JewelryClasses()

@app.route("/detect", methods=["POST"])
def detectClothingItem():
    if request.method == 'POST':
        imageInput = request.files["image"]
        imageInput2 = Image.open(BytesIO(imageInput.read()))
        imageEmbedding = ibed.to_embeddings(imageInput2)
        arr_list = imageEmbedding.tolist() #embedding. To return, type arr = arr_arr_list
        predictionResultClothes = clothingModel(imageInput2)
        predictionResultJewelry = jewerlyModel(imageInput2)
        inferences = predictionResultJewelry[0].boxes.data.numpy()
        inferences1 = predictionResultClothes[0].boxes.data.numpy()
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
    

@app.route("/connectmongo", methods=["GET"])
def getMongoData():
    if request.method == 'GET':
        mongo.db.Product.insert_one({"a": '[ 1.20634639e+00,  3.24711651e-01, -2.71215677e-01, -8.88692856e-01,         5.88664591e-01,  7.00535551e-02,  2.94992715e-01, -7.16695487e-01,         7.87211716e-01, -1.07372975e+00,  5.33935316e-02,  2.95828134e-01,         2.07668304e-01,  1.28030288e+00,  8.19146708e-02,  4.77856278e-01,        -2.16960382e+00, -1.51779675e+00, -5.35801411e-01,  3.13803792e-01,        -2.30610743e-02,  6.49006724e-01, -4.38973531e-02, -2.68130571e-01,        -1.37652561e-01, -7.78390840e-02, -3.87670577e-01,  1.09186125e+00,        -5.69419265e-01,  2.35195780e+00, -9.84662056e-01,  3.67468089e-01,        -4.19383198e-01,  1.78790426e+00,  2.06221655e-01, -3.47951889e-01,         5.17513081e-02,  7.57908642e-01,  2.34209597e-01,  1.67877879e-02,         1.05219567e+00,  5.57137802e-02,  1.37070227e+00,  9.32048798e-01,        -1.24767733e+00,  1.24162145e-01, -2.12485328e-01, -5.19551396e-01,         1.07698607e+00,  1.72373593e+00, -5.84535694e+00, -3.60470206e-01,         7.65836179e-01, -8.32243443e-01, -3.12243283e-01,  1.87565655e-01,         1.85326815e-01,  6.07520461e-01,  3.14505100e-01,  5.29428482e-01,        -4.26001251e-01, -2.16830105e-01,  3.89587164e-01,  1.07781601e+00,        -7.76188433e-01, -6.85445309e-01, -1.88963556e+00,  8.99802506e-01,         6.59702241e-01,  4.73138571e-01,  3.01136345e-01,  8.48859772e-02,         3.51155698e-01, -3.32226247e-01,  1.36211920e+00,  3.62823516e-01,        -3.94046932e-01, -3.58573645e-01, -5.71085095e-01,  5.05171597e-01,         7.22073838e-02,  7.38841653e-01,  5.75284138e-02, -1.17421821e-01,        -3.46094370e-01, -1.06621891e-01,  1.84172392e-01,  9.11578178e-01,        -2.92314112e-01,  3.00465465e-01,  4.52290595e-01,  5.21633625e-01,        -7.96281248e-02,  4.27133590e-01, -3.83519679e-01,  1.19052482e+00,        -6.55120239e-02,  3.43088984e-01,  1.16992581e+00, -2.82163531e-01,         2.24775337e-02, -1.89158130e+00,  5.06694317e-01, -5.91813624e-02,         1.04354310e+00, -2.71922916e-01, -4.22533751e-02,  9.11230206e-01,        -9.13483918e-01,  3.92265826e-01, -3.44431281e-01,  1.60721675e-01,        -6.07059151e-02,  3.06937061e-02, -2.25317001e-01, -5.72980523e-01,         1.81504697e-01,  2.41658235e+00, -9.08682644e-02,  7.95290887e-01,        -4.02500391e-01,  6.08301818e-01, -6.63239211e-02, -8.54647756e-01,        -2.03265762e+00,  5.49895108e-01,  6.83966815e-01,  1.13932490e+00,        -1.16240129e+01, -4.95403588e-01, -1.62974492e-01,  8.33271682e-01,        -7.70099983e-02, -6.90909386e-01,  4.06485908e-02,  3.37926060e-01,        -3.94643992e-01,  1.50481686e-01,  6.71655774e-01,  6.17787302e-01,        -6.84585690e-01,  3.85364503e-01,  1.95369899e+00,  1.65155977e-01,         2.35446021e-01, -4.33428198e-01,  2.69477576e-01,  9.86020088e-01,         9.61057842e-01,  5.77702463e-01, -9.47365165e-01, -4.37880456e-01,        -1.07472260e-02,  1.14295006e+00,  9.47030067e-01, -2.70037055e-01,         2.70953894e-01, -7.59959102e-01, -6.31568313e-01,  9.71319620e-03,         6.04742467e-01,  1.21313834e+00, -1.09928846e+00, -1.90401480e-01,        -2.99908280e-01, -2.75049955e-01,  7.33788788e-01, -3.47557753e-01,         2.43644901e-02, -3.86615209e-02, -2.45063007e-02, -8.66256833e-01,         2.57546715e-02,  5.25060058e-01,  2.01710254e-01, -8.57701525e-02,         1.05302775e+00,  9.14473981e-02,  6.71179950e-01, -9.18904617e-02,         6.56990260e-02,  4.09035310e-02,  4.56941962e-01, -3.41935247e-01,        -1.38867974e+00, -3.74875665e+00, -3.60937268e-01, -2.32573584e-01,         3.39208037e-01, -1.78996757e-01,  3.81190389e-01,  1.99740052e-01,        -8.52172077e-01, -4.55172267e-04, -1.03913158e-01, -1.49379456e+00,         3.17351848e-01, -1.43189514e+00, -1.31249502e-01, -1.34054795e-01,        -7.41347134e-01, -2.00603306e-01, -6.59605980e-01,  1.33740798e-01,        -7.49600351e-01,  5.82205117e-01,  7.77541816e-01,  1.90540278e+00,        -7.87785947e-01, -1.87379196e-01,  1.25606334e+00,  2.18380801e-02,        -1.44647092e-01, -5.99933326e-01, -5.99187911e-01,  1.12871043e-02,         6.68214083e-01,  5.34752309e-02,  4.93712068e-01, -8.36698487e-02,         6.99735165e-01, -4.08210963e-01,  6.61494637e+00,  1.99499607e-01,        -1.05545914e+00,  1.43457651e-01,  4.91611302e-01,  1.45742929e+00,        -1.40318239e+00,  2.20313862e-01,  7.84245133e-01,  7.31247544e-01,        -7.77752757e-01,  5.97451814e-02, -8.65917187e-03,  4.04879272e-01,         5.20192266e-01, -2.52753943e-01, -7.68484697e-02,  3.52015942e-02,        -6.75050914e-01, -3.60534817e-01,  8.11544538e-01,  1.24783170e+00,         4.53219295e-01,  1.15218246e+00,  1.12007773e+00, -9.60902810e-01,         2.23966584e-01, -1.15089059e+00, -8.82726461e-02, -1.25148930e-02,        -6.62920654e-01, -3.52754891e-01, -2.41573706e-01,  7.71455467e-01,         3.01742822e-01,  6.39207661e-01,  1.17688394e+00, -3.43676269e-01,        -1.68559119e-01,  7.55865812e-01, -1.70646393e+00,  4.56406325e-01,         4.88885403e-01,  5.14490604e-01, -2.89174497e-01,  2.43219167e-01,        -1.34296110e-02,  1.15611672e+00, -1.26474321e+00,  5.97710133e-01,         7.94260025e-01, -6.25682473e-01,  7.48999715e-01,  4.30837661e-01,         4.96178925e-01,  5.84646761e-01,  9.99245867e-02, -7.68882930e-01,         1.28519628e-02,  4.41533238e-01, -1.27792716e-01,  2.32548594e-01,         2.47263521e-01, -4.86802310e-01,  7.65000701e-01, -2.21889481e-01,         2.58269966e-01,  1.14973128e-01, -1.66065609e+00, -1.47601593e+00,         3.34077805e-01,  5.12915730e-01, -6.61701381e-01, -5.82623720e-01,         1.03144801e+00,  1.40018016e-01, -2.91702021e-02, -5.93011454e-02,         6.60181582e-01, -1.04589808e+00, -1.89337924e-01, -4.44751620e-01,        -6.44139171e-01,  1.46940792e+00,  1.26439822e+00,  1.79308861e-01,         8.37669428e-03,  2.70550585e+00,  1.21695297e-02,  6.34234369e-01,        -1.83133051e-01,  8.72591972e-01, -4.88203391e-02,  3.92536014e-01,        -2.52777427e-01,  1.09095657e+00,  1.46884128e-01, -7.90174365e-01,         4.36344475e-01,  9.80062306e-01, -6.02355719e-01, -1.00896728e+00,         3.92359525e-01, -5.86300381e-02, -3.27861428e-01, -2.48501584e-01,        -1.17886353e+00, -8.35274518e-01, -6.84785187e-01, -4.70867485e-01,         8.08456242e-01,  5.71071327e-01, -1.96322113e-01,  3.63536000e-01,         1.38451123e+00,  3.20808440e-02,  4.52382773e-01,  1.48010838e+00,        -4.08768594e-01,  1.78794205e+00,  1.79712489e-01,  1.07712126e+00,         1.38296866e+00, -9.19542372e-01, -8.12519670e-01, -7.51675189e-01,         1.01227748e+00,  1.48860157e-01,  3.56167734e-01, -5.99186838e-01,        -1.51126397e+00, -1.61516935e-01, -1.15279865e+00, -7.60676026e-01,         1.44477233e-01, -5.34254670e-01,  1.13233817e+00,  2.52066255e-01,         9.25560176e-01, -4.82715786e-01,  7.59734511e-01,  3.75317246e-01,         3.46364647e-01,  1.09286344e+00, -5.55770338e-01, -4.31670338e-01,         2.20886141e-01,  6.68595359e-03, -2.37252831e-01,  6.58310354e-01,         6.32766113e-02,  1.49873123e-01, -4.06234890e-01,  7.75070846e-01,        -2.08715238e-02,  3.21765989e-01, -3.61074537e-01,  6.27554178e-01,        -8.62305224e-01, -1.50335491e+00,  6.39199913e-01, -3.64610314e-01,         1.08748639e+00,  1.08647597e+00,  1.10903673e-01,  5.07817924e-01,         6.45886138e-02,  7.43729293e-01,  4.32413444e-02,  8.16922367e-01,        -6.00015409e-02,  1.52096212e-01,  8.42092872e-01,  7.09107071e-02,         6.88285887e-01, -1.54252374e+00,  4.38549519e-02,  9.97247640e-03,         1.65978670e-01, -1.77091032e-01,  1.16626687e-01,  8.20340693e-01,         1.27551496e+00, -2.76585072e-01, -7.98970699e-01, -2.02393591e-01,         7.81054795e-01,  1.67720687e+00, -1.85636187e+00, -9.89068970e-02,        -8.68697643e-01,  7.67239928e-01,  1.16009104e+00, -2.22404599e-01,         4.90983456e-01, -7.42794037e-01,  9.42374051e-01,  6.36893809e-01,        -6.67717159e-01,  4.66651529e-01, -7.58353949e-01,  7.69616246e-01,         1.75129205e-01,  1.48840773e+00, -6.96920753e-01,  7.06817508e-01,         4.07034159e-01,  1.48064613e-01,  1.19077325e+00, -2.96004891e-01,        -3.48537385e-01, -9.10467088e-01, -9.76442635e-01,  9.05852616e-01,         2.70411462e-01,  3.05456787e-01,  2.68306732e-01, -6.10668898e-01,         7.36073434e-01,  1.95684701e-01, -2.22309548e-02, -4.31245208e-01,         3.14078201e-03,  1.05334175e+00,  1.44472325e+00, -8.80964339e-01,        -5.77436447e-01,  7.52107203e-01, -1.98670924e-01,  4.93845701e-01,         2.33968824e-01, -3.50425035e-01, -5.64307034e-01,  1.49171576e-01,         8.46719921e-01,  1.20960426e+00,  7.36233771e-01,  1.46151042e+00,         1.34580803e+00,  3.26084197e-01,  5.14563322e-01, -7.29209110e-02,         2.08404675e-01, -4.58639860e-03,  2.09487230e-01, -3.32510442e-01,         2.79641956e-01, -1.53645873e-01,  5.71860492e-01, -1.45976365e+00,        -2.16997396e-02,  1.02386761e+00, -3.66589785e-01,  7.87331879e-01,         2.07968011e-01,  1.51144430e-01,  1.04579711e+00,  4.85546380e-01,         3.62928838e-01,  2.75115818e-01, -6.01550415e-02,  5.30255198e-01,         2.43901491e-01,  2.28523791e-01,  3.59175473e-01, -6.73620582e-01,        -6.04169130e-01,  1.73060477e-01,  2.51076281e-01,  1.30886233e+00,         2.88386464e-01,  8.49266723e-02, -1.69523507e-02,  4.41433370e-01,         2.89505124e-01, -1.45782948e+00,  1.10754168e+00,  9.63767588e-01,         2.99850583e-01,  2.03989342e-01,  1.31180906e+00,  8.05363297e-01,         1.51431227e+00, -7.37825537e+00, -6.07912183e-01, -5.40781438e-01,         6.13669515e-01, -5.41147813e-02, -1.64837971e-01,  4.29590225e-01,         6.47950545e-02,  6.93084955e-01,  2.07934566e-02,  6.86936319e-01,        -1.02401257e+00,  8.79435420e-01,  3.62735182e-01, -1.04810750e+00,         7.29263067e-01,  4.31133248e-02, -8.98472369e-01,  1.02371311e+00,         2.88267493e-01,  9.90308762e-01,  3.66382331e-01,  8.94406065e-02,         2.20231581e+00,  1.52724916e-02,  6.32061124e-01,  1.98939011e-01,         9.31998014e-01, -6.19641662e-01,  9.32620525e-01,  5.18896878e-01,        -7.31879711e-01,  1.79188792e-02, -3.99685204e-01,  1.00037849e+00,        -1.74614917e-02, -9.86541510e-01, -2.06719805e-03,  1.03587389e+00,         5.58225095e-01, -1.83526427e-01, -5.06480411e-02,  2.10980430e-01,         2.64261007e-01,  7.84077048e-01,  2.29955465e-01,  6.29817247e-01,        -5.29552221e-01,  5.75707197e-01,  1.62230587e+00, -1.20672107e+00,         1.62689328e+00, -7.31323846e-03, -1.94860363e+00, -6.72776163e-01,         1.58643186e-01,  1.26540577e+00, -4.28948589e-02,  8.00365150e-01,         1.22754261e-01, -3.38057488e-01, -2.86949933e-01, -1.90901175e-01,         9.58132595e-02,  1.67628098e-02, -1.15865993e+00, -7.74521753e-02,         9.21975613e-01,  8.77448097e-02,  1.19769648e-01,  8.72838378e-01,        -5.17930627e-01,  2.08703017e+00,  1.57187074e-01,  8.24357629e-01,         1.58831030e-01, -3.60554941e-02,  6.69073462e-02,  8.68619025e-01,        -1.65251479e-01, -2.63280072e-03,  4.49088216e-01,  2.65792280e-01,        -2.78672546e-01, -2.49698222e-01, -3.28678280e-01,  1.61186063e+00,         7.50159919e-01,  9.43250656e-01,  2.64264607e+00,  1.49981415e+00,        -1.47657365e-01,  2.22085625e-01, -9.64923725e-02,  8.96389008e-01,         8.56586277e-01,  6.52531505e-01,  1.18778634e+00, -4.09094930e-01,         2.40136123e+00, -4.94153760e-02, -3.26699525e-01, -3.20687294e-01,        -3.32433254e-01, -7.21246123e-01, -1.50403976e-01,  2.21771318e-02,         1.64047623e+00, -1.07954025e+00, -1.56783760e-02,  3.86069506e-01,         6.36487663e-01, -3.87088686e-01, -3.84495296e-02,  9.24658775e-01,         1.21209376e-01, -7.65551269e-01,  1.65841177e-01,  4.71289992e-01,        -1.59651804e+00, -5.07207823e+00, -2.18156517e-01,  1.52839410e+00,        -1.00206149e+00,  1.89763218e-01,  8.80198181e-01,  3.45703691e-01,        -3.67146581e-01,  2.22651526e-01,  7.16562688e-01, -5.59036851e-01,         1.06786025e+00, -6.41773315e-03, -7.46931285e-02, -2.32269876e-02,         7.27270246e-01,  1.09856978e-01, -4.98229682e-01, -1.07638258e-02,         4.63894486e-01, -8.38394642e-01,  2.33984900e+00,  7.08481431e-01,         5.18927515e-01, -5.96308172e-01, -5.63266373e+00,  1.75844848e-01,         1.54760599e+00, -2.86110908e-01, -1.03822000e-01, -1.25968766e+00,         1.83833435e-01, -4.34105724e-01,  1.82174593e-01, -6.52810216e-01,        -4.42279786e-01,  3.65144759e-02,  7.96798706e-01, -1.10979962e+00,         3.23842056e-02,  3.82655025e-01, -8.92374814e-02,  5.18302560e-01,         3.88944089e-01,  1.28104910e-01,  6.59166515e-01, -8.44656117e-03,         1.23831403e+00, -3.96970838e-01,  3.42929453e-01, -3.88821691e-01,        -6.03508130e-02, -3.97913665e-01,  1.18266392e+00, -7.19693974e-02,         8.77067626e-01, -1.34145796e-01,  2.43914891e-02,  1.28763533e+00,        -2.74281949e-01,  1.01189661e+00,  7.37564206e-01, -5.51327392e-02,         5.02288461e-01,  2.64819860e-02, -4.81234305e-02,  7.36508608e-01,        -1.93657368e-01,  1.46965492e+00, -8.91932428e-01, -1.36684000e+00,         8.23317245e-02, -8.88911188e-01,  4.62448448e-01, -3.88297170e-01,         2.67349817e-02,  1.21356763e-01,  3.29228081e-02,  4.43954736e-01,         5.72048426e-01,  1.09117612e-01,  5.13045013e-01,  7.46340454e-02,         9.29429382e-02, -3.52901340e-01, -4.59741145e-01,  6.13709927e-01,         1.09723318e+00,  2.73241013e-01,  8.10347125e-02, -3.50776732e-01,         5.29499710e-01, -1.64967313e-01,  1.45703804e+00,  1.52050275e-02,        -7.41524875e-01, -1.83350705e-02, -1.04122353e+00,  9.90509868e-01,         1.16446042e+00, -5.99369764e-01, -9.41796660e-01,  1.19426596e+00,         6.51504755e-01,  8.86199176e-02,  8.88687193e-01, -8.37571263e-01,         2.83995688e-01, -3.68761897e-01,  1.28118262e-01, -8.05284858e-01,         9.92766559e-01, -1.97005361e-01,  2.20025137e-01,  5.11929929e-01,         7.78715670e-01,  5.41897237e-01, -3.36303324e-01,  4.66273338e-01,        -1.25307870e+00,  4.51680332e-01, -3.47123891e-01, -1.73065737e-01,        -3.76180738e-01,  4.51277852e-01, -4.84155864e-01,  1.23838177e-02,         3.86013627e-01,  2.48364195e-01, -2.62042999e-01, -8.93366784e-02,         1.09324825e+00,  3.02947074e-01, -1.37722754e+00,  1.12023473e-01,        -1.79966956e-01,  1.56048998e-01,  4.42324579e-01, -9.01299298e-01,         1.27221859e+00, -5.80377638e-01,  8.53511333e-01,  6.99844539e-01]'})
        data = {"message":"Data Fetched Successfully"}
        return jsonify(data)
    

# retirevedClasses = {"results": clothClasses.getClassLabels(val)}