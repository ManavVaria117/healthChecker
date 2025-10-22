import json

def handler(event, context):
    # Dummy symptoms for testing
    symptoms = ['fever', 'headache', 'fatigue', 'cough', 'nausea']
    return {
        'statusCode': 200,
        'body': json.dumps({"symptoms": symptoms}),
        'headers': {'Content-Type': 'application/json'}
    }
