import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
from data_collector import DataCollector
from secret_codes import secret_codes
API_KEY = secret_codes["Alpaca API Key"]
API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]

class MarketDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

    def get_data(self):
        pass

    def fetch_data(self):
        pass

    def load_data(self):
        pass

    def save_data(self):
        pass

client = StockHistoricalDataClient(API_KEY, API_SECRET_KEY)

# Create a request for historical bars (candles)
request_params = StockBarsRequest(
    symbol_or_symbols=['AAPL'],  # Stock symbol(s)
    timeframe=TimeFrame.Day,     # Timeframe (Day, Minute, Hour, etc.)
    start=datetime(2023, 1, 1),  # Start date
    end=datetime(2023, 10, 1)    # End date
)

# Fetch the data
bars = client.get_stock_bars(request_params)

# Convert the response to a dictionary
data = bars.df  # pandas DataFrame
print(data)