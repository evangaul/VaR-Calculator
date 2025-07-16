# VaR-Calculator

A python tool to calculate portfolio Value at Risk using Historical or Variance-Covariance methods. 

## Features
- Supports two common VaR methods: Historical and Variance-Covariance
- Uses live financial data
- Plots historical return distributions and confidence thresholds
- User can input custom tickers and start/end dates.
- Adjustable confidence level and investment amount

## Methods
Historical:
- Calculates past daily returns
- Simulates loss distribution
- VaR = percentile of losses at the confidence level

Variance-Covariance:
- Assumes returns follow a normal distribution
- VaR = z-score * portfolio standard deviation

## Tech Stack
- Python 3
- Streamlit (for dashboard)
- yfinance, plotly, spicy, numpy





## License
MIT License
