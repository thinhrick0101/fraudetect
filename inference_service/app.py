from flask import Flask, request, jsonify
import mlflow.pyfunc
import redis
import json
import numpy as np

app = Flask(__name__)

# Load the model from the MLflow Model Registry.
# The model URI is in the format `models:/<model_name>/<version_or_stage>`.
# We'll load the "Production" stage of our model.
try:
    model = mlflow.pyfunc.load_model('models:/fraud_detection_model/Production')
except Exception as e:
    # If the model isn't available in production, we can fall back to a specific version or staging.
    # For this example, we'll exit if it's not found.
    print(f"Error loading model: {e}")
    model = None # Or load a fallback model

# Connect to Redis
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    redis_client = None

def preprocess(transaction_data, user_features):
    """
    A placeholder for your feature preprocessing logic.
    This should transform the raw transaction and user features into the format
    expected by the model.
    """
    # Example: one-hot encode categorical features, scale numerical features, etc.
    # For the dummy model, we expect a numpy array of a certain shape.
    # This is highly dependent on your actual model's training.
    # Let's assume the model expects 10 features.
    features = np.random.rand(1, 10) # Dummy feature vector
    return features


@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 500

    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id not provided"}), 400

        # Fetch pre-computed features from Redis
        user_features_raw = redis_client.get(f"user_features:{user_id}")
        user_features = json.loads(user_features_raw) if user_features_raw else {}

        # Preprocess the input data to create a feature vector
        features = preprocess(data, user_features)

        # Get prediction from the model
        prediction = model.predict(features)

        # The output of predict() is often a numpy array.
        return jsonify({"is_fraud": bool(prediction[0])})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Running in debug mode is not recommended for production
    app.run(host='0.0.0.0', port=5001, debug=True)
