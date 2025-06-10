from pyspark.sql.functions import avg, count, from_json
from pyspark.sql.types import StructType, StructField, StringType, FloatType, DoubleType, BooleanType
from spark.utils import get_spark_session
import yaml

def load_kafka_config(config_path='configs/kafka_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_redis_config(config_path='configs/redis_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def process_batch(df, epoch_id):
    """
    This function is called by `foreachBatch` in the streaming query.
    It writes the aggregated features from the micro-batch to two sinks:
    1. Redis: For real-time, low-latency lookups by the inference service.
    2. Parquet Files: To build a historical dataset for model training.
    """
    redis_config = load_redis_config()
    
    # Sink 1: Write to Redis
    df.write \
        .format("org.apache.spark.sql.redis") \
        .option("table", redis_config['features_key_prefix']) \
        .option("key.column", "user_id") \
        .mode("overwrite") \
        .save()
    
    # Sink 2: Append to Parquet files for historical training data
    df.write.mode("append").parquet("data/processed/features")
    
    print(f"--- Batch {epoch_id} processed ---")
    df.show()

def main():
    spark = get_spark_session()
    spark.sparkContext.setLogLevel("ERROR")
    
    kafka_config = load_kafka_config()
    
    schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("amount", FloatType(), True),
        StructField("timestamp", DoubleType(), True),
        StructField("is_suspicious_amount", BooleanType(), True)
    ])

    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_config['bootstrap_servers']) \
        .option("subscribe", kafka_config['topics']['validated_transactions']) \
        .load()

    parsed_df = kafka_df.select(from_json(kafka_df.value.cast("string"), schema).alias("data")).select("data.*")

    feature_df = parsed_df.groupBy("user_id").agg(
        avg("amount").alias("avg_amount"),
        count("transaction_id").alias("txn_count")
    )

    query = feature_df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("update") \
        .start()
        
    print("Spark streaming job started. Waiting for data from Kafka...")
    query.awaitTermination()

if __name__ == '__main__':
    main()
