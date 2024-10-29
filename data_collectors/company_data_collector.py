import json
import os.path
import pandas as pd
import requests
from finvizfinance.quote import Statements, finvizfinance
from data_collectors.data_collector import DataCollector
from secret_codes import secret_codes
ALPACA_API_KEY = secret_codes["Alpaca API Key"]
ALPACA_API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]
headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_API_SECRET_KEY
}
company_data_relative_folder_path = "../data/company_data"
balance_sheet_relative_folder_path = f"{company_data_relative_folder_path}/balance_sheet"
cash_flow_statement_relative_folder_path = f"{company_data_relative_folder_path}/cash_flow_statement"
income_statement_relative_folder_path = f"{company_data_relative_folder_path}/income_statement"
market_data_relative_folder_path = "../data/market_data"
market_data_csv_relative_file_path = f"{market_data_relative_folder_path}/market_data.csv"


class CompanyDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

    def get_data(self):
        statements = self.fetch_data()
        for symbol in statements.keys():
            pd.DataFrame(statements[symbol]['Annual']['Balance Sheet']).to_csv(f'{balance_sheet_relative_folder_path}/annual/{symbol}.csv')
            pd.DataFrame(statements[symbol]['Annual']['Cash Flow Statement']).to_csv(f'{cash_flow_statement_relative_folder_path}/annual/{symbol}.csv')
            pd.DataFrame(statements[symbol]['Annual']['Income Statement']).to_csv(f'{income_statement_relative_folder_path}/annual/{symbol}.csv')
            pd.DataFrame(statements[symbol]['Quarterly']['Balance Sheet']).to_csv(f'{balance_sheet_relative_folder_path}/quarterly/{symbol}.csv')
            pd.DataFrame(statements[symbol]['Quarterly']['Cash Flow Statement']).to_csv(f'{cash_flow_statement_relative_folder_path}/quarterly/{symbol}.csv')
            pd.DataFrame(statements[symbol]['Quarterly']['Income Statement']).to_csv(f'{income_statement_relative_folder_path}/quarterly/{symbol}.csv')
        return statements

    def fetch_data(self):
        statements = {}
        finviz_statements_client = Statements()
        if os.path.exists(market_data_csv_relative_file_path):
            stocks_symbols_data = pd.read_csv(market_data_csv_relative_file_path, usecols=['symbol'])
        else:
            active_securities_data_url = 'https://paper-api.alpaca.markets/v2/assets?status=active&attributes='
            active_securities_data_dict = json.loads(requests.get(active_securities_data_url, headers=headers).text)
            stocks_symbols_dict = [
                {'symbol': entry['symbol']} for entry in active_securities_data_dict
                if entry['tradable'] == True and entry['class'] == 'us_equity' and entry['exchange'] != 'BATS']
            stocks_symbols_data = pd.DataFrame(stocks_symbols_dict)
        for symbol in stocks_symbols_data['symbol']:
            statements[symbol] = {'Annual': {}, 'Quarterly': {}}
            try:
                statements[symbol]['Annual']['Balance Sheet'] = finviz_statements_client.get_statements(ticker=symbol, statement='B', timeframe='A')
                statements[symbol]['Annual']['Cash Flow Statement'] = finviz_statements_client.get_statements(ticker=symbol, statement='C', timeframe='A')
                statements[symbol]['Annual']['Income Statement'] = finviz_statements_client.get_statements(ticker=symbol, statement='I', timeframe='A')
                statements[symbol]['Quarterly']['Balance Sheet'] = finviz_statements_client.get_statements(ticker=symbol, statement='B', timeframe='Q')
                statements[symbol]['Quarterly']['Cash Flow Statement'] = finviz_statements_client.get_statements(ticker=symbol, statement='C', timeframe='Q')
                statements[symbol]['Quarterly']['Income Statement'] = finviz_statements_client.get_statements(ticker=symbol, statement='I', timeframe='Q')
            except:
                del statements[symbol]
                print(f'No {symbol}')
                continue
        return statements

    def load_data(self):
        pass

cm = CompanyDataCollector()
cm.get_data()
