from data_collectors.data_collector import DataCollector


class NewsDataCollector(DataCollector):
    # insider trading (top exec or managers are more important)
    # political trading
    # ?the more earnings reports are delayed, the more they're usually bad?
    # illegal insider tarding happens before earning and moves the price in that direction
    def __init__(self):
        super().__init__()

    def get_data(self):
        pass

    def fetch_data(self):
        pass

    def load_data(self):
        pass


if __name__ == '__main__':
    pass
