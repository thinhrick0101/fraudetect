from flask import Flask, request, jsonify
import mlflow.pyfunc
import json
import numpy as np
import yaml
from inference_service.utils.redis_features import get_redis_client

app = Flask(__name__)

def load_mlflow_config(config_path='configs/mlflow_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# --- Service Initialization ---
model = None
redis_client = None

try:
    mlflow_config = load_mlflow_config()
    model_uri = f"models:/{mlflow_config['model_name']}/Production"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"Successfully loaded model '{mlflow_config['model_name']}' from '{model_uri}'")
except Exception as e:
    print(f"Error loading model: {e}")

redis_client = get_redis_client()
# --- End Initialization ---


def preprocess(transaction_data, user_features):
    """Placeholder for feature preprocessing logic."""
    features = np.random.rand(1, 10) # Dummy feature vector
    return features


@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not loaded"}), 503
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503

    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id not provided"}), 400

        # Fetch pre-computed features from Redis
        redis_key_prefix = 'user_features' # This could also be in a config
        user_features_raw = redis_client.hgetall(f"{redis_key_prefix}:{user_id}")
        
        # Preprocess the input data to create a feature vector
        features = preprocess(data, user_features_raw)

        # Get prediction from the model
        prediction = model.predict(features)
        
        return jsonify({"is_fraud": bool(prediction[0])})

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": "An internal error occurred during prediction."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
