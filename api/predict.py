import json
import joblib
import os
model = None
mlb = None
le = None

def load_models():
    global model, mlb, le
    if model is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model = joblib.load(os.path.join(script_dir, "model_rf.joblib"))
        mlb = joblib.load(os.path.join(script_dir, "mlb.joblib"))
        le = joblib.load(os.path.join(script_dir, "label_encoder.joblib"))

def handler(event, context):
    try:
        # Load models on first request
        load_models()
        
        body = event.get('body', '')
        data = json.loads(body) if body else {}
        symptoms = data.get("symptoms", [])

        if not symptoms:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Please provide a list of symptoms"}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Predict using the loaded models
        X = mlb.transform([symptoms])
        probs = model.predict_proba(X)[0]
        top3_idx = probs.argsort()[-3:][::-1]
        top3_diseases = [
            {"disease": le.inverse_transform([i])[0], "probability": round(probs[i], 3)}
            for i in top3_idx
        ]
        
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
