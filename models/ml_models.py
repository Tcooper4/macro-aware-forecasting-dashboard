from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
import numpy as np

def prepare_ml_data(df):
    df = df.dropna().copy()
    df["Target"] = np.where(df["Close"].shift(-1) > df["Close"], 1, 0)
    X = df.drop(columns=["Target", "Close"])
    y = df["Target"]
    return X, y

def predict_xgboost(X_train, y_train, X_test):
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    return model.predict(X_test)[-1], model.predict_proba(X_test)[-1][1]

def predict_random_forest(X_train, y_train, X_test):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model.predict(X_test)[-1], model.predict_proba(X_test)[-1][1]

def predict_logistic(X_train, y_train, X_test):
    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model.predict(X_test)[-1], model.predict_proba(X_test)[-1][1]
