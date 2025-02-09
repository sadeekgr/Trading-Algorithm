import requests, json, pandas as pd
from data_collectors.data_collector import DataCollector
from secret_codes import secret_codes
ALPACA_API_KEY = secret_codes["Alpaca API Key"]
ALPACA_API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]
market_data_relative_folder_path = "../data/market_data"
market_data_csv_relative_file_path = f"{market_data_relative_folder_path}/market_data.csv"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET_KEY
}
# bittrex for crypto


class MarketDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

    def fetch_data(self) -> pd.DataFrame:
        stocks_data = self.fetch_stocks_data()
        crypto_data = self.fetch_crypto_data()
        data = pd.concat([stocks_data, crypto_data], axis=0)
        return data

    def save_data_db(self, data): # saves data into database
        self.db_manager.save_market_data(data)

    def save_data_csv(self, data): # saves data into a csv file
        data.to_csv(market_data_csv_relative_file_path, index=True)

    def fetch_stocks_data(self) -> pd.DataFrame: # TO UPDATE, returns us stocks in alpaca, if changed to tradingview could return more, alpaca doesn't support historical data for small stocks, so they are removed too
        active_securities_data_url = "https://paper-api.alpaca.markets/v2/assets?status=active&attributes="
        active_securities_data_dict = json.loads(requests.get(active_securities_data_url, headers=headers).text)
        stocks_data_dict = [
            {'symbol': entry['symbol'], 'exchange': entry['exchange'], 'name': entry['name'], 'type': entry['class']} for entry in active_securities_data_dict
            if entry['tradable'] == True and entry['class'] == 'us_equity' and entry['exchange'] != 'BATS'] # TO UPDATE, only consider companies that have financial statements
        return pd.DataFrame(stocks_data_dict).set_index(['symbol', 'exchange'])

    def fetch_crypto_data(self) -> pd.DataFrame: # TO UPDATE, returns crypto data, use binance or else for this(?)
        return pd.DataFrame([{'symbol': 'XMR/USD', 'exchange': 'KRAKEN', 'name': 'Monero to USD', 'type': 'crypto'}]).set_index(['symbol', 'exchange'])

    def load_market_data_csv(self, csv_file_path):
        return super().load_data_csv(csv_file_path, ['symbol', 'exchange'])

    def load_market_data_db(self):
        return self.db_manager.load_market_data()


if __name__ == "__main__":
    start = pd.Timestamp.now()
    mk = MarketDataCollector()
    db = mk.fetch_data()
    mk.save_data_db(db)
    print(f'Elapsed: {pd.Timestamp.now()-start}')
