from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import json

# Load trained artifacts
model = joblib.load("model_rf.joblib")
mlb = joblib.load("mlb.joblib")
le = joblib.load("label_encoder.joblib")

# Load symptom vocabulary for frontend
with open("data/symptom_vocab.json") as f:
    symptom_vocab = json.load(f)

app = Flask(__name__)
CORS(app)  # allow all origins for development

@app.route("/")
def home():
    return jsonify({"message": "Symptom2Disease API is running 🚀"})

@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    """Return the list of known symptoms for checkboxes"""
    return jsonify({"symptoms": symptom_vocab})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    symptoms = data.get("symptoms", [])

    if not symptoms:
        return jsonify({"error": "Please provide a list of symptoms"}), 400

    try:
        X = mlb.transform([symptoms])
        probs = model.predict_proba(X)[0]
        # Top-3 prediction indices
        top3_idx = probs.argsort()[-3:][::-1]
        top3_diseases = [{"disease": le.inverse_transform([i])[0], "probability": round(probs[i], 3)} for i in top3_idx]
        return jsonify({"top3_predictions": top3_diseases})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
