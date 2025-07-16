import streamlit as st
import yfinance as yf
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.stats import norm

st.title("Stock Value at Risk (VaR) Calculator")

# Sidebar for inputs
st.sidebar.header("Parameters")
stock = st.sidebar.selectbox("Select Stock", ["AAPL", "MSFT", "TSLA", "GOOGL"])
confidence_level = st.sidebar.slider("Confidence Level (%)", 90, 99, 95) / 100
investment = st.sidebar.slider("Investment Amount ($)", 1000, 1000000, 100000, 1000)
method = st.sidebar.selectbox("VaR Method", ["Historical", "Variance-Covariance"])

# Date range input
default_end = datetime(2025, 5, 24)
default_start = default_end - timedelta(days=365 * 2)  # 2 years of data
date_range = st.sidebar.date_input("Select Date Range", value=[default_start, default_end],
                                    min_value=datetime(2020, 1, 1),
                                    max_value=datetime(2025, 6, 30))


# Download stock data with caching
@st.cache_data
def load_data(stock, start_date, end_date):
    try:
        df = yf.download(stock, start=start_date, end=end_date, progress=False)
        if df.empty:
            raise ValueError("No data for the selected stock and date range")
        return df
    except Exception as e:
        raise Exception(f"Error getting data: {e}")


# Process data and calculate VaR
try:
    # date_range has to have two dates
    if len(date_range) != 2:
        st.error("Please select valid start and end date.")
    else:
        start_date, end_date = date_range
        data = load_data(stock, start_date, end_date)
        prices = data["Close"]

        # Calculate daily returns
        returns = prices.pct_change().dropna()
        if len(returns) < 10:
            st.error("Not enough data points to compute VaR")
        else:
            returns_1d = returns.to_numpy().flatten() # 1d returns for Plotly

            # Compute VaR with the method that is selected
            if method == "Historical":
                var_percent = np.percentile(returns_1d, (1 - confidence_level) * 100)
            else:  # Variance-Covariance
                mean = returns_1d.mean()
                std = returns_1d.std()
                z_score = norm.ppf(1 - confidence_level)  # One-tailed z-score, negative for left tail
                var_percent = mean + z_score * std

            var_dollar = var_percent * investment

            # Display results
            st.header(f"{method} VaR for {stock}")
            st.write(f"1-day {confidence_level * 100:.1f}% VaR (percent): {var_percent:.2%}")
            st.write(f"1-day {confidence_level * 100:.1f}% VaR (dollar): ${-var_dollar:.2f}")

            # Create interactive histogram
            fig = px.histogram(
                x=returns_1d,
                nbins=50,
                title=f"Daily Returns Distribution for {stock} ({method} VaR)",
                labels={"x": "Daily Returns", "y": "Frequency"}
            )
            fig.add_vline(
                x=var_percent,
                line_dash="dash",
                line_color="red",
                annotation_text=f"VaR: {var_percent:.2%}",
                annotation_position="top right"
            )
            # Add normal distribution curve for var-covar method
            if method == "Variance-Covariance":
                x = np.linspace(min(returns_1d), max(returns_1d), 100)
                y = norm.pdf(x, mean, std) * len(returns_1d) * (max(returns_1d) - min(returns_1d)) / 50
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Normal Distribution", line=dict(color="blue")))
            st.plotly_chart(fig, use_container_width=True)

            # Plot stock price history
            st.header(f"{stock} Price History")
            prices_1d = prices.to_numpy().flatten() # PRICES HAVE TO BE 1D for Plotly
            price_fig = px.line(x=prices.index, y=prices_1d,
                title=f"{stock} Adjusted Closing Prices",
                labels={"x": "Date", "y": "Price ($)"})
            st.plotly_chart(price_fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Developed by Evan Gaul")
