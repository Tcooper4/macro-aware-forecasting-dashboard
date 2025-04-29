import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from utils import navigation_bar

st.set_page_config(page_title="Portfolio Optimizer", layout="wide")
navigation_bar()

st.title("📊 Portfolio Optimizer")
with st.expander("ℹ️ About the Portfolio Optimizer", expanded=True):
    st.markdown("""
    This tool helps you **optimize your stock portfolio** based on historical returns and volatility.

    - 📈 **Goal:** Maximize the Sharpe Ratio (risk-adjusted returns).
    - 🎯 **How:** Simulates thousands of random portfolios and identifies the most efficient one.
    - ⚙️ **Input:** Select your stocks and historical time range.
    - 📊 **Output:** Optimal weights for each stock, risk metrics, and Efficient Frontier.

    **Use this to balance return and risk intelligently!**
    """)

st.markdown("### Optimize your portfolio for maximum Sharpe Ratio using historical price data.")

# --- User Inputs ---
tickers_input = st.text_input("Enter stock tickers (comma-separated)", "AAPL, MSFT, GOOGL")
start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))
risk_free_rate = st.number_input("Risk-Free Rate (Annual, %)", min_value=0.0, max_value=10.0, value=1.5) / 100

# --- Clean Tickers ---
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

# --- Fetch Price Data ---
@st.cache_data
def fetch_prices(tickers, start, end):
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=True)['Close']
        return data if isinstance(data, pd.DataFrame) and not data.empty else None
    except Exception:
        return None

# --- Portfolio Metrics ---
def portfolio_performance(weights, mean_returns, cov_matrix, rf_rate):
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    sharpe = (returns - rf_rate) / std
    return returns, std, sharpe

def negative_sharpe(weights, mean_returns, cov_matrix, rf_rate):
    return -portfolio_performance(weights, mean_returns, cov_matrix, rf_rate)[2]

def optimize_portfolio(mean_returns, cov_matrix, rf_rate):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, rf_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    result = minimize(negative_sharpe, num_assets * [1. / num_assets], args=args,
                      method='SLSQP', bounds=bounds, constraints=constraints)
    return result

# --- Run Optimization ---
if st.button("Run Optimization"):
    if len(tickers) < 2:
        st.error("Please enter at least two valid stock tickers.")
    else:
        with st.spinner("Fetching data and optimizing portfolio..."):
            df = fetch_prices(tickers, start_date, end_date)
            if df is None:
                st.error("Failed to fetch price data. Check your tickers and try again.")
                st.stop()

            returns = df.pct_change().dropna()
            mean_returns = returns.mean()
            cov_matrix = returns.cov()

            opt = optimize_portfolio(mean_returns, cov_matrix, risk_free_rate)
            opt_weights = opt.x

            st.success("✅ Portfolio optimized successfully!")
            st.subheader("📋 Optimal Portfolio Weights")
            opt_df = pd.DataFrame({'Ticker': tickers, 'Weight': opt_weights})
            st.dataframe(opt_df.style.format({"Weight": "{:.2%}"}))

            port_return, port_std, port_sharpe = portfolio_performance(opt_weights, mean_returns, cov_matrix, risk_free_rate)

            st.metric("Expected Annual Return", f"{port_return:.2%}")
            st.metric("Annual Volatility", f"{port_std:.2%}")
            st.metric("Sharpe Ratio", f"{port_sharpe:.2f}")

            # Efficient Frontier Plot
            st.subheader("📈 Efficient Frontier")
            results = {'Returns': [], 'Volatility': [], 'Sharpe': [], 'Weights': []}
            for _ in range(5000):
                weights = np.random.dirichlet(np.ones(len(tickers)), size=1)[0]
                ret, vol, sharpe = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
                results['Returns'].append(ret)
                results['Volatility'].append(vol)
                results['Sharpe'].append(sharpe)
                results['Weights'].append(weights)

            results_df = pd.DataFrame(results)
            plt.figure(figsize=(10, 6))
            scatter = plt.scatter(results_df['Volatility'], results_df['Returns'], c=results_df['Sharpe'], cmap='viridis', alpha=0.7)
            plt.colorbar(scatter, label='Sharpe Ratio')
            plt.scatter(port_std, port_return, c='red', s=60, label='Optimal Portfolio')
            plt.title('Efficient Frontier')
            plt.xlabel('Volatility')
            plt.ylabel('Expected Return')
            plt.legend()
            st.pyplot(plt)
