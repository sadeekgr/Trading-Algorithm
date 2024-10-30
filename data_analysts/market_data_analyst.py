from data_analysts.data_analyst import DataAnalyst
from data_collectors import MarketDataCollector


class MarketDataAnalyst(DataAnalyst):
    def __init__(self, market_data_collector=None):
        if market_data_collector == None:
            market_data_collector = MarketDataCollector()
        super().__init__(market_data_collector)
        self.indicators = {
            'EMA': {13: None}, # maybe with what angle it intersects the RMAs
            'RMA': {21: None, 53: None, 199: None},
            'ROC': {12: None},
            'Support': {3: None, 59: None}, # strenght proportional to volume
            'Resistance': {3: None, 59: None},
            # consider change in num of shares (use an average share count?)
            # order book / market depth / liquidity heatmap
            # rate of change of ROC
            # average up / down movement's duration and speed calculated through ROC
            # variability of ROC compared to average ROC
            # Bollinger Bands
            #'RSI': {14: None},
            # pre and after market price action
            # analyze time of day (sleep, breakfast, after work)
        }
        pass

    def load_indicators_historical_market_data(self, csv_path):
        pass

    def analyze_data(self):
        pass


if __name__ == '__main__':
    pass
