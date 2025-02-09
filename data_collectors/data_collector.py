import pandas as pd
from database_manager import DatabaseManager


class DataCollector:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def save_data_csv(self, data):
        raise NotImplementedError("Subclasses must implement the save_data_csv method")

    def save_data_db(self, data):
        raise NotImplementedError("Subclasses must implement the save_data_db method")

    def fetch_data(self):
        raise NotImplementedError("Subclasses must implement the fetch_data method")

    def load_data_csv(self, csv_file_path, index_names): # pass index names as ['index1', 'index2', ...]
        data = pd.read_csv(csv_file_path)
        data.set_index(index_names, inplace=True)
        return data
    
    def load_data_db(self, index_names):
        raise NotImplementedError("Subclasses must implement the load_data_db method")


if __name__ == '__main__':
    pass
