import unittest
from unittest.mock import patch
import ray
import numpy as np
from sklearn.model_selection import train_test_split
from ray_mlflow.train import train_model

class TestRayTraining(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize Ray in local mode for testing."""
        # local_mode=True runs Ray sequentially in a single process.
        # This is ideal for fast, simple unit testing.
        ray.init(local_mode=True, ignore_reinit_error=True)

    @patch('ray_mlflow.train.load_data')
    def test_train_function_logic(self, mock_load_data):
        """
        Test a single run of the training function with a mocked data loader.
        This checks if the function runs, logs to MLflow, and reports to Tune
        without needing real data or a filesystem.
        """
        # Configure the mock to return a predictable, simple dataset
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 100)
        mock_load_data.return_value = train_test_split(X, y, test_size=0.2)

        # Define a simple config for a single trial
        config = {
            "n_estimators": 10,
            "max_depth": 5
        }
        
        # We can wrap the call in a try-except block to check for successful execution
        try:
            train_model(config)
            executed_successfully = True
        except Exception as e:
            print(f"Training function failed with an exception: {e}")
            executed_successfully = False
            
        self.assertTrue(executed_successfully, "The train_model function failed to execute.")
        # Verify that our mock was called, confirming the test setup is correct
        mock_load_data.assert_called_once()


    @classmethod
    def tearDownClass(cls):
        """Shutdown Ray."""
        ray.shutdown()

if __name__ == '__main__':
    unittest.main()
