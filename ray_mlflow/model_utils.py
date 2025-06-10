import mlflow
import yaml

def load_config(config_path='configs/mlflow_config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_mlflow():
    """
    Sets up the MLflow tracking URI and experiment.
    """
    config = load_config()
    mlflow.set_tracking_uri(config['tracking_uri'])
    mlflow.set_experiment(config['experiment_name'])
    return config['model_name']

def register_best_model(analysis, model_name):
    """
    Finds the best run from a Ray Tune analysis and registers the model
    in the MLflow Model Registry.
    """
    best_run = analysis.get_best_run(metric="accuracy", mode="max")
    if best_run:
        best_model_uri = f"runs:/{best_run.run_id}/fraud_detection_model"
        mlflow.register_model(model_uri=best_model_uri, name=model_name)
        print(f"Registered model '{model_name}' from run '{best_run.run_id}'")
        return True
    print("Could not find a best run to register.")
    return False
