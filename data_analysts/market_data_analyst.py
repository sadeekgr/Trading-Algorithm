from data_analysts.data_analyst import DataAnalyst
from data_collectors import MarketDataCollector
import talib as ta
import numpy as np
import pandas as pd
import finplot as fin
from sklearn.linear_model import LinearRegression
market_data_relative_folder_path = "../data/market_data"
historical_market_data_relative_folder_path = f"{market_data_relative_folder_path}/historical_market_data"


class MarketDataAnalyst(DataAnalyst):
    def __init__(self, market_data_collector=None):
        self.market_data_collector = market_data_collector
        if market_data_collector == None:
            self.market_data_collector = MarketDataCollector()
        super().__init__(market_data_collector)
        self.indicators = {
            'EMA': [13], # exponential moving average
            'RMA': [21, 53, 199], # rolling moving average
            'ROC': [12], # rate of change, seems to behave like a pendulum (oscillator) with resistance, oscillates between similar highs and lows (or little less than earlier ones), especially when there is a bit of volatility
            'ROC_of_ROC': [12],
            'mean_absolute_deviation_from_linear_ROC': [12], # mean absolute deviation of ROC compared to its linear regression
            'support': [43, 177, 599], # strenght proportional to volume and difference between close and low, should divide price in bands whose width is 0.1% of curr price
            'resistance': [43, 177, 599], # strenght proportional to volume and difference between high and close, should divide price in bands whose width is 0.1% of curr price
            # inclined support and resistance are caused by market orders (they are a 'perceived' resistance and support), horizontal are caused by limit orders (they usually represent 'actual' support and resistance, should be stronger as they might be bulk orders from companies)
            # maybe consider with what angle the EMA intersects the RMAs
            # average up / down movement's duration and speed calculated through ROC
            # consider change in num of shares (use an average share count?)
            # order book / market depth / liquidity heatmap
            # Bollinger Bands
            # 'RSI': [14],
            # pre and after market price action
            # analyze time of day (sleep, breakfast, after work)
        }

    def get_indicators(self, csv_file_path):
        historical_market_data = self.load_indicators(csv_file_path)
        historical_market_data.to_csv(csv_file_path)
        return historical_market_data

    def load_indicators(self, csv_file_path):
        historical_market_data = self.market_data_collector.load_historical_market_data_csv(csv_file_path)
        wap_weights = {
            'close': 0.48,
            'high': 0.2,
            'low': 0.2,
            'open': 0.12
        }
        wap = np.array((sum(historical_market_data[price_type] * wap_weights[price_type] for price_type in wap_weights.keys()))) # weighted average price
        for indicator in self.indicators.keys():
            for timeperiod in self.indicators[indicator]:
                if indicator == 'support' or indicator == 'resistance':
                    historical_market_data[f'{indicator}_{timeperiod}'] = self.load_indicator(indicator, historical_market_data, timeperiod)
                else:
                    historical_market_data[f'{indicator}_{timeperiod}'] = self.load_indicator(indicator, wap, timeperiod)
        return historical_market_data

    def load_indicator(self, indicator, prices, timeperiod):
        if indicator == 'EMA':
            indicator_data = ta.EMA(prices, timeperiod=timeperiod)
        elif indicator == 'RMA':
            indicator_data = self.RMA(prices, timeperiod=timeperiod)
        elif indicator == 'ROC':
            indicator_data = ta.ROC(prices, timeperiod=timeperiod)
        elif indicator == 'ROC_of_ROC':
            indicator_data = self.ROC_of_ROC(prices, timeperiod=timeperiod)
        elif indicator == 'mean_absolute_deviation_from_linear_ROC':
            indicator_data = self.mean_absolute_deviation_from_linear_ROC(prices, timeperiod=timeperiod)
        elif indicator == 'support':
            indicator_data = self.support(prices, timeperiod=timeperiod)
        elif indicator == 'resistance':
            indicator_data = self.resistance(prices, timeperiod=timeperiod)
        first_valid_value = indicator_data[~np.isnan(indicator_data)][0]
        indicator_data = np.nan_to_num(indicator_data, nan=first_valid_value)
        return indicator_data

    def support(self, prices, timeperiod, use_candles=True, use_volume=True, use_smoothing=False): # TO UPDATE smoothing doesn't work well, maybe use numpy arrays to make calculations faster, maybe consider groups of candles not just single low or high
        rolling_lows = ta.MIN(prices['low'], timeperiod=timeperiod)
        rolling_lows = rolling_lows[rolling_lows != rolling_lows.shift(1)].dropna()
        lows = pd.DataFrame(columns=prices.columns)
        for timestamp, low_value in rolling_lows.items():
            current_position = prices.index.get_loc(timestamp)
            start_position = max(0, current_position - timeperiod + 1)
            earlier_prices = prices.iloc[start_position:current_position+1]
            match = earlier_prices[earlier_prices['low'] == low_value]
            most_recent_row = match.iloc[[0]]
            lows = pd.concat([lows, most_recent_row])
        volume = 1
        if use_volume:
            volume = lows['volume']
        close_low_diff = high_low_diff = 1
        high_close_diff = 0
        if use_candles:
            close_low_diff = lows['close'] - lows['low']
            high_close_diff = lows['high'] - lows['close']
            high_low_diff = lows['high'] - lows['low']
        lows['support_strength'] = ((close_low_diff * volume) - (high_close_diff * volume)) / high_low_diff
        lows.fillna(0, inplace=True)
        indicator_data = pd.DataFrame(index=prices.index)
        indicator_data['support_strength'] = 0.0
        indicator_data.loc[lows.index, 'support_strength'] = lows['support_strength']
        indicator_data['price'] = pd.NA
        indicator_data.loc[lows.index, 'price'] = lows['low']
        indicator_data['support_strength'] = indicator_data['support_strength'].rolling(window=timeperiod, min_periods=1).max()
        indicator_data['support_strength'] = indicator_data['support_strength'].where(indicator_data['support_strength'] > 0, pd.NA)
        indicator_data.ffill(inplace=True)
        indicator_data.bfill(inplace=True)
        indicator_data.reset_index(inplace=True)
        for i in range(1, len(indicator_data)):
            if indicator_data['support_strength'].iloc[i] == indicator_data['support_strength'].iloc[i - 1]:
                indicator_data.loc[indicator_data.index[i], 'price'] = indicator_data['price'].iloc[i - 1]
            else:
                strength = indicator_data['support_strength'].iloc[i]
                matching_lows = lows[(lows['support_strength'] == strength) & (lows.index <= indicator_data['timestamp'].iloc[i])]['low']
                if not matching_lows.empty:
                    indicator_data.loc[indicator_data.index[i], 'price'] = matching_lows.values[-1]
                else:
                    indicator_data.loc[indicator_data.index[i], 'price'] = pd.NA
        if use_smoothing:
            support = np.empty(len(indicator_data))
            for i in range(len(indicator_data)):
                if i < timeperiod:
                    window_len = i + 1
                    if window_len == 1:
                        support[i] = indicator_data.iloc[:i + 1].reset_index(drop=True)['price'][0]
                        continue
                else:
                    window_len = timeperiod
                current_window = indicator_data.iloc[i - window_len + 1:i + 1].reset_index(drop=True)
                current_window['change'] = current_window['support_strength'] != current_window['support_strength'].shift(1)
                current_window_prices = current_window[current_window['change']]['price'].values
                current_window_weights = current_window[current_window['change']]['support_strength'].values
                current_window_pos = current_window[current_window['change']].index.values
                X = current_window_pos.reshape(-1, 1)
                y = current_window_prices
                model = LinearRegression()
                model.fit(X, y, sample_weight=current_window_weights)
                full_range = np.arange(0, window_len).reshape(-1, 1)
                predicted_prices = model.predict(full_range)
                weighted_mean_price = float(np.sum(current_window_prices * current_window_weights) / sum(current_window_weights))
                predicted_prices = (predicted_prices + weighted_mean_price) / 2
                support[i - window_len + 1:i + 1] = predicted_prices
        else:
            support = indicator_data['price'].to_numpy()
        return support

    def resistance(self, prices, timeperiod, use_candles=True, use_volume=True, use_smoothing=False): # TO UPDATE, smoothing doesn't work well, maybe use numpy arrays to make calculations faster, maybe consider groups of candles not just single low or high
        rolling_highs = ta.MAX(prices['high'], timeperiod=timeperiod)
        rolling_highs = rolling_highs[rolling_highs != rolling_highs.shift(1)].dropna()
        highs = pd.DataFrame(columns=prices.columns)
        for timestamp, high_value in rolling_highs.items():
            current_position = prices.index.get_loc(timestamp)
            start_position = max(0, current_position - timeperiod + 1)
            earlier_prices = prices.iloc[start_position:current_position + 1]
            match = earlier_prices[earlier_prices['high'] == high_value]
            most_recent_row = match.iloc[[0]]
            highs = pd.concat([highs, most_recent_row])
        volume = 1
        if use_volume:
            volume = highs['volume']
        high_close_diff = high_low_diff = 1
        close_low_diff = 0
        if use_candles:
            high_close_diff = highs['high'] - highs['close']
            close_low_diff = highs['close'] - highs['low']
            high_low_diff = highs['high'] - highs['low']
        highs['resistance_strength'] = ((high_close_diff * volume) - (close_low_diff * volume)) / high_low_diff
        highs.fillna(0, inplace=True)
        indicator_data = pd.DataFrame(index=prices.index)
        indicator_data['resistance_strength'] = 0.0
        indicator_data.loc[highs.index, 'resistance_strength'] = highs['resistance_strength']
        indicator_data['price'] = pd.NA
        indicator_data.loc[highs.index, 'price'] = highs['high']
        indicator_data['resistance_strength'] = indicator_data['resistance_strength'].rolling(window=timeperiod, min_periods=1).max()
        indicator_data['resistance_strength'] = indicator_data['resistance_strength'].where(indicator_data['resistance_strength'] > 0, pd.NA)
        indicator_data.ffill(inplace=True)
        indicator_data.bfill(inplace=True)
        indicator_data.reset_index(inplace=True)
        for i in range(1, len(indicator_data)):
            if indicator_data['resistance_strength'].iloc[i] == indicator_data['resistance_strength'].iloc[i - 1]:
                indicator_data.loc[indicator_data.index[i], 'price'] = indicator_data['price'].iloc[i - 1]
            else:
                strength = indicator_data['resistance_strength'].iloc[i]
                matching_lows = highs[(highs['resistance_strength'] == strength) & (highs.index <= indicator_data['timestamp'].iloc[i])]['high']
                if not matching_lows.empty:
                    indicator_data.loc[indicator_data.index[i], 'price'] = matching_lows.values[-1]
                else:
                    indicator_data.loc[indicator_data.index[i], 'price'] = pd.NA
        if use_smoothing:
            resistance = np.empty(len(indicator_data))
            for i in range(len(indicator_data)):
                if i < timeperiod:
                    window_len = i + 1
                    if window_len == 1:
                        resistance[i] = indicator_data.iloc[:i + 1].reset_index(drop=True)['price'][0]
                        continue
                else:
                    window_len = timeperiod
                current_window = indicator_data.iloc[i - window_len + 1:i + 1].reset_index(drop=True)
                current_window['change'] = current_window['resistance_strength'] != current_window['resistance_strength'].shift(1)
                current_window_prices = current_window[current_window['change']]['price'].values
                current_window_weights = current_window[current_window['change']]['resistance_strength'].values
                current_window_pos = current_window[current_window['change']].index.values
                X = current_window_pos.reshape(-1, 1)
                y = current_window_prices
                model = LinearRegression()
                model.fit(X, y, sample_weight=current_window_weights)
                full_range = np.arange(0, window_len).reshape(-1, 1)
                predicted_prices = model.predict(full_range)
                weighted_mean_price = float(np.sum(current_window_prices * current_window_weights) / sum(current_window_weights))
                predicted_prices = (predicted_prices + weighted_mean_price) / 2
                resistance[i - window_len + 1:i + 1] = predicted_prices
        else:
            resistance = indicator_data['price'].to_numpy()
        return resistance

    def RMA(self, prices, timeperiod):
        alpha = 1 / timeperiod
        rma = np.zeros(len(prices))
        rma[0] = prices[0]
        for i in range(1, len(prices)):
            rma[i] = (1 - alpha) * rma[i - 1] + alpha * prices[i]
        return rma

    def ROC_of_ROC(self, prices, timeperiod):
        roc_values = ta.ROC(prices, timeperiod=timeperiod)
        first_valid_value = roc_values[~np.isnan(roc_values)][0]
        roc_values = np.nan_to_num(roc_values, nan=first_valid_value)
        roc_of_roc = ta.ROC(roc_values, timeperiod=timeperiod)
        return roc_of_roc

    def mean_absolute_deviation_from_linear_ROC(self, prices, timeperiod):
        roc_values = ta.ROC(prices, timeperiod=timeperiod)
        first_valid_value = roc_values[~np.isnan(roc_values)][0]
        roc_values = np.nan_to_num(roc_values, nan=first_valid_value)
        x = np.arange(len(roc_values)).reshape(-1, 1)
        linear_model = LinearRegression()
        linear_model.fit(x, roc_values)
        linear_values = linear_model.predict(x)
        absolute_deviations = np.abs(roc_values - linear_values)
        absolute_deviation_series = pd.Series(absolute_deviations)
        mean_absolute_deviation_from_linear_roc = absolute_deviation_series.rolling(window=timeperiod).mean().to_numpy()
        return mean_absolute_deviation_from_linear_roc


