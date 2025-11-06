import yaml
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from lightgbm import LGBMRegressor
import json
import argparse

# Import date feature functions from utils.py
from utils import extract_date_features, date_feature_extractor


# ==========================================================
#  Utility Functions
# ==========================================================

def load_config(path="config.yaml"):
    """Load configuration YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def make_feature_transformer(numeric_cols, categorical_cols, date_cols):
    """
    Build preprocessing pipelines for numeric, categorical, and date columns.
    Uses ColumnTransformer to apply different transformations to each type.
    """
    # Numeric pipeline
    num_pipeline = Pipeline([
        ("scale", StandardScaler())
    ])

    # Categorical pipeline
    cat_pipeline = Pipeline([
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    # Date pipeline (extract month/day, then scale)
    date_pipeline = Pipeline([
        ("date_extract", FunctionTransformer(date_feature_extractor, validate=False)),
        ("scale", StandardScaler())
    ])

    # Combine all transformations
    preprocessor = ColumnTransformer(transformers=[
        ("num", num_pipeline, numeric_cols),
        ("cat", cat_pipeline, categorical_cols),
        ("date", date_pipeline, date_cols)
    ], remainder="drop", sparse_threshold=0)

    return preprocessor


# ==========================================================
#  Main Training Pipeline
# ==========================================================

def main(cfg_path="config.yaml", out_model_path=None):
    """Main entry point for model training."""
    # Load YAML config
    cfg = load_config(cfg_path)

    # Read data-related parameters
    data_path = cfg["data"]["path"]
    target = cfg["data"]["target"]
    test_size = cfg["data"].get("test_size", 0.2)
    random_state = cfg["data"].get("random_state", 42)

    # Load dataset
    df = pd.read_csv(data_path)
    df = df.dropna(subset=[target]).reset_index(drop=True)

    # Feature lists from config
    numeric_cols = cfg["features"]["numeric"]
    categorical_cols = cfg["features"]["categorical"]
    date_cols = cfg["features"].get("date", [])

    # Validate all required columns exist
    for c in numeric_cols + categorical_cols + date_cols + [target]:
        if c not in df.columns:
            raise ValueError(f"Column '{c}' not found in data")

    # Separate features and target
    X = df[numeric_cols + categorical_cols + date_cols]
    y = df[target]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Create preprocessor
    preprocessor = make_feature_transformer(numeric_cols, categorical_cols, date_cols)

    # Initialize model (LightGBM - DART boosting)
    model_params = cfg["model"]["params"]
    lgb = LGBMRegressor(**model_params)

    # Full pipeline
    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("model", lgb)
    ])

    print("Training model — this may take a while depending on data size...")
    pipeline.fit(X_train, y_train)

    # ==========================================================
    #  Evaluation
    # ==========================================================
    preds = pipeline.predict(X_test)

    # Robust metric computation (backward-compatible)
    mse = mean_squared_error(y_test, preds)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print("\nModel Evaluation Metrics:")
    print(f" - MSE : {mse:.2f}")
    print(f" - RMSE: {rmse:.2f}")
    print(f" - MAE : {mae:.2f}")
    print(f" - R²  : {r2:.4f}\n")

    # ==========================================================
    #  Save model and feature info
    # ==========================================================
    out_model_path = out_model_path or cfg["pipeline"]["output_model_path"]
    os.makedirs(os.path.dirname(out_model_path), exist_ok=True)

    joblib.dump(pipeline, out_model_path)
    print(f"Saved trained pipeline to: {out_model_path}")

    # Save feature info for reproducibility
    feat_info = {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "date": date_cols
    }
    feat_file = cfg["pipeline"].get("save_features_file", "models/feature_columns.json")
    with open(feat_file, "w") as f:
        json.dump(feat_info, f, indent=2)

    print(f"Saved feature metadata to: {feat_file}")


# ==========================================================
#  CLI Entry Point
# ==========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a LightGBM DART model for revenue prediction.")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML file")
    parser.add_argument("--out", default=None, help="Optional path to save trained model")
    args = parser.parse_args()

    main(cfg_path=args.config, out_model_path=args.out)
