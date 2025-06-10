from flask import Flask, request, jsonify
import mlflow.pyfunc
import json
import pandas as pd
import yaml
from inference_service.utils.redis_features import get_redis_client
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# --- Metrics Initialization ---
metrics = PrometheusMetrics(app)
# Static metric to track the total number of predictions
predictions_total = metrics.counter(
    'predictions_total', 'Total number of predictions',
    labels={'result': lambda: 'fraud' if 'is_fraud' in request.json and request.json['is_fraud'] else 'not_fraud'}
)
# --- End Metrics Initialization ---

def load_mlflow_config(config_path='configs/mlflow_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_redis_config(config_path='configs/redis_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# --- Service Initialization ---
model = None
redis_client = None
redis_key_prefix = 'user_features' # Default

try:
    mlflow_config = load_mlflow_config()
    model_uri = f"models:/{mlflow_config['model_name']}/Production"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"Successfully loaded model '{mlflow_config['model_name']}' from '{model_uri}'")
except Exception as e:
    print(f"Error loading model: {e}")

redis_client = get_redis_client()
if redis_client:
    try:
        redis_config = load_redis_config()
        redis_key_prefix = redis_config['features_key_prefix']
    except Exception as e:
        print(f"Could not load Redis key prefix from config: {e}")
# --- End Initialization ---


def preprocess(transaction_data, user_features):
    """
    Combines real-time transaction data with historical features from Redis
    to create a feature vector for the model.
    """
    avg_amount = float(user_features.get('avg_amount', 0.0))
    txn_count = int(user_features.get('txn_count', 0))

    feature_vector = pd.DataFrame({
        'avg_amount': [avg_amount],
        'txn_count': [txn_count]
    })
    
    return feature_vector


@app.route('/predict', methods=['POST'])
@predictions_total
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

        user_features_raw = redis_client.hgetall(f"{redis_key_prefix}:{user_id}")
        
        features = preprocess(data, user_features_raw)

        prediction = model.predict(features)
        
        result = {"is_fraud": bool(prediction[0])}
        # Attach result to request context for the metric counter
        request.json['is_fraud'] = result['is_fraud']
        
        return jsonify(result)

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": "An internal error occurred during prediction."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
