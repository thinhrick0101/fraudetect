# Real-Time Fraud Detection System

This project is a comprehensive, real-time fraud detection system utilizing a modern stack of open-source technologies. It is designed to ingest, process, and analyze transaction data in real-time to identify and flag potentially fraudulent activities.

## Architecture Overview

The system follows a distributed, microservices-oriented architecture.

```
Transaction Stream --> Kafka --> Flink (Validation & Preprocessing) --> Kafka
   |
   +--> Spark (Batch Feature Engineering) --> Redis (Online Store)
   |
   +--> Ray/MLflow (Model Training/Tuning) --> MLflow Model Registry
           |
           +--> Flask API (Real-time Inference)
                 |
                 +--> Redis (Feature Retrieval)
                 +--> MLflow Model (Inference)
```

### Core Components:

*   **Kafka**: Acts as the central nervous system of the platform, providing a high-throughput, distributed message bus for real-time data streams.
*   **Flink**: Provides real-time stream processing capabilities for data validation, enrichment, and simple transformations on the incoming transaction stream.
*   **Spark**: Used for large-scale batch processing to generate historical features from validated transaction data.
*   **Redis**: Serves as a low-latency online feature store, making user-level features available to the inference service in real-time.
*   **Ray**: A distributed execution framework used to scale up model training and hyperparameter tuning.
*   **MLflow**: Manages the end-to-end machine learning lifecycle, including experiment tracking, model packaging, and a model registry for versioning and deployment.
*   **Flask Service**: A lightweight web service that exposes a REST API for real-time fraud predictions.

## Project Structure

```
fraudetect/
│
├── docker/
│   ├── docker-compose.yml
│   └── Dockerfile
├── kafka/
│   ├── producer.py
│   └── consumer.py
├── flink/
│   ├── transaction_validation.py
│   └── utils.py
├── spark/
│   ├── feature_engineering.py
│   └── spark_submit.sh
├── ray_mlflow/
│   ├── train.py
│   └── model_utils.py
├── inference_service/
│   ├── app.py
│   └── requirements.txt
├── ... (and other directories)
```

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   Python 3.8+
*   An environment to run the services (local machine, cloud VMs, Kubernetes).

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd fraud-detection-system
    ```
2.  **Configure Environment:**
    Update the configuration files in `configs/` to match your environment (e.g., Kafka brokers, Redis host).
3.  **Build and Start Services:**
    Use the provided `docker-compose.yml` to start all the infrastructure components.
    ```bash
    docker-compose up -d
    ```
4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Start Data Producer:**
    Run the Kafka producer to simulate a stream of transactions.
    ```bash
    python kafka/producer.py
    ```
2.  **Submit Flink Job:**
    Deploy the Flink job to start validating transactions.
    ```bash
    # (Instructions on how to submit a PyFlink job)
    ```
3.  **Run Spark Batch Job:**
    Execute the Spark job to generate features.
    ```bash
    # (Instructions on how to submit a PySpark job)
    ```
4.  **Train a Model:**
    Run the training script to train and register a model with MLflow.
    ```bash
    python ray_mlflow/train.py
    ```
5.  **Start Inference Service:**
    Launch the Flask API to serve predictions.
    ```bash
    python inference_service/app.py
    ```
---
This README provides a high-level overview. For more detailed information on each component, refer to the respective directories.
