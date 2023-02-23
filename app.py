from flask import Flask
from flask import request, jsonify
#import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials,firestore,storage
from datetime import datetime, timedelta
import os,requests

app = Flask(__name__)

cred = credentials.Certificate("smart-power-adapter-3a443-firebase-adminsdk-4gp49-a276da6c45.json")
firebase_admin.initialize_app(cred,{'storageBucket' : "smart-power-adapter-3a443.appspot.com"})
db = firestore.client()
devices_col_ref = db.collection(u'devices')
bucket = storage.bucket()

url = 'http://52c8-112-134-140-140.in.ngrok.io/create-anomaly' 

@app.route('/predict',methods=  ['POST'])
def makePrediction():
   try:
      predictValue = [[]]

      json_data = request.get_json()
      predictData=json_data['data_reading']

      day_of_week = datetime.fromtimestamp(predictData["time"]/1000).weekday()
      time_of_day = datetime.fromtimestamp(predictData["time"]/1000).strftime("%I")

      predictValue = [[day_of_week,time_of_day]]
      json_deviceid = json_data['device_id'] 
      fileName = json_deviceid +'_anomaly.joblib'
      if not os.path.exists(fileName):
         try:
            storage_blob = bucket.blob(fileName)
            storage_blob.download_to_filename(fileName)
         except Exception as e: 
            print(e)
            return 'model file could not retrieved'   
      model = joblib.load(fileName)
      prediction = model.predict(predictValue)
      #os.remove(fileName)
      if prediction == False:
         UIJsonObject ={
            "device_id": json_deviceid,
            "requested_value": predictValue,
            "response": prediction.tolist(),
            "data reading": predictData
         }
         response=requests.post(url, json = UIJsonObject)
         print(response.text)
      return jsonify({"requested device id":json_deviceid,"response":prediction.tolist(),"requested_value":predictValue})
   except Exception as e:
      print(e)
      return 'error'

@app.route('/cforcast',methods=  ['POST','GET'])
def makeCForcast():
   try:
      json_data = request.get_json()
      json_deviceid = json_data['device_id']
      fileName = json_deviceid +'_power_consumption.joblib' 
      if not os.path.exists(fileName):
         try:
            storage_blob = bucket.blob(fileName)
            storage_blob.download_to_filename(fileName)
         except Exception as e: 
            print(e)
            return 'model file could not retrieved'
      model = joblib.load(fileName)
      power_output = {"device_id": json_deviceid, "data": {}}
      datalog=power_output["data"]
      for day in range(7):
         if day not in datalog:
            datalog[day] = []
         for hour in range(24):
            power = model.predict([[day, hour]])
            datalog[day].append([power[0]])
      #os.remove(fileName)
      return power_output
   except Exception as e:
      print(e)
      return 'error'


if __name__ == '__main__':
   app.run(port=8080, debug=False)