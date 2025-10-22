import json
import os

def handler(event, context):
    try:
        # Construct path to the JSON file relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'symptom_vocab.json')

        with open(json_path) as f:
            symptom_vocab = json.load(f)
        
        return {
            'statusCode': 200,
            'body': json.dumps({"symptoms": symptom_vocab}),
            'headers': {'Content-Type': 'application/json'}
        }
    except FileNotFoundError:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Symptom vocabulary file not found."}),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
