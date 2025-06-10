import unittest
import json
from unittest.mock import patch, MagicMock

# Import the Flask app object
from inference_service.app import app

class TestInferenceAPI(unittest.TestCase):

    def setUp(self):
        """Set up the Flask test client."""
        self.app = app.test_client()
        self.app.testing = True

    @patch('inference_service.app.mlflow.pyfunc.load_model')
    @patch('inference_service.app.redis.Redis')
    def test_predict_endpoint(self, mock_redis, mock_mlflow_load):
        """Test the /predict endpoint with mocked dependencies."""
        # Mock the MLflow model's predict method
        mock_model = MagicMock()
        mock_model.predict.return_value = [1] # Simulate a fraud prediction
        mock_mlflow_load.return_value = mock_model
        
        # Mock the Redis client's hgetall method
        mock_redis_client = MagicMock()
        mock_redis_client.hgetall.return_value = {'avg_amount': '150.0', 'txn_count': '10'}
        mock_redis.return_value = mock_redis_client

        # The app needs to be re-initialized to use the mocks
        # A better approach would be to use a Flask app factory pattern.
        # For this test, we can patch the globals directly used by the app.
        with patch('inference_service.app.model', mock_model), \
             patch('inference_service.app.redis_client', mock_redis_client):
            
            payload = {'user_id': 'user123', 'amount': 200.0}
            response = self.app.post('/predict',
                                     data=json.dumps(payload),
                                     content_type='application/json')

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.get_data(as_text=True))
            self.assertIn('is_fraud', data)
            self.assertEqual(data['is_fraud'], True)

    def test_predict_no_user_id(self):
        """Test for a 400 error when user_id is missing."""
        payload = {'amount': 200.0}
        response = self.app.post('/predict',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
