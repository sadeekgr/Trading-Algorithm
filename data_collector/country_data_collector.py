from .data_collector import DataCollector

class CountryDataCollector(DataCollector):
    def __init__(self):
        super().__init__("country")