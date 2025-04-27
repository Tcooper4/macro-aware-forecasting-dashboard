import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

st.set_page_config(page_title="Portfolio Optimization Dashboard", layout="wide")
st.title("📈 Portfolio Optimization Dashboard")

st.caption("Optimize your portfolio for maximum Sharpe Ratio using historical data.")

# ---- User Inputs ----
tickers = st.text_input("Enter stock tickers separated by commas (e.g., AAPL, MSFT, GOOG):", value="AAPL, MSFT, GOOG")
start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

tickers = [ticker.strip().upper() for ticker in tickers.split(",") if ticker.strip()]

# ---- Caching data fetching ----
@st.cache_data
def fetch_data(tickers, start, end):
    try:
        data = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True)

        # If empty DataFrame
        if data.empty:
            st.error("No data was returned. Please check tickers and date range.")
            return None

        # Handle multi-ticker download
        if isinstance(data.columns, pd.MultiIndex):
            # Check if "Adj Close" exists in the multiindex
            if "Adj Close" in data.columns.get_level_values(1):
                df = data.xs('Adj Close', level=1, axis=1)
            else:
                st.error("'Adj Close' data is missing. Please check your tickers.")
                return None
        else:
            # Single ticker situation
            df = data.to_frame(name=tickers[0])

        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# ---- Optimization functions ----
def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    sharpe = returns / std
    return returns, std, sharpe

def negative_sharpe(weights, mean_returns, cov_matrix):
    return -portfolio_performance(weights, mean_returns, cov_matrix)[2]

def optimize_portfolio(mean_returns, cov_matrix):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    result = minimize(negative_sharpe, num_assets*[1./num_assets], args=args,
                      method='SLSQP', bounds=bounds, constraints=constraints)
    return result

# ---- Main Execution ----
if st.button("Optimize Portfolio"):
    if len(tickers) < 2:
        st.error("Please enter at least two tickers.")
    else:
        with st.spinner("Fetching data and optimizing..."):
            df = fetch_data(tickers, start_date, end_date)
            if df is None:
                st.stop()  # 🛑 Immediately stop app if data fetch failed

            returns = df.pct_change().dropna()
            mean_returns = returns.mean()
            cov_matrix = returns.cov()

            opt = optimize_portfolio(mean_returns, cov_matrix)
            opt_weights = opt.x

            # Show Optimal Portfolio
            st.subheader("🔎 Optimal Portfolio Allocation")
            opt_df = pd.DataFrame({'Ticker': tickers, 'Weight': opt_weights})
            st.dataframe(opt_df.style.format({"Weight": "{:.2%}"}))

            port_return, port_std, port_sharpe = portfolio_performance(opt_weights, mean_returns, cov_matrix)

            st.metric("Expected Annual Return", f"{port_return:.2%}")
            st.metric("Annual Volatility", f"{port_std:.2%}")
            st.metric("Sharpe Ratio", f"{port_sharpe:.2f}")

            # Plot Efficient Frontier
            st.subheader("📈 Efficient Frontier")
            results = {'Returns': [], 'Volatility': [], 'Sharpe': [], 'Weights': []}
            for _ in range(5000):
                weights = np.random.dirichlet(np.ones(len(tickers)), size=1)[0]
                ret, vol, sharpe = portfolio_performance(weights, mean_returns, cov_matrix)
                results['Returns'].append(ret)
                results['Volatility'].append(vol)
                results['Sharpe'].append(sharpe)
                results['Weights'].append(weights)

            results_df = pd.DataFrame(results)
            plt.figure(figsize=(10,6))
            scatter = plt.scatter(results_df['Volatility'], results_df['Returns'], c=results_df['Sharpe'], cmap='viridis', alpha=0.7)
            plt.colorbar(scatter, label='Sharpe Ratio')
            plt.scatter(port_std, port_return, c='red', s=50, label='Optimal Portfolio')
            plt.title('Efficient Frontier')
            plt.xlabel('Volatility')
            plt.ylabel('Return')
            plt.legend()
            st.pyplot(plt)
