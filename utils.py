import pandas as pd

def extract_date_features(df, date_col="date"):
    """Extract month and day_of_week features from a date column."""
    dates = pd.to_datetime(df[date_col], errors='coerce')
    return pd.DataFrame({
        "month": dates.dt.month.fillna(0).astype(int),
        "day_of_week": dates.dt.dayofweek.fillna(0).astype(int)
    })

def date_feature_extractor(df):
    """Wrapper function for sklearn FunctionTransformer (needed for pickling)."""
    date_col = df.columns[0] if hasattr(df, "columns") else "date"
    return extract_date_features(df, date_col)
