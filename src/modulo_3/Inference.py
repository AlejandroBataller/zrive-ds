import pandas as pd
import joblib
import logging
import argparse


# MAIN
def run_inference(model_path: str, input_path: str, output_path: str):

    # 1. Load model
    model = joblib.load(model_path)
    logging.info(f"Model load from: {model_path}")

    # 2. load new data 
    df = pd.read_csv(input_path)

    FEATURES = ['global_popularity', 'abandoned_before', 'ordered_before']

    X = df[FEATURES].fillna(0)

    # 3. Prediction
    preds = model.predict_proba(X)[:, 1]

    # 4. Save results
    output_df = df.copy()
    output_df['prediction'] = preds

    output_df.to_csv(output_path, index=False)

    logging.info(f"Predictions save in: {output_path}")


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_path", type=str, required=True, help="Ruta al modelo .joblib")
    parser.add_argument("--input_path", type=str, required=True, help="CSV de entrada")
    parser.add_argument("--output_path", type=str, required=True, help="CSV de salida")

    args = parser.parse_args()

    run_inference(
        model_path=args.model_path,
        input_path=args.input_path,
        output_path=args.output_path
    )