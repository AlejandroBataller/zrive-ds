import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import os


def get_config():
    return {
        "input_path": "data/sampled_box_builder_df.csv",
        "model_output_dir": "models/",
        "min_purchase_size": 5,
        "features": ['global_popularity', 'abandoned_before', 'ordered_before', 
                     'set_as_regular', 'normalised_price']
    }


def load_data(path):
    """Easy to change in case we want to read from a DB insted of a CSV."""
    return pd.read_csv(path)


def preprocess_data(df, min_size = 5):
    df['real_purchase_size'] = df.groupby('order_id')['outcome'].transform('sum')
    return df[df['real_purchase_size'] >= min_size].copy()


def train_model(X, y, params):
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', GradientBoostingClassifier(**params, random_state=42))
    ])
    model.fit(X, y)
    return model


def save_model(model, output_dir):
    date_str = datetime.now().strftime("%Y_%m_%d")
    filename = f"push_{date_str}.pkl"
    path = os.path.join(output_dir, filename)
    
    joblib.dump(model, path) #we save the model in the file path
    return path


def handler_fit(event, context = None):
    config = get_config()
    best_params = {
        "n_estimators" : 50,
        "max_depth": 5,
        "learning_rate": 0.1
    }
    params = event.get("model_params", best_params)
    
    data = load_data(config["input_path"])
    clean_data = preprocess_data(data, config["min_purchase_size"])
    
    X = clean_data[config["features"]].fillna(0)
    y = clean_data['outcome']
    
    model = train_model(X, y, params)
    model_path = save_model(model, config["model_output_dir"])
    
    return {
        "statusCode": "200",
        "body": json.dumps({"message": "Training successful", "model_path": model_path})
    }

if __name__ == "__main__":
    event ={
        "model_params" : {
        "n_estimators" : 50,
        "max_depth": 5,
        "learning_rate": 0.1
        }
    }
    result = handler_fit(event, None)
    print("Execution finished correctly")
    print(result)