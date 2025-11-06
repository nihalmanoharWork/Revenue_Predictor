import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Revenue Prediction Dashboard", layout="wide")

st.title("📈 Revenue Prediction Dashboard")

DATA_PATH = "data/predictions.csv"

@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv(DATA_PATH)

try:
    df = load_data()
    st.success("✅ Data loaded successfully!")
except FileNotFoundError:
    st.error("❌ predictions.csv not found. Please run the pipeline first.")
    st.stop()

# KPIs
latest_revenue = df["predicted_revenue"].iloc[-1]
avg_revenue = df["predicted_revenue"].mean()
max_revenue = df["predicted_revenue"].max()

col1, col2, col3 = st.columns(3)
col1.metric("Latest Predicted Revenue", f"${latest_revenue:,.2f}")
col2.metric("Average Predicted Revenue", f"${avg_revenue:,.2f}")
col3.metric("Max Predicted Revenue", f"${max_revenue:,.2f}")

st.divider()

st.subheader("Revenue Predictions Over Time")
if "date" in df.columns:
    st.line_chart(df.set_index("date")["predicted_revenue"])
else:
    st.line_chart(df["predicted_revenue"])

st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
