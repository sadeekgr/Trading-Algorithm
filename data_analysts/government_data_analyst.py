from data_analysts.data_analyst import DataAnalyst
from data_collectors import GovernmentDataCollector


class GovernmentDataAnalyst(DataAnalyst):
    def __init__(self, government_data_collector=None):
        if government_data_collector == None:
            government_data_collector = GovernmentDataCollector()
        super().__init__(government_data_collector)
        self.indicators = {
            # investment into research
            # government bonds, https://tradingeconomics.com/bonds (affected by interest rate)
            # foreign credit rating's rate of change
        }
        pass

    def analyze_data(self):
        pass


if __name__ == '__main__':
    pass
