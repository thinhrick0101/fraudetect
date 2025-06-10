import redis
import yaml

def load_config(config_path='configs/redis_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_redis_client():
    """
    Initializes and returns a Redis client.
    """
    config = load_config()
    try:
        client = redis.Redis(
            host=config['host'],
            port=config['port'],
            db=config['db'],
            decode_responses=True
        )
        client.ping()
        print("Successfully connected to Redis.")
        return client
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        return None
