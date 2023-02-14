from flask import Flask
from flask import request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score  
import joblib
import firebase_admin
from firebase_admin import credentials,firestore
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials ,storage
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
   # fileName = 'Prediction-Model.joblib'
   #storage_blob = bucket.blob(fileName)
   #storage_blob.download_to_filename(fileName)
   model = joblib.load(fileName)
   prediction = model.predict(predictValue)
   #os.remove(fileName)
   return jsonify({"response":prediction.tolist(),"requested_value":predictValue})
  

@app.route('/train')
def trainPredictionModel():
   now = datetime.now()
   three_months_ago = now - timedelta(days=2)
   data=[]
   for device_doc_snap in devices_col_ref.stream():
      device_id = device_doc_snap.id
      readings_col_ref=device_doc_snap.reference.collection(u'readings')
    
      for reading_doc_snap in readings_col_ref.where(u"time", u">=", three_months_ago.timestamp()).stream():
         datum=reading_doc_snap.to_dict()
         datum["isOn"] = True if datum["i"] > 0.4 else False
         datum["day_of_week"] = datetime.fromtimestamp(datum["time"]/1000).weekday()
         datum["time_of_day"] = datetime.fromtimestamp(datum["time"]/1000).strftime("%I")
         data.append(datum)

      df= pd.DataFrame.from_dict(data)

      X = df[['time_of_day', 'day_of_week']]
      y = df['isOn']

      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

      model = RandomForestClassifier()
      model.fit(X_train.values, y_train.values)

      score = model.score(X_test.values, y_test.values)
      print(f'Accuracy: {score:.2f}')
      fileName = device_id +'.joblib'
      joblib.dump(model,f'{fileName}')
      
      blob = bucket.blob(fileName)
      blob.upload_from_filename(fileName)
      #os.remove(fileName)
   return ['prediction model trained']

if __name__ == '__main__':
   app.run(port=8080, debug=False)