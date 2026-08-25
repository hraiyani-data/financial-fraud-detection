import pandas as pd
import pickle
import time
import datetime
import sqlite3


with open('models/logistic_regression_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('models/feature_columns.pkl', 'rb') as f:
    feature_cols = pickle.load(f)

print("Model loaded successfully. Starting stream simulation...\n")

def check_and_alert(transaction_id, fraud_probability, threshold=0.5):
    if fraud_probability >= threshold:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_msg = f"[{timestamp}] ALERT! Transaction {transaction_id} flagged as FRAUD (probability: {fraud_probability:.2%})"
        print(alert_msg)
        with open('outputs/fraud_alerts.log', 'a') as f:
            f.write(alert_msg + '\n')
        return alert_msg
    else:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Transaction {transaction_id} - OK (probability: {fraud_probability:.2%})")
        return None

conn = sqlite3.connect('database/fraud_detection.db')
stream_data = pd.read_sql('SELECT * FROM transactions LIMIT 50', conn)
conn.close()

print(f"Loaded {len(stream_data)} transactions for streaming simulation.\n")


print("--- Live Transaction Stream ---\n")

for idx, row in stream_data.iterrows():
    transaction_id = row['Transaction_ID']
    features = pd.DataFrame([row[feature_cols]], columns=feature_cols)
    
    fraud_prob = model.predict_proba(features)[0][1]
    
    check_and_alert(transaction_id, fraud_prob)
    
    time.sleep(1)

print("\n--- Stream simulation complete ---")