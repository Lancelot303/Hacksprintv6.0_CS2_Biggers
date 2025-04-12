import joblib
import pandas as pd
import json
from flask import Flask, request, jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

def custom_tokenizer(x):
    return x.replace('.', ' ').replace('/', ' ').replace('-', ' ').split()

# Load the model
try:
    model = joblib.load('RF_categorizer.pkl')
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

def custom_tokenizer(x):
    return x.replace('.', ' ').replace('/', ' ').replace('-', ' ').split()

def process_data(json_data):
    try:
        if isinstance(json_data, dict):
            data = pd.DataFrame([json_data])
        elif isinstance(json_data, list):
            data = pd.DataFrame(json_data)
        else:
            return {"error": "Invalid JSON format"}
        
        data['text'] = data['domain'].fillna('') + ' ' + data['title'].fillna('') + ' ' + data['description'].fillna('')
        
        results = []
        for idx, row in data.iterrows():
            prediction = model.predict([row['text']])[0]
            result = {
                #"input_id": idx+1,
                "url": row['domain'],
                "predicted_category": prediction
            }
            results.append(result)
            
            #print(f"Input #{idx+1}")
            print(f"URL: {row['domain']}")
            print(f"Predicted Category: {prediction}")
            print("-" * 40)
            
        return results
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return {"error": str(e)}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No data provided"}), 400
        
        results = process_data(json_data)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting server on port 5005...")
    app.run(host='192.168.197.77', port=5005, debug=False)