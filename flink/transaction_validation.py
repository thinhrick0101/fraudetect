from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.expressions import col, lit
from flink.utils import get_flink_env
import yaml

def load_config(config_path='configs/kafka_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    env = get_flink_env()
    table_env = StreamTableEnvironment.create(env)
    config = load_config()

    kafka_bootstrap_servers = config['bootstrap_servers']
    raw_topic = config['topics']['raw_transactions']
    validated_topic = config['topics']['validated_transactions']
    consumer_group = config['consumer_group']

    # Create Kafka source table for raw transactions
    table_env.execute_sql(f"""
        CREATE TABLE transactions (
            `transaction_id` STRING,
            `user_id` STRING,
            `amount` FLOAT,
            `timestamp` DOUBLE
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{raw_topic}',
            'properties.bootstrap.servers' = '{kafka_bootstrap_servers}',
            'properties.group.id' = '{consumer_group}',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        );
    """)

    # Create Kafka sink table for validated and enriched transactions
    table_env.execute_sql(f"""
        CREATE TABLE validated_transactions (
            `transaction_id` STRING,
            `user_id` STRING,
            `amount` FLOAT,
            `timestamp` DOUBLE,
            `is_suspicious_amount` BOOLEAN
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{validated_topic}',
            'properties.bootstrap.servers' = '{kafka_bootstrap_servers}',
            'format' = 'json'
        );
    """)

    # Read from source, validate, and enrich the data
    source_table = table_env.from_path("transactions")
    
    enriched_table = source_table \
        .filter(col('amount') > 0) \
        .add_columns(
            (col('amount') > 1000).if_else(lit(True, DataTypes.BOOLEAN()), lit(False, DataTypes.BOOLEAN())).alias('is_suspicious_amount')
        )

    # Insert the enriched data into the sink table
    enriched_table.execute_insert("validated_transactions").wait()

if __name__ == '__main__':
    main()
