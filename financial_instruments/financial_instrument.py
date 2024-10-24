class FinancialInstrument:
    def __init__(self, name, symbol, price, currency, volume):
        self.name = name
        self.symbol = symbol
        self.price = price
        self.currency = currency
        self.volume = volume
        self.historical_data = self.fetch_historical_data()

    def fetch_historical_data(self):
        pass