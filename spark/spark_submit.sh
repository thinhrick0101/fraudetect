#!/bin/bash
# This script is an example of how to submit the Spark streaming job
# to the standalone cluster running in Docker.

# --- Variables ---
SPARK_MASTER="spark://localhost:7077"
APP_NAME="FraudDetectionStreaming"
PYTHON_FILE="spark/feature_engineering.py"

# Required JARs for Kafka and Redis connectors.
# These versions should be compatible with your Spark version (3.3.0 in this case).
JARS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.redislabs:spark-redis_2.12:3.2.0"

# --- Zipping project files ---
# Spark needs access to your utility and config files on all nodes.
# A common way to do this is to zip them and send them with --py-files.
echo "Zipping python modules for Spark..."
zip -r frauddetect.zip configs/ spark/

# --- Spark Submit Command ---
echo "Submitting Spark job..."
spark-submit \
  --master $SPARK_MASTER \
  --name $APP_NAME \
  $JARS \
  --py-files frauddetect.zip \
  $PYTHON_FILE

# Clean up the zip file after submission
echo "Cleaning up..."
rm frauddetect.zip

echo "Job submitted."
