import pandas as pd
class DataCollector:
    def __init__(self):
        pass

    def get_data(self):
        pass

    def fetch_data(self):
        pass

    def load_data_csv(self, csv_file_path):
        data = pd.read_csv(csv_file_path)
        return data

    def save_data_csv(self, data, csv_file_path):
        data.to_csv(csv_file_path, index=True)
