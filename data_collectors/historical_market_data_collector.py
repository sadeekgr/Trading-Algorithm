import pandas as pd
from math import ceil
from alpaca.data import StockHistoricalDataClient, StockBarsRequest, TimeFrame
from tvDatafeed import TvDatafeed, Interval
from data_collectors.market_data_collector import MarketDataCollector
from secret_codes import secret_codes
ALPACA_API_KEY = secret_codes["Alpaca API Key"]
ALPACA_API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]
tv_username = secret_codes["TradingView username"]
tv_password = secret_codes["TradingView password"]
market_data_relative_folder_path = "../data/market_data"
historical_market_data_relative_folder_path = f"{market_data_relative_folder_path}/historical_market_data"
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
    (1, "Min"): Interval.in_1_minute,
    (3, "Min"): Interval.in_3_minute,
    (5, "Min"): Interval.in_5_minute,
    (15, "Min"): Interval.in_15_minute,
    (30, "Min"): Interval.in_30_minute,
    (45, "Min"): Interval.in_45_minute,
    (1, "Hour"): Interval.in_1_hour,
    (2, "Hour"): Interval.in_2_hour,
    (3, "Hour"): Interval.in_3_hour,
    (4, "Hour"): Interval.in_4_hour,
    (1, "Day"): Interval.in_daily,
    (1, "Week"): Interval.in_weekly,
    (1, "Month"): Interval.in_monthly
}
# bittrex for crypto


