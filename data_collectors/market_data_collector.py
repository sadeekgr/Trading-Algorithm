import requests
from alpaca.data import StockHistoricalDataClient, CryptoBarsRequest, TimeFrame, StockBarsRequest

from data_collector import DataCollector
from secret_codes import secret_codes
API_KEY = secret_codes["Alpaca API Key"]
API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]


headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET_KEY
}


class MarketDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

    def get_data(self):

        pass

    def fetch_data(self):
        url = "https://paper-api.alpaca.markets/v2/assets?status=active&attributes="
        response = requests.get(url, headers=headers).text
        pass

    def load_data(self):
        pass

    def save_data(self):
        pass

client = StockHistoricalDataClient(API_KEY, API_SECRET_KEY)

request_params = CryptoBarsRequest(
  symbol_or_symbols=["BTC/USD"],
  timeframe=TimeFrame.Day,
  start="2022-09-01",
  end="2022-09-07"
)

# Create a request for historical bars (candles)
request_params = StockBarsRequest(
    symbol_or_symbols=['AAPL'],
    timeframe=TimeFrame.Day,
    start="2023-01-01",
    end="2023-10-01"
)

# Fetch the data
bars = client.get_stock_bars(request_params)

# Convert the response to a dictionary
data = bars.df  # pandas DataFrame
print(data)
