import unittest
from unittest.mock import patch, MagicMock
from pyspark.sql import SparkSession
from spark.feature_engineering import process_batch

class TestSparkStreaming(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a local Spark session for the tests."""
        cls.spark = SparkSession.builder \
            .appName("SparkTest") \
            .master("local[2]") \
            .getOrCreate()

    @patch('spark.feature_engineering.load_redis_config')
    def test_process_batch_logic(self, mock_load_redis_config):
        """
        Unit test for the process_batch function, which is the core
        of the Spark streaming job's logic.
        """
        # Mock the configuration loader
        mock_load_redis_config.return_value = {'features_key_prefix': 'test_features'}

        # Create a sample aggregated DataFrame, as would be produced by the streaming query
        feature_data = [
            ("user1", 55.0, 3),
            ("user2", 18.5, 2)
        ]
        feature_df = self.spark.createDataFrame(feature_data, ["user_id", "avg_amount", "txn_count"])

        # We need to mock the DataFrameWriter that is used inside process_batch
        # to write to Redis and Parquet.
        mock_writer = MagicMock()
        mock_writer.format.return_value.option.return_value.option.return_value.mode.return_value.save.return_value = None
        mock_writer.mode.return_value.parquet.return_value = None
        
        with patch('pyspark.sql.DataFrame.write', new=mock_writer):
            # Call the function with our test DataFrame
            process_batch(feature_df, epoch_id=1)

            # Assert that the write operations were called
            self.assertTrue(mock_writer.format.called)
            self.assertTrue(mock_writer.mode.called)
            
            # Check if Redis write was attempted
            redis_call_args = mock_writer.format.call_args_list[0]
            self.assertEqual(redis_call_args[0][0], "org.apache.spark.sql.redis")
            
            # Check if Parquet write was attempted
            parquet_call_args = mock_writer.mode.call_args_list[0]
            self.assertEqual(parquet_call_args[0][0], "append")


    @classmethod
    def tearDownClass(cls):
        """Stop the Spark session."""
        cls.spark.stop()

if __name__ == '__main__':
    unittest.main()
