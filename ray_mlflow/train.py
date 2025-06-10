import ray
import mlflow
from ray import tune
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np

def load_data():
    # This is a placeholder for loading your actual training data.
    # In a real project, you would load data from a file or a data store like S3 or a feature store.
    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)
    return train_test_split(X, y, test_size=0.2)

def train_model(config):
    # MLflow tracking is managed by Ray Tune's `MLflowLoggerCallback`
    X_train, X_test, y_train, y_test = load_data()
    
    model = RandomForestClassifier(
        n_estimators=config["n_estimators"],
        max_depth=config["max_depth"]
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    
    # Log parameters and metrics to MLflow
    mlflow.log_param("n_estimators", config["n_estimators"])
    mlflow.log_param("max_depth", config["max_depth"])
    mlflow.log_metric("accuracy", accuracy)
    
    # Log the model to MLflow
    mlflow.sklearn.log_model(model, "fraud_detection_model")
    
    # Report metrics to Ray Tune
    tune.report(accuracy=accuracy)

def main():
    # Set the MLflow tracking URI. You would have an MLflow server running.
    # For local testing, it can write to a local `mlruns` directory.
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("fraud_detection_training")

    ray.init(ignore_reinit_error=True)

    # Define the hyperparameter search space for Ray Tune
    search_space = {
        "n_estimators": tune.grid_search([50, 100, 150]),
        "max_depth": tune.choice([10, 20, 30])
    }

    # Run the hyperparameter tuning job
    analysis = tune.run(
        train_model,
        config=search_space,
        metric="accuracy",
        mode="max",
        num_samples=1, # In a real run, you'd use more samples
        resources_per_trial={'cpu': 1, 'gpu': 0}
    )

    print("Best hyperparameters found were: ", analysis.best_config)
    
    # Register the best model in the MLflow Model Registry
    best_run = analysis.get_best_run(metric="accuracy", mode="max")
    if best_run:
        best_model_uri = f"runs:/{best_run.run_id}/fraud_detection_model"
        model_name = "fraud_detection_model"
        mlflow.register_model(model_uri=best_model_uri, name=model_name)
        print(f"Registered model '{model_name}' from run '{best_run.run_id}'")

    ray.shutdown()

if __name__ == "__main__":
    main()
