import unittest
import ray
from ray_mlflow.train import train_model

class TestRay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize Ray in local mode for testing."""
        ray.init(local_mode=True, ignore_reinit_error=True)

    def test_train_function(self):
        """
        Test a single run of the training function.
        This checks if the function runs, logs to MLflow (in-memory),
        and reports a metric to Tune without errors.
        """
        # Define a simple config for a single trial
        config = {
            "n_estimators": 10,
            "max_depth": 5
        }
        
        # We can wrap the call in a try-except block to check for successful execution
        try:
            # In local_mode, this runs sequentially in the same process.
            train_model(config)
            executed_successfully = True
        except Exception as e:
            print(f"Training function failed with an exception: {e}")
            executed_successfully = False
            
        self.assertTrue(executed_successfully)

    @classmethod
    def tearDownClass(cls):
        """Shutdown Ray."""
        ray.shutdown()

if __name__ == '__main__':
    unittest.main()
