from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def send_transaction(data):
    producer.send('transactions', data)

# Simulate transaction data streaming
if __name__ == "__main__":
    while True:
        transaction = {
            'transaction_id': 'txn123',
            'user_id': 'user456',
            'amount': 100.0,
            'timestamp': time.time()
        }
        send_transaction(transaction)
        print(f"Sent transaction: {transaction}")
        time.sleep(1)
