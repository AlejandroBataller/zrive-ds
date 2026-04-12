import os
import pandas as pd
import joblib 
import logging 
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from datetime import datetime


# CONFIG
FEATURES = ['global_popularity', 'abandoned_before', 'ordered_before']
RIDGE_Cs = [1e-8, 1e-6, 1e-4, 1e-2]


# UTILS
def push_relevant_dataframe(df: pd.DataFrame, min_products: int = 5) -> pd.DataFrame:
    df = df.copy()
    df['real_purchase_size'] = df.groupby('order_id')['outcome'].transform('sum')
    return df[df['real_purchase_size'] >= min_products]


def format_data_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    return df


# TRAIN
def train_production_model():

    # 1. Load data
    df = pd.read_csv('data/sampled_box_builder_df.csv')

    # 2. Preprocessing
    df = (
        df
        .pipe(push_relevant_dataframe)
        .pipe(format_data_columns)
        .sort_values('order_date')
    )

    # 3. Split
    daily_orders = df.groupby("order_date").order_id.nunique()
    cumsum_daily_orders = daily_orders.cumsum() / daily_orders.sum()

    train_val_cutoff = cumsum_daily_orders[cumsum_daily_orders <= 0.8].idxmax()

    df_train = df[df.order_date <= train_val_cutoff]
    df_val = df[df.order_date > train_val_cutoff]
    
    X_train = df_train[FEATURES].fillna(0)
    y_train = df_train['outcome']

    X_val = df_val[FEATURES].fillna(0)
    y_val = df_val['outcome']
   
    # 4. Model selection
    best_auc = -1
    best_c = None
    best_model = None

    for c in RIDGE_Cs:
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                penalty='l2',
                C=c,
                class_weight='balanced',
                random_state=42,
                max_iter=1000
            )
        )

        model.fit(X_train, y_train)

        val_proba = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, val_proba)

        logging.info(f"C={c} → AUC={auc:.4f}")

        if auc > best_auc:
            best_auc = auc
            best_c = c
            best_model = model

    logging.info(f"\nBest C: {best_c} | Best AUC: {best_auc:.4f}")

    # 5. Save model
    os.makedirs("models", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    model_path = f'models/push_model_linear_{timestamp}.joblib'

    joblib.dump(best_model, model_path)

    logging.info(f"Model save in: {model_path}")

    return model_path


if __name__ == "__main__":
    train_production_model()