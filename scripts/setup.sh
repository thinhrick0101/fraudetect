#!/bin/bash
# This script sets up the environment for the fraud detection system.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 1. Start Docker Services ---
echo "Starting all services with Docker Compose..."
docker-compose -f docker/docker-compose.yml up -d
echo "Services started."

# --- 2. Install Python Dependencies ---
# It's recommended to do this in a virtual environment.
echo "Installing Python requirements..."
pip install -r requirements.txt
echo "Dependencies installed."

# --- 3. Create Kafka Topics ---
echo "Waiting for Kafka to be ready..."
# A simple sleep might not be robust enough for a real script.
# More robust solutions involve tools like 'kafka-is-ready' or a loop.
sleep 15

echo "Creating Kafka topics: transactions and validated_transactions..."
docker-compose -f docker/docker-compose.yml exec kafka kafka-topics --create \
  --topic transactions \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 1

docker-compose -f docker/docker-compose.yml exec kafka kafka-topics --create \
  --topic validated_transactions \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 1

echo "Kafka topics created successfully."

echo "Setup complete. The environment is ready."
