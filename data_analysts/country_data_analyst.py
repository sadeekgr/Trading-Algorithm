from data_analysts.data_analyst import DataAnalyst
from data_collectors import CountryDataCollector


class CountryDataAnalyst(DataAnalyst):
    def __init__(self, country_data_collector=None):
        if country_data_collector == None:
            country_data_collector = CountryDataCollector()
        super().__init__(country_data_collector)
        pass

    def analyze_data(self):
        pass
