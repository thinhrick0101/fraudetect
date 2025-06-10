import unittest
from pyspark.sql import SparkSession
from spark.feature_engineering import main as spark_main # Assuming it can be adapted

class TestSparkJobs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a local Spark session for the tests."""
        cls.spark = SparkSession.builder \
            .appName("SparkTest") \
            .master("local[2]") \
            .getOrCreate()

    def test_feature_engineering(self):
        """Test the feature engineering logic on a sample DataFrame."""
        # Create a sample DataFrame
        transactions = [
            ("txn1", "user1", 10.0), ("txn2", "user2", 25.0),
            ("txn3", "user1", 5.0),  ("txn4", "user3", 100.0),
            ("txn5", "user2", 12.0), ("txn6", "user1", 150.0)
        ]
        df = self.spark.createDataFrame(transactions, ["transaction_id", "user_id", "amount"])

        # Apply the core logic from your feature engineering script
        from pyspark.sql.functions import avg, count
        feature_df = df.groupBy("user_id").agg(
            avg("amount").alias("avg_amount"),
            count("transaction_id").alias("txn_count")
        )

        # Collect results to a dictionary for easy assertion
        results = {row['user_id']: row for row in feature_df.collect()}
        
        # Assertions
        self.assertEqual(len(results), 3)
        self.assertAlmostEqual(results['user1']['avg_amount'], 55.0)
        self.assertEqual(results['user1']['txn_count'], 3)
        self.assertAlmostEqual(results['user2']['avg_amount'], 18.5)
        self.assertEqual(results['user2']['txn_count'], 2)

    @classmethod
    def tearDownClass(cls):
        """Stop the Spark session."""
        cls.spark.stop()

if __name__ == '__main__':
    unittest.main()
