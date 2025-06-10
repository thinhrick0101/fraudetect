from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count

def main():
    # In a real setup, Spark session creation would be more elaborate,
    # possibly connecting to a remote cluster and configuring connectors.
    # For the Spark-Redis connector, you would need to add the JAR to your Spark setup
    # e.g., --packages com.redislabs:spark-redis_2.12:3.2.0
    spark = SparkSession.builder \
        .appName('FraudFeatureGen') \
        .config("spark.redis.host", "localhost") \
        .config("spark.redis.port", "6379") \
        .getOrCreate()

    # The user example reads from HDFS. In a real project, this could be any data lake
    # or warehouse like S3, GCS, or a Delta Lake table.
    # For this example, let's assume we have sample data in the `data/processed` dir.
    # We would first need to get the "validated_transactions" from Kafka into a file.
    # A separate consumer or Flink job could do that.
    # For now, we'll create a dummy dataframe.
    
    # Create a dummy DataFrame for demonstration
    transactions = [
        ("txn1", "user1", 10.0), ("txn2", "user2", 25.0), ("txn3", "user1", 5.0),
        ("txn4", "user3", 100.0), ("txn5", "user2", 12.0), ("txn6", "user1", 150.0)
    ]
    df = spark.createDataFrame(transactions, ["transaction_id", "user_id", "amount"])

    # Feature engineering: calculate average amount and transaction count per user
    feature_df = df.groupBy("user_id").agg(
        avg("amount").alias("avg_amount"),
        count("transaction_id").alias("txn_count")
    )

    # Write features to Redis for the online inference service to use.
    # The key will be "user_features:<user_id>"
    feature_df.write \
        .format("org.apache.spark.sql.redis") \
        .option("table", "user_features") \
        .option("key.column", "user_id") \
        .mode("overwrite") \
        .save()
        
    print("Successfully generated and saved features to Redis.")
    spark.stop()

if __name__ == '__main__':
    main()
