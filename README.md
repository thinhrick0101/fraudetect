# Real-Time Fraud Detection System

This project is a comprehensive, real-time fraud detection system utilizing a modern stack of open-source technologies. It is designed to ingest, process, and analyze transaction data in real-time to identify and flag potentially fraudulent activities.

## Architecture Overview

The system follows a distributed, streaming-first architecture.

```
Transaction Stream -> Kafka -> Flink (Validation & Enrichment) -> Kafka
                               |
                               +-> Spark (Streaming Feature Engineering) -> Redis (Online Store)
                               |                                           |
                               |                                           +-> Parquet (Offline Training Data)
                               |
                               +-> Ray/MLflow (Model Training) -> MLflow Model Registry
                                     |
                                     +-> Flask API (Real-time Inference) -> Prometheus & Grafana
                                           |
                                           +-> Redis (Feature Retrieval)
                                           +-> MLflow Model (Inference)
```

### Core Components:

*   **Kafka**: The central message bus for real-time data streams (`transactions` and `validated_transactions` topics).
*   **Flink**: Provides real-time stream processing for data validation and enrichment (e.g., flagging suspicious amounts).
*   **Spark**: Runs a Structured Streaming job to generate user-level features from the validated transaction stream.
*   **Redis**: Serves as a low-latency online feature store for real-time inference.
*   **Parquet Files**: Historical features are persisted to disk in `data/processed/features` to be used as a training dataset.
*   **Ray**: A distributed execution framework used to scale up model training and hyperparameter tuning.
*   **MLflow**: Manages the end-to-end machine learning lifecycle, including experiment tracking and a model registry.
*   **Flask Service**: A lightweight, instrumented web service that exposes a REST API for real-time fraud predictions.
*   **Prometheus**: Scrapes metrics from the inference service to monitor its health and performance.
*   **Grafana**: Provides pre-built dashboards to visualize the metrics collected by Prometheus.

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   Python 3.8+ and `pip`

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd frauddetect
    ```
2.  **Run the setup script:**
    This script will start all Docker services (Kafka, Spark, Redis, etc.) and create the necessary Kafka topics.
    ```bash
    bash scripts/setup.sh
    ```
    You can check the status of the running containers with `docker-compose -f docker/docker-compose.yml ps`.

## How to Run the Full Pipeline

After running the setup script, open multiple terminal windows to run each component.

1.  **Start the Spark Feature Engineering Job:**
    This job will listen for validated transactions and update features in Redis and Parquet.
    ```bash
    python spark/feature_engineering.py
    ```

2.  **Start the Flink Validation Job:**
    This job will listen for raw transactions, validate/enrich them, and send them to the next topic.
    ```bash
    python flink/transaction_validation.py
    ```
    
3.  **Start the Kafka Producer:**
    This script simulates a stream of new transactions.
    ```bash
    python kafka/producer.py
    ```
    
    *At this point, you have a live data pipeline. You should see output in the Spark terminal as it processes batches.*

4.  **(Optional) Train a New Model:**
    If you've let the pipeline run for a while to generate some training data, you can train a new model.
    ```bash
    python ray_mlflow/train.py
    ```

5.  **Start the Inference Service:**
    This launches the API that serves predictions.
    ```bash
    python inference_service/app.py
    ```

## Accessing Services

*   **Spark UI**: `http://localhost:8080`
*   **Flink UI**: `http://localhost:8081`
*   **MLflow UI**: `http://localhost:5000`
*   **Prometheus UI**: `http://localhost:9090`
*   **Grafana UI**: `http://localhost:3000` (user: `admin`, pass: `admin`)

## Tearing Down

To stop all services and remove the containers and volumes, run the teardown script:
```bash
bash scripts/teardown.sh
```
---
This README provides a high-level overview. For more detailed information on each component, refer to the respective directories.