class HistoricalMarketDataCollector(MarketDataCollector):
    def __init__(self):
        super().__init__()
        self.tv = TvDatafeed(tv_username, tv_password)
        self.alpaca_historical_stock_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_API_SECRET_KEY)
        # update db?

    def fetch_historical_data_default(self, symbol, exchange):
        data = pd.DataFrame()
        try:  # TO UPDATE, random days and periods hardcoded temporarily
            end = pd.Timestamp.now()
            start = end - pd.Timedelta(days=4)
            symbol_data = self.fetch_historical_data(symbol, exchange, interval=(1, "Min"), start=start, end=end)
            data = pd.concat([symbol_data, data], axis=0)
            end = start - pd.Timedelta(minutes=1)
            start = end - pd.Timedelta(days=10)
            symbol_data = self.fetch_historical_data(symbol, exchange, interval=(1, "Hour"), start=start, end=end)
            data = pd.concat([symbol_data, data], axis=0)
            end = start - pd.Timedelta(minutes=1)
            start = end - pd.Timedelta(days=360)
            symbol_data = self.fetch_historical_data(symbol, exchange, interval=(1, "Day"), start=start, end=end)
            data = pd.concat([symbol_data, data], axis=0)
            end = start - pd.Timedelta(minutes=1)
            start = end - pd.Timedelta(days=360)
            symbol_data = self.fetch_historical_data(symbol, exchange, interval=(1, "Week"), start=start, end=end)
            data = pd.concat([symbol_data, data], axis=0)
        except:  # TO UPDATE, Alpaca and TvDataFeed sometimes don't support data for crypto and some stocks, for now these get removed
            pass
        return data

    def fetch_historical_data(self, symbol, exchange, interval, start, end=pd.Timestamp.now()):# TO UPDATE, need aggregate historical_market_data
        last_date_query = f"""
            SELECT MAX(timestamp)
            FROM historical_market_data
            WHERE symbol = '{symbol}' AND exchange = '{exchange}';
        """
        first_date_query = f"""
            SELECT MIN(timestamp)
            FROM historical_market_data
            WHERE symbol = '{symbol}' AND exchange = '{exchange}';
        """
        last_date_db = self.db_manager.execute(last_date_query).fetchall()[0][0]
        first_date_db = self.db_manager.execute(first_date_query).fetchall()[0][0]
        historical_market_data = pd.DataFrame()
        # TO UPDATE, need aggregate historical_market_data if you inputted 3 Min, 4 Hours etc. instead of 1 Min, 1 Hour etc.
        if last_date_db != None and last_date_db >= start >= first_date_db:
            if end <= last_date_db:
                load_db_query = f"""
                    SELECT *
                    FROM historical_market_data
                    WHERE symbol = '{symbol}' AND exchange = '{exchange}' AND timestamp >= '{start}' AND timestamp <= '{end}';
                """
                historical_market_data = pd.read_sql(load_db_query, self.db_manager.connection)
                historical_market_data.set_index(['symbol', 'exchange', 'timestamp'], inplace=True)
                return historical_market_data
            else:
                load_db_query = f"""
                    SELECT *
                    FROM historical_market_data
                    WHERE symbol = '{symbol}' AND exchange = '{exchange}' AND timestamp >= '{start}';
                """
                historical_market_data = pd.read_sql(load_db_query, self.db_manager.connection)
                historical_market_data.set_index(['symbol', 'exchange', 'timestamp'], inplace=True)
                start = last_date_db + pd.Timedelta(minutes=1)
        difference = end - start
        seconds_difference = difference.total_seconds()
        num_bars_needed = ceil(seconds_difference / (interval[0]*time_letter_to_seconds[interval[1]]))
        try:
            tv_data = self.tv.get_hist(symbol, exchange, interval=time_letter_to_tv_interval[interval], n_bars=num_bars_needed, extended_session=True)
            tv_data.index.name = 'timestamp'
            del tv_data['symbol']
            tv_data.index = tv_data.index - pd.Timedelta(hours=2)
            earliest_bar_timestamp = tv_data.index[0]
        except TypeError:
            print(f"TvDataFeed does not support historical data of {symbol} in exchange {exchange}")
            raise TypeError
        historical_market_data_tv = pd.DataFrame()
        historical_market_data_alpaca = pd.DataFrame()
        if earliest_bar_timestamp < end:
            historical_market_data_tv = tv_data[tv_data.index <= end]
            end = earliest_bar_timestamp - pd.Timedelta(seconds=interval[0]*time_letter_to_seconds[interval[1]])
        if earliest_bar_timestamp <= start:
            historical_market_data_tv = historical_market_data_tv[historical_market_data_tv.index >= start]
        else:
            try:
                request_params = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=time_letter_to_alpaca_timeframe[interval[1]],
                    start=start.to_pydatetime(),
                    end=end.to_pydatetime()
                )
                historical_market_data_alpaca = self.alpaca_historical_stock_client.get_stock_bars(request_params).df # pandas data frame
                del historical_market_data_alpaca['vwap']
                del historical_market_data_alpaca['trade_count']
                historical_market_data_alpaca.index = historical_market_data_alpaca.index.droplevel('symbol')
                historical_market_data_alpaca.index = historical_market_data_alpaca.index.tz_localize(None)
                historical_market_data_alpaca.index.name = 'timestamp'
                # TO UPDATE, need aggregate historical_market_data_alpaca if you inputted 3 Min, 4 Hours etc. instead of 1 Min, 1 Hour etc.
            except KeyError:
                print(f"Alpaca does not support historical data of {symbol} in exchange {exchange}")
                raise KeyError
        fetched_historical_market_data = pd.concat([historical_market_data_alpaca, historical_market_data_tv], axis=0)
        fetched_historical_market_data.reset_index(inplace=True)
        fetched_historical_market_data['symbol'] = symbol
        fetched_historical_market_data['exchange'] = exchange
        fetched_historical_market_data.set_index(['symbol', 'exchange', 'timestamp'], inplace=True)
        historical_market_data = pd.concat([historical_market_data, fetched_historical_market_data], axis=0)
        return historical_market_data

    def save_data_csv(self, data):
        #data.to_csv(data.to_csv(f"{folder_path}/{symbol}_{exchange}_historical_market_data.csv"), index=True)
        pass

    def save_data_db(self, data):
        self.db_manager.save_historical_market_data(data)

    def update_data_db(self):
        symbols_data = self.fetch_data()
        super().save_data_db(symbols_data)
        for symbol, exchange in symbols_data.index:
            data = self.fetch_historical_data_default(symbol, exchange)
            self.db_manager.save_historical_market_data(data)

    def load_historical_market_data_csv(self, csv_file_path):
        data = super().load_data_csv(csv_file_path, 'timestamp')
        data.index = pd.to_datetime(data.index)
        return data

if __name__ == "__main__":
    start = pd.Timestamp.now()
    hmk = HistoricalMarketDataCollector()
    hmk.update_data_db()
    print(f'Elapsed: {start-pd.Timestamp.now()}')
