import requests
import json
import os
import pandas as pd
from datetime import date, datetime, timedelta
from alpaca.data import StockHistoricalDataClient, StockBarsRequest, TimeFrame
from tvDatafeed import TvDatafeed, Interval
from data_collector import DataCollector
from secret_codes import secret_codes

ALPACA_API_KEY = secret_codes["Alpaca API Key"]
ALPACA_API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]
tv_username = secret_codes["TradingView username"]
tv_password = secret_codes["TradingView password"]
market_data_relative_folder_path = "../data/market_data"
market_data_csv_relative_file_path = f"{market_data_relative_folder_path}/market_data.csv"
historical_market_data_relative_folder_path = f"{market_data_relative_folder_path}/historical_market_data"
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET_KEY
}
time_letter_to_seconds = {
    "Min": 60,
    "Hour": 360,
    "Day": 8640,
    "Week": 60480,
    "Month": 267840 # assuming 31 days
}
time_letter_to_alpaca_timeframe = {
    "Min": TimeFrame.Minute,
    "Hour": TimeFrame.Hour,
    "Day": TimeFrame.Day,
    "Week": TimeFrame.Week,
    "Month": TimeFrame.Month
}
time_letter_to_tv_interval = {
    [1, "Min"]: Interval.in_1_minute,
    [3, "Min"]: Interval.in_3_minute,
    [5, "Min"]: Interval.in_5_minute,
    [15, "Min"]: Interval.in_15_minute,
    [30, "Min"]: Interval.in_30_minute,
    [45, "Min"]: Interval.in_45_minute,
    [1, "Hour"]: Interval.in_1_hour,
    [2, "Hour"]: Interval.in_2_hour,
    [3, "Hour"]: Interval.in_3_hour,
    [4, "Hour"]: Interval.in_4_hour,
    [1, "Day"]: Interval.in_daily,
    [1, "Week"]: Interval.in_weekly,
    [1, "Month"]: Interval.in_monthly
}


class MarketDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

    def get_data(self, historical=False) -> pd.DataFrame: # saves data into a csv file
        data = self.fetch_data(historical)
        data.set_index('symbol', inplace=True)
        self.save_data_csv(data, market_data_csv_relative_file_path)
        return data

    def fetch_data(self, historical=False) -> pd.DataFrame:
        stocks_data = self.fetch_stocks_data(historical)
        crypto_data = self.fetch_crypto_data(historical)
        data = pd.concat([stocks_data, crypto_data], axis=0)
        return data

    def fetch_stocks_data(self, historical=False) -> pd.DataFrame: # returns us stocks in alpaca, if changed to tradingview could return more
        active_securities_data_url = "https://paper-api.alpaca.markets/v2/assets?status=active&attributes="
        active_securities_data_dict = json.loads(requests.get(active_securities_data_url, headers=headers).text)
        stocks_data_dict = [
            {'symbol': entry['symbol'], 'exchange': entry['exchange'], 'name': entry['name'], 'class': entry['class']}
            for entry in active_securities_data_dict if entry['tradable'] == True and entry['class'] == 'us_equity']
        if historical:
            for stock_dict in stocks_data_dict:
                self.get_historical_data(stock_dict['symbol'], stock_dict["exchange"], interval=[1, "Min"], start=date.today()-timedelta(days=4), end=date.today())
        return pd.DataFrame(stocks_data_dict)

    def fetch_crypto_data(self, historical=False) -> pd.DataFrame: # returns crypto, use binance or else for this(?)
        if historical:
            pass
        return pd.DataFrame([{'symbol': 'XMR/USD', 'name': 'Monero to USD', 'class': 'crypto'}])

    def get_historical_data(self, symbol, exchange, interval, start, end=date.today()) -> pd.DataFrame: # start and end included, saves data to a csv
        client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_API_SECRET_KEY)
        tv = TvDatafeed(tv_username, tv_password)
        difference = datetime.now() - start
        seconds_difference = difference.total_seconds()
        num_bars_needed = seconds_difference / (interval[0]*time_letter_to_seconds[interval[1]])
        if num_bars_needed > 7000:
            num_bars_needed = 10000
        tv_data = tv.get_hist(symbol, exchange, interval=time_letter_to_tv_interval[interval], n_bars=num_bars_needed, extended_session=True)
        earliest_bar_timestamp = tv_data.index[0]
        historical_market_data_tv = pd.DataFrame()
        historical_market_data_alpaca = pd.DataFrame()
        if earliest_bar_timestamp < end:
            # historical_market_data_tv = tv_data from earliest_bar to end
            end = earliest_bar_timestamp
        if earliest_bar_timestamp <= start:
            # historical_market_data_tv = historical_market_data_tv from start
            pass
        else:
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=time_letter_to_alpaca_timeframe[interval[1]],
                start=start,
                end=end
            )
            historical_market_data_alpaca = client.get_stock_bars(request_params).df # pandas data frame
            # technically, you should aggregate historical_market_data_alpaca if you inputted 3 Min, 4 Hours etc. instead of 1 Min, 1 Hour etc.
        historical_market_data = historical_market_data_alpaca # + historical_market_data_tv with axis = 0?
        folder_path = f"{historical_market_data_relative_folder_path}/Start_{start}_End_{end}_Interval_{interval[0]}{interval[1]}"
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        historical_market_data.to_csv(f"{folder_path}/{symbol}_{exchange}_historical_market_data.csv")
        return historical_market_data

    def load_data_csv(self, csv_file_path):
        data = super().load_data_csv(csv_file_path)
        data.set_index('symbol', inplace=True)
        return data





mk = MarketDataCollector()













print()