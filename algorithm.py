import pandas as pd

# ===== READ PRICE DATA =====
prices_df = pd.read_csv('prices.csv')
print(f"Loaded prices.csv: {len(prices_df)} days")

# Get stock tickers from columns (exclude 'Date' column)
stocks = [col for col in prices_df.columns if col != 'Date']
print(f"Stocks: {stocks}")


# ===== TRADING ALGORITHM =====
def moving_average_strategy(prices, short_window=20, long_window=50):
    """Moving Average Crossover Strategy"""
    short_ma = prices.rolling(window=short_window).mean()
    long_ma = prices.rolling(window=long_window).mean()

    signals = pd.Series(0, index=prices.index)
    signals[short_ma > long_ma] = 1   # Buy
    signals[short_ma < long_ma] = -1  # Sell

    return signals

# Generate signals for each stock
signals = {}
for ticker in stocks:
    signals[ticker] = moving_average_strategy(prices_df[ticker])

# Run simulation
from trading_simulator import TradingSimulator
simulator = TradingSimulator(stocks = stocks, initial_cash=100000)

for idx, row in prices_df.iterrows():
    date = row['Date']

    # Execute only one trade per day (first signal that triggers)
    traded_today = False
    for ticker in stocks:
        if not traded_today:
            signal = signals[ticker].iloc[idx]
            price = row[ticker]
            if simulator.execute_trade(date, ticker, signal, price):
                traded_today = True

    # Record portfolio state
    simulator.record_portfolio(date, row)

# Save results and plot performance
simulator.save_results(orders_file='orders.csv', portfolio_file='portfolio.csv')
simulator.plot_performance(prices_df, save_file='performance_plot.png')