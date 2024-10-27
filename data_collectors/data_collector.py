import pandas as pd
class DataCollector:
    def __init__(self):
        pass

    def get_data(self):
        pass

    def fetch_data(self):
        pass

    def load_data_csv(self, csv_file_path): # maybe pass needed index instead of implementing in subclasses
        pass

    def save_data_csv(self, data, csv_file_path):
        data.to_csv(csv_file_path, index=True)
