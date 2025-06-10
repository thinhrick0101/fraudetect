from kafka import KafkaProducer
import json
import time
import yaml

def load_config(config_path='configs/kafka_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_producer():
    config = load_config()
    return KafkaProducer(
        bootstrap_servers=config['bootstrap_servers'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_transaction(producer, topic, data):
    producer.send(topic, data)

# Simulate transaction data streaming
if __name__ == "__main__":
    producer = create_producer()
    topic_name = load_config()['topics']['raw_transactions']
    
    while True:
        try:
            transaction = {
                'transaction_id': f'txn_{int(time.time())}',
                'user_id': f'user_{int(time.time()) % 100}',
                'amount': round(100.0 * (int(time.time()) % 10) + 0.5, 2),
                'timestamp': time.time()
            }
            send_transaction(producer, topic_name, transaction)
            print(f"Sent transaction: {transaction}")
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping producer.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)
    
    producer.close()
