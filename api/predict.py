import joblib
import json

# Load trained artifacts
model = joblib.load("model_rf.joblib")
mlb = joblib.load("mlb.joblib")
le = joblib.load("label_encoder.joblib")

# Load symptom vocabulary
with open("data/symptom_vocab.json") as f:
    symptom_vocab = json.load(f)

def handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', 'GET')
    body = event.get('body', '')

    if method == 'GET' and path == '/api/symptoms':
        return {
            'statusCode': 200,
            'body': json.dumps({"symptoms": symptom_vocab}),
            'headers': {'Content-Type': 'application/json'}
        }
    elif method == 'POST' and path == '/api/predict':
        try:
            data = json.loads(body) if body else {}
            symptoms = data.get("symptoms", [])

            if not symptoms:
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": "Please provide a list of symptoms"}),
                    'headers': {'Content-Type': 'application/json'}
                }

            X = mlb.transform([symptoms])
            probs = model.predict_proba(X)[0]
            top3_idx = probs.argsort()[-3:][::-1]
            top3_diseases = [{"disease": le.inverse_transform([i])[0], "probability": round(probs[i], 3)} for i in top3_idx]
            return {
                'statusCode': 200,
                'body': json.dumps({"top3_predictions": top3_diseases}),
                'headers': {'Content-Type': 'application/json'}
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({"error": str(e)}),
                'headers': {'Content-Type': 'application/json'}
            }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({"error": "Not Found"}),
            'headers': {'Content-Type': 'application/json'}
        }
