import streamlit as st
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["ad_analytics"]
collection = db["campaign_metrics"]

st.set_page_config(page_title="Ad Campaign Dashboard", layout="wide")
st.title("📊 Ad Campaign Analytics Dashboard")

# Load data
data = list(collection.find({}, {"_id": 0}))
if not data:
    st.warning("No data found in MongoDB.")
    st.stop()

df = pd.DataFrame(data)

# Add missing columns if needed
for col in ["device", "location", "ctr", "cvr", "clicks", "conversions", "revenue"]:
    if col not in df.columns:
        df[col] = 0

# Sidebar filters
st.sidebar.header("📌 Filters")
campaigns = st.sidebar.multiselect("Campaign ID", df["campaign_id"].unique(), default=df["campaign_id"].unique())
devices = st.sidebar.multiselect("Device", df["device"].unique(), default=df["device"].unique())
locations = st.sidebar.multiselect("Location", df["location"].unique(), default=df["location"].unique())

# Filter data
filtered_df = df[
    (df["campaign_id"].isin(campaigns)) &
    (df["device"].isin(devices)) &
    (df["location"].isin(locations))
]

# KPIs
st.markdown("## 🧮 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Clicks", int(filtered_df["clicks"].sum()))
col2.metric("Total Conversions", int(filtered_df["conversions"].sum()))
col3.metric("Total Revenue", f"${filtered_df['revenue'].sum():.2f}")
col4.metric("Avg. CVR", f"{filtered_df['cvr'].mean() * 100:.2f}%")

# Charts
st.markdown("## 📊 Metrics Breakdown")

tab1, tab2, tab3 = st.tabs(["CTR by Ad", "Revenue by Ad", "CVR by Ad"])
with tab1:
    st.bar_chart(filtered_df.set_index("ad_id")["ctr"])

with tab2:
    st.bar_chart(filtered_df.set_index("ad_id")["revenue"])

with tab3:
    st.bar_chart(filtered_df.set_index("ad_id")["cvr"])

# Detailed Table
st.markdown("## 🧾 Detailed Metrics")
st.dataframe(filtered_df, use_container_width=True)

# Export to CSV
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Export CSV", csv, "campaign_metrics.csv", "text/csv")
