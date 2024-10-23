import secret_codes
from .data_collector import DataCollector
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
