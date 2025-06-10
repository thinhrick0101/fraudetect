import json
from kafka import KafkaConsumer
import yaml

def load_config(config_path='configs/kafka_config.yaml'):
    """Loads Kafka configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """
    A simple Kafka consumer that subscribes to a topic and prints messages.
    This is useful for debugging and verifying that the producer is working.
    """
    config = load_config()
    
    consumer = KafkaConsumer(
        config['topics']['raw_transactions'],
        bootstrap_servers=config['bootstrap_servers'],
        group_id=config['consumer_group'],
        auto_offset_reset='earliest',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    
    print(f"Subscribed to topic '{config['topics']['raw_transactions']}'. Waiting for messages...")
    
    try:
        for message in consumer:
            print(f"Received message: {message.value}")
    except KeyboardInterrupt:
        print("Stopping consumer.")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
