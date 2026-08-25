import streamlit as st
import pandas as pd
import sqlite3
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")

st.title("Financial Fraud Detection Dashboard")
st.markdown("Real-time monitoring of transaction fraud risk")

@st.cache_data
def load_data():
    conn = sqlite3.connect('database/fraud_detection.db')
    data = pd.read_sql('SELECT * FROM transactions', conn)
    conn.close()
    return data

df = load_data()

total_transactions = len(df)
total_fraud = df['Fraudulent'].sum()
fraud_rate = (total_fraud / total_transactions) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", f"{total_transactions:,}")
col2.metric("Fraud Cases", f"{total_fraud:,}")
col3.metric("Fraud Rate", f"{fraud_rate:.2f}%")

st.sidebar.header("Filters")
selected_location = st.sidebar.multiselect(
    "Select Location(s)",
    options=df['Location'].unique(),
    default=df['Location'].unique()
)

filtered_df = df[df['Location'].isin(selected_location)]

st.subheader("Fraud Rate by Location")
location_fraud = filtered_df.groupby('Location')['Fraudulent'].mean().sort_values(ascending=False)
st.bar_chart(location_fraud)

st.subheader("Fraud Rate by Hour of Day")
filtered_df['Hour'] = pd.to_datetime(filtered_df['Transaction_Date']).dt.hour

fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(x='Hour', y='Fraudulent', data=filtered_df, estimator='mean', ax=ax)
ax.set_xlabel('Hour')
ax.set_ylabel('Fraud Rate')
ax.set_title('Fraud Rate by Hour of Day')
st.pyplot(fig)

st.subheader("Recent Fraud Alerts (Log)")
try:
    with open('outputs/fraud_alerts.log', 'r') as f:
        alerts = f.readlines()
    st.text_area("Alert Log", value=''.join(alerts[-10:]), height=200)
except FileNotFoundError:
    st.info("No alerts logged yet. Run the stream simulator first.")

st.subheader("Transaction Data")
st.dataframe(filtered_df.head(100))