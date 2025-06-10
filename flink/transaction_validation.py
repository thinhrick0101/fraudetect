from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    table_env = StreamTableEnvironment.create(env)

    # Note: In a real-world scenario, you would configure the Kafka connection details
    # through a configuration file or command-line arguments.
    # For Flink 1.17+, the syntax for table creation has changed slightly.
    # This example uses a syntax compatible with recent versions.

    table_env.execute_sql("""
        CREATE TABLE transactions (
            `transaction_id` STRING,
            `user_id` STRING,
            `amount` FLOAT,
            `timestamp` DOUBLE
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'transactions',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'flink_fraud_detector',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        );
    """)

    table_env.execute_sql("""
        CREATE TABLE validated_transactions (
            `transaction_id` STRING,
            `user_id` STRING,
            `amount` FLOAT,
            `timestamp` DOUBLE
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'validated_transactions',
            'properties.bootstrap.servers' = 'localhost:9092',
            'format' = 'json'
        );
    """)

    # Simple validation: filter out transactions with non-positive amounts
    table_env.from_path("transactions") \
        .filter("amount > 0") \
        .execute_insert("validated_transactions").wait()

if __name__ == '__main__':
    main()
