import pandas as pd
import yfinance as yf

# Volatilits ETF, Emerging markets ETF, Euro & APAC large companies ETF 
index = ['^VIX', 'EEM', 'EFA']

#Olja, Guld, Silver, Natural Gas, Copper
commodities = ['CL=F', 'GC=F', 'SI=F', 'NG=F', 'HG=F']

# European auto pair (Volkswagen & Stellantis), Nordic banks pair (Nordea & SEB), European Energy pair (TotalEnergies & Equinor)
# Euro renewable energy pair (ENEL & Vestas), Nordic materials/mining pair (Boliden & Yara international)
# Standalones: Ericsson, BNP Paribas, Indra Sistemas, Vestas, Tullow Oil 
stocks = ['VOW3.DE', 'STLAM.MI', 'NDA-FI.HE', 'SEB-A.ST', 'TTE', 'EQNR.OL', 'ENEL.MI', 'VWS.CO', 'BOL.ST', 'YAR.OL', 'ERIC', 'BNP.PA', 'IDR.MC', 'TLW.L']

#EUR/USD, USD/JPY, USD/SEK
currencies = ['EURUSD=X', 'JPY=X', 'SEK=X']

start_date = "2010-01-01"
end_date = "2026-01-01"

all_tickers = index + commodities + stocks + currencies
all_data = yf.download(all_tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)

# Find common dates
if isinstance(all_data.columns, pd.MultiIndex):
    adj_close_prices = all_data['Close']
else:
    adj_close_prices = all_data['Close'].to_frame()

missing = [col for col in adj_close_prices.columns if adj_close_prices[col].iloc[:20].isna().all()]                                                                                          
print(f"Tickers missing data from {start_date}:", missing)     
common_dates = adj_close_prices.dropna().index

def save_asset_group(tickers, filename, prefix):
    df = adj_close_prices[tickers].loc[common_dates].copy()
    # Make dates anonymous
    df.to_csv(f"{filename}.csv", index=False)

print(f"Saving asset data from {common_dates[0]} to {common_dates[-1]}")
save_asset_group(index, "indices", "I")
save_asset_group(commodities, "commodities", "C")
save_asset_group(stocks, "stocks", "S")
save_asset_group(currencies, "currencies", "FX")