import unittest
import json
import time
from kafka import KafkaProducer, KafkaConsumer

class TestKafka(unittest.TestCase):

    def setUp(self):
        """Set up a Kafka producer and consumer for testing."""
        self.bootstrap_servers = 'localhost:9092'
        self.topic = 'test_topic'
        
        # It's good practice to use a separate topic for tests.
        # This requires the test topic to be created beforehand.
        # For now, we assume it exists or can be auto-created.
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            consumer_timeout_ms=1000, # End test if no message found
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

    def test_produce_consume(self):
        """Test sending and receiving a message from Kafka."""
        message = {'test_key': 'test_value', 'timestamp': time.time()}
        self.producer.send(self.topic, message)
        self.producer.flush()

        # Poll for the message
        received_message = next(self.consumer)
        
        self.assertIsNotNone(received_message)
        self.assertEqual(received_message.value['test_key'], 'test_value')

    def tearDown(self):
        """Close Kafka connections."""
        self.producer.close()
        self.consumer.close()

if __name__ == '__main__':
    unittest.main()
