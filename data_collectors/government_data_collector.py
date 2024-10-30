import requests, re, json, pandas as pd
from bs4 import BeautifulSoup
from data_collectors.data_collector import DataCollector
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
government_data_folder_path = "../data/government_data"
credit_ratings_file_path = f'{government_data_folder_path}/credit_ratings.csv'
inflation_rates_file_path = f'{government_data_folder_path}/inflation_rates.csv'


class GovernmentDataCollector(DataCollector):
    def __init__(self):
        super().__init__()

    def get_data(self):
        data = {}
        credit_ratings = self.get_credit_ratings()
        inflation_rates = self.get_inflation_rates()
        data['credit_ratings'] = credit_ratings
        data['inflation_rates'] = inflation_rates
        return data

    def fetch_data(self):
        data = {}
        credit_ratings = self.fetch_credit_ratings()
        inflation_rates = self.fetch_inflation_rates()
        data['credit_ratings'] = credit_ratings
        data['inflation_rates'] = inflation_rates
        return data

    def get_credit_ratings(self):
        credit_ratings = self.fetch_credit_ratings()
        credit_ratings.to_csv(credit_ratings_file_path)
        return credit_ratings

    def fetch_credit_ratings(self):
        credit_ratings_url = "https://tradingeconomics.com/country-list/rating"
        html = requests.get(credit_ratings_url, headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')
        credit_ratings_dict = {}
        entries = soup.find_all('tr')
        for entry in entries:
            country_raw = entry.find('a')
            score_raw = entry.find('span', class_='te-rating-score')
            if country_raw and score_raw:
                country = country_raw.text.strip()
                score = 0 if score_raw.text.strip() == '' else int(score_raw.text.strip())
                credit_ratings_dict[country] = score
        credit_ratings = pd.DataFrame(list(credit_ratings_dict.values()), index=list(credit_ratings_dict.keys()), columns=['credit_rating'])
        credit_ratings.index.name = 'country'
        return credit_ratings

    def get_inflation_rates(self):
        inflation_rates = self.fetch_inflation_rates()
        inflation_rates.to_csv(inflation_rates_file_path)
        return inflation_rates

    def fetch_inflation_rates(self):
        inflation_rates_url = 'https://tradingeconomics.com/country-list/inflation-rate?continent=world'
        html = requests.get(inflation_rates_url, headers=headers).text
        countries_data_match = re.search(r'var data = (\[.*?]);', html, re.DOTALL)
        inflation_rates_dict = {item['name']: item['value'] for item in json.loads(countries_data_match.group(1))}
        inflation_rates = pd.DataFrame(list(inflation_rates_dict.values()), index=list(inflation_rates_dict.keys()), columns=['inflation_rate'])
        inflation_rates.index.name = 'country'
        return inflation_rates

    def load_data(self, csv_file_path):
        return super().load_data_csv(csv_file_path, 'country')


if __name__ == '__main__':
    gov = GovernmentDataCollector()
    gov.get_data()
