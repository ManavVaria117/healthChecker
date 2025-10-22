import json

def handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', 'GET')
    body = event.get('body', '')

    if method == 'GET' and path == '/api/symptoms':
        # Dummy symptoms for testing
        symptoms = ['fever', 'headache', 'fatigue']
        return {
            'statusCode': 200,
            'body': json.dumps({"symptoms": symptoms}),
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
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({"error": "Not Found"}),
            'headers': {'Content-Type': 'application/json'}
        }
