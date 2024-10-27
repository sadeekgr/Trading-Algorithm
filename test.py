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
start = datetime(year=2024, month=10, day=23, hour=12, minute=12, second=29)
end = datetime(year=2024, month=10, day=23, hour=18, minute=2, second=20)
num_bars_needed = 5
client = StockHistoricalDataClient(API_KEY, API_SECRET_KEY)
request_params = StockBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=TimeFrame.Minute,
    start=start,
    end=end
)
historical_market_data_alpaca = client.get_stock_bars(request_params).df
tv = TvDatafeed(tv_username, tv_password)
tv_data = tv.get_hist(symbol, exchange, interval=Interval.in_1_minute, n_bars=num_bars_needed, extended_session=True)
d = tv_data.index[0]
filtered_df = tv_data[tv_data.index >= start]
interval = Interval.in_1_minute
filename = "market_data.csv"
print(filtered_df)
