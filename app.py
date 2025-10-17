from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

# Load trained artifacts
model = joblib.load("model_rf.joblib")
mlb = joblib.load("mlb.joblib")
le = joblib.load("label_encoder.joblib")

app = Flask(__name__)
CORS(app)   # <- allow all origins for dev


@app.route("/")
def home():
    return jsonify({"message": "Symptom2Disease API is running 🚀"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    symptoms = data.get("symptoms", [])

    # Check if symptoms provided
    if not symptoms:
        return jsonify({"error": "Please provide a list of symptoms"}), 400

    try:
        X = mlb.transform([symptoms])
        pred = model.predict(X)
        disease = le.inverse_transform(pred)[0]
        return jsonify({"predicted_disease": disease})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
