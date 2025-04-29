# 🧠 Macro-Aware Quant Forecasting Dashboard

This project combines real-time market and macroeconomic data with advanced forecasting models and an interactive Streamlit dashboard designed to provide actionable trade ideas and portfolio optimization.

## ✨ Features

- Real-time data ingestion from **Yahoo Finance**, **FRED**, and **MarketWatch**
- Forecasting engine with:
  - ARIMA
  - GARCH (coming soon)
  - Hidden Markov Models (HMM)
  - Exponential Smoothing
  - Facebook Prophet
  - SARIMA
  - LSTM Neural Networks
  - Hybrid model averaging (e.g., ARIMA + Prophet)
- Confidence intervals, volatility scoring, and expected return projection
- Automated trade recommendations: **Buy**, **Sell**, **Hold** signals
- Portfolio optimization using **Sharpe Ratio** maximization
- Efficient Frontier chart and interactive risk-return visualization
- Macro regime and market sentiment overlay (VIX, Put/Call Ratio, AAII sentiment)
- Strategy recommendations aligned to current macro environment
- Custom model selection by complexity (Simple → Elite)
- Downloadable trade summaries (coming soon)
- Weekly refresh via GitHub Actions

## 📂 Project Structure

- `dashboard.py` – Main app entry point
- `pages/trade_recommendations.py` – Multi-model trade forecasting
- `pages/macro_dashboard.py` – Macro data + Put/Call sentiment
- `pages/macro_sentiment_dashboard.py` – VIX + market fear gauge
- `pages/portfolio_dashboard.py` – Portfolio optimizer with efficient frontier
- `utils.py` – Navigation and layout components
- `forecast_engine.py` – Core modeling engine
- `refresh.yml` – GitHub Action for weekly updates
- `.env.example` – Template for API keys (FRED)

## 🚀 Quickstart

```bash
# Step 1: Clone the repo
https://github.com/Tcooper4/macro-aware-forecasting-dashboard.git

# Step 2: Navigate into the project
cd macro-aware-forecasting-dashboard

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Add your FRED API key
cp .env.example .env
# Then edit .env to include your key:
# FRED_API_KEY=your_actual_key_here

# Step 5: Run the app
streamlit run dashboard.py
```

## 🧠 Why This Matters

This platform helps individual and institutional users:

- Detect high-confidence trading opportunities using advanced statistical models
- Visualize risk-adjusted portfolio allocations
- Align investment strategies with macroeconomic signals
- Build model-driven trading discipline

## 🧪 In Progress

- GARCH and HMM modeling integrations
- Strategy backtesting and expected return scoring
- PDF/CSV export of recommendations

---

Built and maintained by [Tcooper4](https://github.com/Tcooper4) — Pull requests welcome!
