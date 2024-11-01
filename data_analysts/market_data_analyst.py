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
            #'support': [3, 59], # strenght proportional to volume
            #'resistance': [3, 59], # strenght proportional to volume
            # maybe consider with what angle the EMA intersects the RMAs
            # average up / down movement's duration and speed calculated through ROC
            # consider change in num of shares (use an average share count?)
            # order book / market depth / liquidity heatmap
            # Bollinger Bands
            #'RSI': [14],
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
            roc_values = ta.ROC(prices, timeperiod=timeperiod)
            first_valid_value = roc_values[~np.isnan(roc_values)][0]
            roc_values = np.nan_to_num(roc_values, nan=first_valid_value)
            indicator_data = ta.ROC(roc_values, timeperiod=timeperiod)
        elif indicator == 'mean_absolute_deviation_from_linear_ROC':
            roc_values = ta.ROC(prices, timeperiod=timeperiod)
            first_valid_value = roc_values[~np.isnan(roc_values)][0]
            roc_values = np.nan_to_num(roc_values, nan=first_valid_value)
            x = np.arange(len(roc_values)).reshape(-1, 1)
            linear_model = LinearRegression()
            linear_model.fit(x, roc_values)
            linear_values = linear_model.predict(x)
            absolute_deviations = np.abs(roc_values - linear_values)
            absolute_deviation_series = pd.Series(absolute_deviations)
            indicator_data = absolute_deviation_series.rolling(window=timeperiod).mean().to_numpy()
        elif indicator == 'support':
            pass
        elif indicator == 'resistance':
            pass
        first_valid_value = indicator_data[~np.isnan(indicator_data)][0]
        indicator_data = np.nan_to_num(indicator_data, nan=first_valid_value)
        return indicator_data

    def RMA(self, prices, timeperiod):
        alpha = 1 / timeperiod
        rma = np.zeros(len(prices))
        rma[0] = prices[0]
        for i in range(1, len(prices)):
            rma[i] = (1 - alpha) * rma[i - 1] + alpha * prices[i]
        return rma

    def analyze_data(self):
        pass


if __name__ == '__main__':
    mk = MarketDataAnalyst()
    data = mk.get_indicators(f'../sprt.csv')
    data.reset_index(inplace=True)
    fin.background = '#000000'
    fin.odd_plot_background = '#000000'
    fin.even_plot_background = '#000000'
    fin.foreground = '#ffffff'
    fin.cross_hair_color = '#ffffff'
    fin.legend_text_color = '#ffffff'
    fin.scale_text_color = '#ffffff'
    ax, ax2, ax3 = fin.create_plot('AAPL', rows=3)
    candles = data[['timestamp', 'open', 'close', 'high', 'low']]
    fin.candlestick_ochl(candles, ax=ax)
    fin.plot(data['timestamp'], data['EMA_13'], ax=ax, color='#486c77', legend='EMA 13')
    fin.plot(data['timestamp'], data['RMA_21'], ax=ax, color='#7297c4', legend='RMA 21')
    fin.plot(data['timestamp'], data['RMA_53'], ax=ax, color='#2a632e', legend='RMA 53')
    fin.plot(data['timestamp'], data['RMA_199'], ax=ax, color='#83222b', legend='RMA 199')
    fin.plot(data['timestamp'], data['ROC_12'], ax=ax2, legend='ROC 12')
    fin.plot(data['timestamp'], data['mean_absolute_deviation_from_linear_ROC_12'], ax=ax2, legend='MAD from Linear ROC 12')
    fin.plot(data['timestamp'], data['ROC_of_ROC_12'], ax=ax3, legend='ROC of ROC 12')
    fin.show()
