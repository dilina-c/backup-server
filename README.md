# backup-server

This code defines a Flask web application with two endpoints: /predict and /train.

The /predict endpoint receives a JSON object containing a data reading, which is used to predict whether a device is on or off. The data reading includes a timestamp and a device ID. The code converts the timestamp to the day of the week and time of day, and uses these as features for a trained machine learning model. The model predicts whether the device is on or off, and returns the prediction along with the original requested value as a JSON response.

The /train endpoint trains a machine learning model for each device in a Firestore database. The code retrieves the last three months of readings for each device, converts the timestamps to day of the week and time of day, and uses these as features to train a random forest classifier. The trained model is saved to a file and uploaded to a Google Cloud Storage bucket.

The code imports several Python packages, including Flask, pandas, scikit-learn, joblib, and firebase_admin. It uses Firebase Admin SDK to authenticate and interact with Firebase services, including Firestore and Cloud Storage.