if __name__ == '__main__':
    mk = MarketDataAnalyst()
    data = mk.get_indicators(f'../data/market_data/historical_market_data/Start_2024-10-24-00-00-00_End_2024-10-28-00-00-00_Interval_1Min/NVDA_NASDAQ_historical_market_data.csv')
    data.reset_index(inplace=True)
    fin.background = '#000000'
    fin.odd_plot_background = '#000000'
    fin.even_plot_background = '#000000'
    fin.foreground = '#ffffff'
    fin.cross_hair_color = '#ffffff'
    fin.legend_text_color = '#ffffff'
    fin.scale_text_color = '#ffffff'
    ax, ax2, axv = fin.create_plot('AAPL', rows=3)
    candles = data[['timestamp', 'open', 'close', 'high', 'low']]
    fin.candlestick_ochl(candles, ax=ax)
    volumes = data[['timestamp', 'open', 'close', 'volume']]
    fin.volume_ocv(volumes, ax=axv)
    #fin.plot(data['timestamp'], data['EMA_13'], ax=ax, color='#486c77', legend='EMA 13')
    #fin.plot(data['timestamp'], data['RMA_21'], ax=ax, color='#7297c4', legend='RMA 21')
    #fin.plot(data['timestamp'], data['RMA_53'], ax=ax, color='#2a632e', legend='RMA 53')
    #fin.plot(data['timestamp'], data['RMA_199'], ax=ax, color='#83222b', legend='RMA 199')
    #fin.plot(data['timestamp'], data['LOW_7'], ax=ax, legend='LOW 7')
    #fin.plot(data['timestamp'], data['LOW_43'], ax=ax, legend='LOW 43')
    #fin.plot(data['timestamp'], data['LOW_177'], ax=ax, legend='LOW 177')
    fin.plot(data['timestamp'], data['support_43'], ax=ax, legend='support 43')
    fin.plot(data['timestamp'], data['support_177'], ax=ax, legend='support 177')
    fin.plot(data['timestamp'], data['support_599'], ax=ax, legend='support 599')
    fin.plot(data['timestamp'], data['resistance_43'], ax=ax, legend='resistance 43')
    fin.plot(data['timestamp'], data['resistance_177'], ax=ax, legend='resistance 177')
    fin.plot(data['timestamp'], data['resistance_599'], ax=ax, legend='resistance 599')
    fin.plot(data['timestamp'], data['ROC_12'], ax=ax2, legend='ROC 12')
    fin.plot(data['timestamp'], data['mean_absolute_deviation_from_linear_ROC_12'], ax=ax2, legend='MAD from Linear ROC 12')
    #fin.plot(data['timestamp'], data['ROC_of_ROC_12'], ax=ax3, legend='ROC of ROC 12')
    fin.show()
