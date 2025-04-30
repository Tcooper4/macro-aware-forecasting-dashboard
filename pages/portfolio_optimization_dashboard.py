import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

st.set_page_config(page_title="Portfolio Optimization Dashboard", layout="wide")
st.title("📈 Portfolio Optimization Dashboard")
st.caption("Optimize your portfolio for maximum Sharpe Ratio using historical price data.")

# --- Sidebar Inputs ---
st.sidebar.header("⚙️ Portfolio Settings")
tickers = st.sidebar.text_input("Enter stock tickers (comma-separated)", value="AAPL, MSFT, GOOG")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))
risk_free_rate = st.sidebar.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=10.0, value=1.5) / 100
freq = st.sidebar.selectbox("Return Frequency", ["Daily", "Weekly", "Monthly"])
st.sidebar.page_link("streamlit_app.py", label="🔙 Back to Home")
st.sidebar.page_link("pages/live_macro_charts.py", label="🌐 Macroeconomic Charts")


tickers = [ticker.strip().upper() for ticker in tickers.split(",") if ticker.strip()]

# --- Fetch Price Data ---
@st.cache_data
def fetch_data(tickers, start, end):
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=True)['Close']
        if isinstance(data, pd.DataFrame) and not data.empty:
            return data
        else:
            return None
    except Exception:
        return None

# --- Portfolio Optimization Functions ---
def portfolio_performance(weights, mean_returns, cov_matrix, rf_rate=0.0):
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    sharpe = (returns - rf_rate) / std
    return returns, std, sharpe

def negative_sharpe(weights, mean_returns, cov_matrix, rf_rate=0.0):
    return -portfolio_performance(weights, mean_returns, cov_matrix, rf_rate)[2]

def optimize_portfolio(mean_returns, cov_matrix, rf_rate=0.0):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, rf_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    result = minimize(negative_sharpe, num_assets * [1. / num_assets], args=args,
                      method='SLSQP', bounds=bounds, constraints=constraints)
    return result

# --- Main Execution ---
if st.button("🚀 Run Optimization"):
    if len(tickers) < 2:
        st.error("⚠️ Please enter at least two stock tickers.")
    else:
        with st.spinner("Fetching data and optimizing your portfolio..."):
            df = fetch_data(tickers, start_date, end_date)
            if df is None:
                st.error("Failed to fetch price data. Check ticker symbols and date range.")
                st.stop()

            df = df.resample({'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}[freq]).last().dropna()
            returns = df.pct_change().dropna()
            mean_returns = returns.mean()
            cov_matrix = returns.cov()

            opt = optimize_portfolio(mean_returns, cov_matrix, risk_free_rate)
            opt_weights = opt.x

            st.success("✅ Portfolio optimization completed!")

            # --- Portfolio Metrics ---
            port_return, port_std, port_sharpe = portfolio_performance(opt_weights, mean_returns, cov_matrix, risk_free_rate)
            cumulative = (1 + returns @ opt_weights).cumprod()
            rolling_max = cumulative.cummax()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_dd = drawdown.min()

            with st.expander("🔎 Optimal Portfolio Allocation"):
                opt_df = pd.DataFrame({'Ticker': mean_returns.index, 'Weight': opt_weights})
                st.dataframe(opt_df.style.format({"Weight": "{:.2%}"}))

                # Pie chart
                fig1, ax1 = plt.subplots()
                ax1.pie(opt_weights, labels=mean_returns.index, autopct='%1.1f%%', startangle=90)
                ax1.axis('equal')
                st.pyplot(fig1)

                # Download button
                csv = opt_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Portfolio Weights", data=csv, file_name='optimized_portfolio.csv')

            with st.expander("📊 Portfolio Performance Metrics"):
                st.metric("Expected Annual Return", f"{port_return:.2%}")
                st.metric("Annual Volatility", f"{port_std:.2%}")
                st.metric("Sharpe Ratio", f"{port_sharpe:.2f}")
                st.metric("Max Drawdown", f"{max_dd:.2%}")

            with st.expander("📈 Efficient Frontier Visualization"):
                results = {'Returns': [], 'Volatility': [], 'Sharpe': []}
                for _ in range(5000):
                    weights = np.random.dirichlet(np.ones(len(mean_returns)), size=1)[0]
                    ret, vol, sharpe = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
                    results['Returns'].append(ret)
                    results['Volatility'].append(vol)
                    results['Sharpe'].append(sharpe)

                results_df = pd.DataFrame(results)

                with plt.style.context("dark_background" if st.get_option("theme.base") == "dark" else "default"):
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    scatter = ax2.scatter(results_df['Volatility'], results_df['Returns'],
                                          c=results_df['Sharpe'], cmap='viridis', alpha=0.7)
                    ax2.scatter(port_std, port_return, c='red', s=70, label='Optimal Portfolio')
                    ax2.set_title('Efficient Frontier')
                    ax2.set_xlabel('Annualized Volatility')
                    ax2.set_ylabel('Expected Annual Return')
                    ax2.legend()
                    fig2.colorbar(scatter, label='Sharpe Ratio')
                    st.pyplot(fig2)
