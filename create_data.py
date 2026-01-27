import pandas as pd
import yfinance as yf
import numpy as np

# Volatilitetsindex, Europe Stock Index, omx30 
index = ['^VIX', '^STOXX', '^OMX']

#Olja, Guld, Silver
commodities = ['CL=F', 'GC=F', 'SI=F']

# Stock pairs
stocks = ['JPM', 'BAC', 'XOM', 'CVX', 'NKE', 'ADDYY', 'INTC', 'AMD']

#EUR/USD, USD/GBP, USD/JPY, EUR/JPY
currencies = ['EURUSD=X', 'GBP=X', 'JPY=X', 'EURJPY=X']    

start_date = "2021-01-01"
end_date = "2026-01-01"

all_tickers = index + commodities + stocks + currencies
all_data = yf.download(all_tickers, start=start_date, end=end_date, progress=False)

# Find common dates
if isinstance(all_data.columns, pd.MultiIndex):
    open_prices = all_data['Open']
else:
    open_prices = all_data['Open'].to_frame()

common_dates = open_prices.dropna().index

def save_asset_group(tickers, filename, prefix):
    df = open_prices[tickers].loc[common_dates].copy()
    df.columns = [f"{prefix}{i}" for i in range(1, len(tickers) + 1)]
    df.to_csv(f"{filename}.csv", index=False)

save_asset_group(index, "Indices", "I")
save_asset_group(commodities, "Commodities", "C")
save_asset_group(stocks, "Stocks", "S")
save_asset_group(currencies, "Currencies", "FX")