import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Revenue Prediction Dashboard", layout="wide")
st.title("📈 Revenue Prediction Dashboard")

# ----------------------------
# Utility to get the latest CSV
# ----------------------------
def get_latest_csv(folder="data", pattern="predictions.csv"):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(pattern)]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

# ----------------------------
# Load Latest Predictions Data
# ----------------------------
latest_csv = get_latest_csv()
if not latest_csv:
    st.error("❌ predictions.csv not found. Please run the pipeline first.")
    st.stop()

@st.cache_data(ttl=3600)
def load_data(path):
    return pd.read_csv(path)

df = load_data(latest_csv)
st.success(f"✅ Data loaded from {latest_csv}")

# ----------------------------
# Optional: Load latest revenue_data.csv
# ----------------------------
latest_revenue_csv = get_latest_csv(pattern="revenue_data.csv")
df_revenue = None
if latest_revenue_csv:
    df_revenue = pd.read_csv(latest_revenue_csv)

# ----------------------------
# KPIs
# ----------------------------
latest_revenue = df["predicted_revenue"].iloc[-1]
avg_revenue = df["predicted_revenue"].mean()
max_revenue = df["predicted_revenue"].max()
min_revenue = df["predicted_revenue"].min()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Predicted Revenue", f"${latest_revenue:,.2f}")
col2.metric("Average Predicted Revenue", f"${avg_revenue:,.2f}")
col3.metric("Max Predicted Revenue", f"${max_revenue:,.2f}")
col4.metric("Min Predicted Revenue", f"${min_revenue:,.2f}")

st.divider()

# ----------------------------
# Chart: Predicted Revenue Over Time
# ----------------------------
st.subheader("Revenue Predictions Over Time")
if "date" in df.columns:
    st.line_chart(df.set_index("date")["predicted_revenue"])
else:
    st.line_chart(df["predicted_revenue"])

# ----------------------------
# Optional: Chart from revenue_data.csv
# ----------------------------
if df_revenue is not None:
    st.subheader("Original Revenue Data Over Time")
    if "date" in df_revenue.columns:
        st.line_chart(df_revenue.set_index("date")["revenue"])
    else:
        st.line_chart(df_revenue["revenue"])
    st.caption(f"Data source: {latest_revenue_csv}")

# ----------------------------
# Last Updated
# ----------------------------
st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# ----------------------------
# Optional: Auto-refresh every 10 mins
# ----------------------------
# Uncomment the next two lines to enable auto-refresh
# import streamlit as st
# st.experimental_rerun()  # Note: Use with caution; will rerun every time page reloads
