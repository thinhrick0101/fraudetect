from pyspark.sql.functions import avg, count
from spark.utils import get_spark_session
import yaml

def load_redis_config(config_path='configs/redis_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    spark = get_spark_session()
    redis_config = load_redis_config()

    # In a real-world scenario, this job would consume from the 'validated_transactions'
    # Kafka topic. For this example, we continue with a dummy DataFrame.
    transactions = [
        ("txn1", "user1", 10.0), ("txn2", "user2", 25.0), ("txn3", "user1", 5.0),
        ("txn4", "user3", 100.0), ("txn5", "user2", 12.0), ("txn6", "user1", 150.0)
    ]
    df = spark.createDataFrame(transactions, ["transaction_id", "user_id", "amount"])

    # Feature engineering
    feature_df = df.groupBy("user_id").agg(
        avg("amount").alias("avg_amount"),
        count("transaction_id").alias("txn_count")
    )

    # Write features to Redis
    feature_df.write \
        .format("org.apache.spark.sql.redis") \
        .option("table", redis_config['features_key_prefix']) \
        .option("key.column", "user_id") \
        .mode("overwrite") \
        .save()
        
    print("Successfully generated and saved features to Redis.")
    spark.stop()

if __name__ == '__main__':
    main()
