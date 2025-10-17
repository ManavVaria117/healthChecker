import joblib

mlb = joblib.load("mlb.joblib")
le = joblib.load("label_encoder.joblib")
model = joblib.load("model_rf.joblib")

user_symptoms = ["fever", "cough", "sore_throat"]
X = mlb.transform([user_symptoms])
pred = model.predict(X)
print("Predicted disease:", le.inverse_transform(pred)[0])
