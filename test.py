from datetime import datetime, timedelta
import time
import pandas as pd
import requests
import json
import os
from alpaca.data import TimeFrame, StockHistoricalDataClient, StockLatestTradeRequest, StockLatestQuoteRequest, StockBarsRequest
from secret_codes import secret_codes
from tvDatafeed import TvDatafeed, Interval
API_KEY = secret_codes["Alpaca API Key"]
API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]
tv_username = secret_codes["TradingView username"]
tv_password = secret_codes["TradingView password"]
symbol = 'AAPL'
exchange = 'NASDAQ'
start = '2024-10-10'
tv = TvDatafeed(tv_username, tv_password)
num_bars_needed = 5
# see how far back the earliest is, then alpaca up to that date or just alpaca to the end
tv_data = tv.get_hist(symbol, exchange, interval=Interval.in_daily, n_bars=num_bars_needed, extended_session=True)
# Set the symbol and parameters
symbol = 'AAPL'
exchange = "NASDAQ"
interval = Interval.in_1_minute
# Initialize an empty DataFrame or load existing data
filename = "market_data.csv"
try:
    data = pd.read_csv(filename)
except:
    data = pd.DataFrame()

# Function to fetch and save data
def fetch_and_save():
    # Fetch the latest 1-minute data
    new_data = tv.get_hist(symbol, exchange, interval=interval, n_bars=1, extended_session=True)
    return new_data

# Run every minute
while True:
    new_data = fetch_and_save()
    try:
        new_data.to_csv(filename, mode='a', index=True)
    except KeyboardInterrupt:
        print("Realtime Updating Interrupted")
    except:
        pass
    time.sleep(30)  # Wait one minute
