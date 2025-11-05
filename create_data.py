import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate synthetic stock data
def generate_stock_data(start_price, num_days=365, volatility=0.02):
    """Generate synthetic stock price data using random walk"""
    returns = np.random.normal(0.0005, volatility, num_days)
    prices = start_price * np.exp(np.cumsum(returns))
    return prices

# Stock configuration
stocks = {
    'AAPL': 150,
    'GOOGL': 140,
    'MSFT': 300,
    'TSLA': 200
}

# Generate dates and prices
num_days = 365
dates = [(datetime.now() - timedelta(days=num_days-i)).date() for i in range(num_days)]

# Create prices DataFrame
prices_df = pd.DataFrame({'Date': dates})
for ticker, start_price in stocks.items():
    prices_df[ticker] = generate_stock_data(start_price, num_days)

# Save prices CSV (date-only format)
prices_df.to_csv('prices.csv', index=False)
print(f"Generated prices.csv: {len(prices_df)} days x {len(stocks)} stocks")