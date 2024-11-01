import pandas as pd


class DataCollector:
    def __init__(self):
        pass

    def get_data(self):
        raise NotImplementedError("Subclasses must implement the get_data method")

    def fetch_data(self):
        raise NotImplementedError("Subclasses must implement the fetch_data method")

    def load_data_csv(self, csv_file_path, index_name): # maybe pass needed index instead of implementing in subclasses
        data = pd.read_csv(csv_file_path)
        data.set_index(index_name, inplace=True)
        return data


if __name__ == '__main__':
    pass
