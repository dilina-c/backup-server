from flask import Flask
from flask import request, jsonify
import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials,firestore,storage
from datetime import datetime, timedelta
import os

app = Flask(__name__)

cred = credentials.Certificate("smart-power-adapter-3a443-firebase-adminsdk-4gp49-a276da6c45.json")
firebase_admin.initialize_app(cred,{'storageBucket' : "smart-power-adapter-3a443.appspot.com"})
db = firestore.client()
devices_col_ref = db.collection(u'devices')
bucket = storage.bucket()

@app.route('/predict',methods=  ['POST'])
def makePrediction():
   predictValue = [[]]

   json_data = request.get_json()
   predictData=json_data['data reading']

   day_of_week = datetime.fromtimestamp(predictData["time"]/1000).weekday()
   time_of_day = datetime.fromtimestamp(predictData["time"]/1000).strftime("%I") 

   predictValue = [[day_of_week,time_of_day]]
   json_deviceid = json_data['device_id'] 
   fileName = json_deviceid +'.joblib'
   storage_blob = bucket.blob(fileName)
   storage_blob.download_to_filename(fileName)
   model = joblib.load(fileName)
   prediction = model.predict(predictValue)
   #os.remove(fileName)
   return jsonify({"response":prediction.tolist(),"requested_value":predictValue})
  

if __name__ == '__main__':
   app.run(port=8080, debug=False)