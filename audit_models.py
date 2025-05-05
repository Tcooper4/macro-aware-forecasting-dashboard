from utils.common import fetch_price_data
from models.lstm_model import audit_lstm_accuracy
from models.ml_models import audit_ml_accuracy

ticker = "AAPL"
df = fetch_price_data(ticker, start_date="2018-01-01", end_date="2023-12-31")

print("🔍 LSTM Accuracy Audit")
print(audit_lstm_accuracy(ticker, df))

print("\n🔍 XGBoost/ML Accuracy Audit")
print(audit_ml_accuracy(df))
