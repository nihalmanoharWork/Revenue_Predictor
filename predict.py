# predict.py
import argparse
import pandas as pd
import joblib
import yaml
import os


def load_pipeline(path):
    """Load trained ML pipeline."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}")
    print(f"Loading model from {path} ...")
    return joblib.load(path)


def main():
    parser = argparse.ArgumentParser(description="Run revenue prediction")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config file")
    parser.add_argument("--input", default=None, help="Path to new CSV data for prediction")
    parser.add_argument("--model", default="models/revenue_model.joblib", help="Path to trained model")
    parser.add_argument("--output", default="data/predictions.csv", help="Output CSV for predictions")
    parser.add_argument("--single", action="store_true", help="Enable single prediction mode")
    parser.add_argument("--data", nargs="+", help="Single input feature values (in config order)")
    args = parser.parse_args()

    # Load config & model
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    pipeline = load_pipeline(args.model)
    features = cfg["features"]["numeric"] + cfg["features"]["categorical"] + cfg["features"].get("date", [])

    if args.single:
        # Single record prediction mode
        if not args.data:
            raise ValueError("In single mode, you must provide --data values.")
        df = pd.DataFrame([args.data], columns=features)
        pred = pipeline.predict(df)[0]
        print(f"Predicted revenue: {pred:.2f}")
        return

    # Batch mode
    if not args.input:
        raise ValueError("Please provide --input CSV for batch prediction.")
    print(f"Loading input data from {args.input} ...")

    df = pd.read_csv(args.input)
    for c in features:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    preds = pipeline.predict(df[features])
    df["predicted_revenue"] = preds

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"Predictions saved to {args.output}")


if __name__ == "__main__":
    main()
