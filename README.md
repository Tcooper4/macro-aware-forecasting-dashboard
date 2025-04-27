# 🧠 Macro-Aware Quant Forecasting Dashboard

This project combines real-time market and macroeconomic data with advanced forecasting models (ARIMA, GARCH, HMM) and an interactive Streamlit dashboard.

## ✨ Features

- Real-time data ingestion from Yahoo Finance and FRED
- Forecasting engine with ARIMA, GARCH, and Hidden Markov Models
- Confidence intervals and volatility-based risk scoring
- Automated trade recommendations (Buy, Sell, Hold)
- Option trading suggestions based on forecast trends
- Top 3 trade ideas highlighted daily
- Downloadable trade recommendation summaries (CSV)
- Weekly data refresh via GitHub Actions

## 📂 Project Structure

- `src/` - Feature engineering, macroeconomic API calls, modeling tools
- `notebooks/` - Jupyter notebooks for exploratory modeling
- `streamlit_app/dashboard.py` - Main forecasting dashboard
- `streamlit_app/trade_recommendations.py` - Daily trade recommendation engine
- `.github/workflows/refresh.yml` - Weekly automation setup
- `.env.example` - Environment variable template (FRED API key)

## 🚀 Quickstart

```bash
pip install -r requirements.txt
streamlit run streamlit_app/dashboard.py
# OR
streamlit run streamlit_app/trade_recommendations.py
