import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Portfolio Overview", layout="wide")
st.title("💼 Portfolio Overview")

# --- Sidebar Portfolio Input ---
st.sidebar.header("📊 Portfolio Settings")
tickers = st.sidebar.text_input("Holdings (comma-separated)", "AAPL, MSFT, TSLA")
weights = st.sidebar.text_input("Weights (comma-separated)", "0.4, 0.3, 0.3")
benchmark = st.sidebar.text_input("Benchmark Ticker", "SPY")
start_date = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

tickers = [t.strip().upper() for t in tickers.split(",")]
weights = [float(w.strip()) for w in weights.split(",")]

if len(tickers) != len(weights):
    st.error("Tickers and weights must match.")
    st.stop()

# --- Fetch Price Data ---
def fetch_prices(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)["Adj Close"]
    return data.dropna()

df_prices = fetch_prices(tickers + [benchmark], start_date, end_date)
returns = df_prices.pct_change().dropna()

# --- Calculate Portfolio Metrics ---
weights = pd.Series(weights, index=tickers)
portfolio_returns = (returns[tickers] * weights).sum(axis=1)
cumulative = (1 + portfolio_returns).cumprod()

# --- Plot Portfolio Value ---
st.subheader("📈 Portfolio Value Over Time")
fig = go.Figure()
fig.add_trace(go.Scatter(x=cumulative.index, y=cumulative, mode='lines', name="Portfolio"))

if benchmark in df_prices.columns:
    benchmark_returns = returns[benchmark]
    benchmark_cum = (1 + benchmark_returns).cumprod()
    fig.add_trace(go.Scatter(x=benchmark_cum.index, y=benchmark_cum, mode='lines', name=benchmark))

fig.update_layout(title="Portfolio vs Benchmark", xaxis_title="Date", yaxis_title="Cumulative Return")
st.plotly_chart(fig, use_container_width=True)

# --- Show Metrics ---
st.subheader("📊 Performance Metrics")
st.metric("Total Return", f"{(cumulative[-1] - 1):.2%}")
st.metric("Annualized Volatility", f"{portfolio_returns.std() * (252**0.5):.2%}")
st.metric("Sharpe Ratio", f"{(portfolio_returns.mean() * 252) / (portfolio_returns.std() * (252**0.5)):.2f}")

# --- Allocation Pie Chart ---
st.subheader("🧮 Allocation Breakdown")
fig_pie = go.Figure(data=[go.Pie(labels=tickers, values=weights, hole=0.4)])
fig_pie.update_layout(title="Portfolio Allocation")
st.plotly_chart(fig_pie, use_container_width=True)

# --- Export Portfolio Returns ---
st.subheader("📥 Export")
df_export = pd.DataFrame({
    "Portfolio Cumulative Return": cumulative,
    benchmark: benchmark_cum if benchmark in df_prices.columns else None
})
st.download_button("Download CSV", df_export.to_csv().encode("utf-8"), file_name="portfolio_vs_benchmark.csv")
