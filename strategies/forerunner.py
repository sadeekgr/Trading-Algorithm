from strategy import Strategy
from data_analysts import GovernmentDataAnalyst, CountryDataAnalyst


class Forerunner(Strategy):
    def __init__(self, analysts=None):
        if analysts == None:
            analysts = {
                "government": GovernmentDataAnalyst(),
                "country": CountryDataAnalyst
            }
        super().__init__(analysts)

    def buy_condition(self):
        pass

    def sell_condition(self):
        pass