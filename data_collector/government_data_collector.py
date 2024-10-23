from .data_collector import DataCollector

class GovernmentDataCollector(DataCollector):
    def __init__(self):
        super().__init__("government")