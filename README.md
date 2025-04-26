# 🧠 Macro-Aware Quant Forecasting Dashboard

This project combines real-time market and macroeconomic data with forecasting models (ARIMA, GARCH, HMM) and an interactive dashboard using Streamlit.

## 📂 Structure

- `src/` - Feature engineering, macro API, modeling tools
- `notebooks/` - Jupyter notebooks for modeling
- `streamlit_app/dashboard.py` - Interactive forecasting dashboard
- `.github/workflows/refresh.yml` - Weekly automation via GitHub Actions
- `.env.example` - Environment variable template (do not commit real keys)

## 🚀 Quickstart

```bash
pip install -r requirements.txt
streamlit run streamlit_app/dashboard.py
```

## 🌐 Deployment

- Connect this repo to [Streamlit Cloud](https://streamlit.io/cloud)
- Add your FRED API key to Streamlit secrets:

```
FRED_API_KEY=your_key_here
```

## 🔁 Automation

Data is refreshed weekly using GitHub Actions.

---

Made with 💻 by [Tcooper4](https://github.com/Tcooper4)
