from pyspark.sql import SparkSession
import yaml

def load_config(config_path='configs/spark_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_spark_session():
    """
    Initializes and returns a Spark session, configured to connect to Redis.
    """
    config = load_config()
    spark_config = config['redis_connector']

    return SparkSession.builder \
        .appName(config['app_name']) \
        .master(config['master_url']) \
        .config("spark.redis.host", spark_config['host']) \
        .config("spark.redis.port", spark_config['port']) \
        .config("spark.jars.packages", spark_config['jar_package']) \
        .getOrCreate()
