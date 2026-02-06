import pandas as pd

from trading_simulator import TradingSimulator

# ===== READ PRICE DATA =====
stock_prices = pd.read_csv('stocks.csv')
idx_prices = pd.read_csv('indices.csv')
com_prices = pd.read_csv('commodities.csv')
fx_prices = pd.read_csv('currencies.csv')

print(f"Loaded stock prices {len(stock_prices)} days")
print(f"Loaded index prices: {len(idx_prices)} days")
print(f"Loaded commodity prices: {len(com_prices)} days")
print(f"Loaded fx prices: {len(fx_prices)} days")

# Get tickers from columns (no Date column in CSVs)
stocks = list(stock_prices.columns)
indexes = list(idx_prices.columns)
commodities = list(com_prices.columns)
currencies = list(fx_prices.columns)
all_tickers = stocks + indexes + commodities + currencies

print(f"Stocks: {stocks}")
print(f"Indices: {indexes}")
print(f"Commodities: {commodities}")
print(f"FX Pairs: {currencies}" )

def trading_strategy(day_index, cash, holdings, prices, stock_prices, idx_prices, com_prices, fx_prices):
    short_window = 20
    long_window = 50
    day_index = int(day_index)  # Convert to int for iloc

    signals = []
    for ticker in stocks:
        # Use index-based slicing (day_index is the row number from the merged dataframe)
        series = stock_prices[ticker].iloc[:day_index + 1]
        if len(series) < long_window:
            continue

        short_ma = series.rolling(window=short_window).mean().iloc[-1]
        long_ma = series.rolling(window=long_window).mean().iloc[-1]

        if short_ma < long_ma:
            signals.append(("BUY", ticker, 10))
        if short_ma > long_ma and holdings.get(ticker, 0) > 0:
            signals.append(("SELL", ticker, 10))

    for ticker in indexes:
        # Do something
        pass

    for ticker in commodities:
        # Do something else
        pass    

    for ticker in currencies:
        # Do something else 
        pass

    return signals 

def build_all_prices_df():
    # Merge by index since CSVs don't have a Date column
    merged = pd.concat([stock_prices, idx_prices, com_prices, fx_prices], axis=1)
    # Add a Date column based on index
    merged['Date'] = range(len(merged))
    return merged

# ===== RUN SIMULATION =====
prices_df = build_all_prices_df()
simulator = TradingSimulator(assets=all_tickers)
simulator.run(
    trading_strategy,
    prices_df,
    data={
        "stocks": stock_prices,
        "indexes": idx_prices,
        "commodities": com_prices,
        "currencies": fx_prices,
    },
)

simulator.save_results(orders_file='orders.csv', portfolio_file='portfolio.csv')
simulator.plot_performance(prices_df, save_file='performance_plot.png')