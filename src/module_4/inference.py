import json
import joblib
import pandas as pd
import glob
import os

class PushModelInference: 
    def __init__(self, model_path):
        self.model = joblib.load(model_path)
        # Imputation of missing values strategy
        self.imputation_values = {
            'global_popularity': 0,
            'abandoned_before': 0,
            'ordered_before': 0,
            'set_as_regular': 0,
            'normalised_price': 0.0
        }

    def preprocess(self, df):
        """Apply the imputation and prepare the DataFrame for the model."""
        # We only impute the columns we know, with specific values.
        for col, value in self.imputation_values.items():
            if col in df.columns:
                df[col] = df[col].fillna(value)
        return df

    def predict(self, data):
        return self.model.predict_proba(data)[:, 1]

def handler_predict(event, _):
    # 1. load the data
    users_data = json.loads(event["users"])
    data_to_predict = pd.DataFrame.from_dict(users_data, orient='index')
    
    # 2. Model Configuration and Loading (using the latest version)
    model_files = glob.glob('models/*.pkl') # returns all the files .pkl inside the folder models
    if not model_files:
        return {"statusCode": "404", "body": json.dumps({"error": "No model found"})}
    latest_model = max(model_files, key=os.path.getctime)
    
    # 3. Encapsulation in the class
    engine = PushModelInference(latest_model)
    
    # 4. Processing and Prediction
    clean_data = engine.preprocess(data_to_predict)
    predictions = engine.predict(clean_data)
    
    results = dict(zip(data_to_predict.index, predictions.tolist()))
    
    return {
        "statusCode": "200",
        "body": json.dumps({"prediction": results})
    }

if __name__ == "__main__":
    # Simulating an input event (the same as the one the API would receive in production)
    # We must simulate the structure {"user_id": {"feature": value, ...}}
    mock_event = {
        "users": json.dumps({
            "user_001": {
                "global_popularity": 0.8, 
                "abandoned_before": 0, 
                "ordered_before": 1, 
                "set_as_regular": 0, 
                "normalised_price": 5.5
            },
            "user_002": {
                "global_popularity": 0.1, 
                "abandoned_before": 1, 
                "ordered_before": 0, 
                "set_as_regular": 0, 
                "normalised_price": 2.0
            }
        })
    }
    
    result = handler_predict(mock_event)
    print("Inference result:")
    print(result)