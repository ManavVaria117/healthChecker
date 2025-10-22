import json

def handler(event, context):
    # This function now only handles POST requests for predictions.
    try:
        body = event.get('body', '')
        data = json.loads(body) if body else {}
        symptoms = data.get("symptoms", [])

        if not symptoms:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Please provide a list of symptoms"}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Dummy prediction for testing
        top3_diseases = [
            {"disease": "Common Cold", "probability": 0.8},
            {"disease": "Flu", "probability": 0.6},
            {"disease": "Allergy", "probability": 0.4}
        ]
        return {
            'statusCode': 200,
            'body': json.dumps({"top3_predictions": top3_diseases}),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": f"Prediction failed: {str(e)}"}),
            'headers': {'Content-Type': 'application/json'}
        }
