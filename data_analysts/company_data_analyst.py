from data_analysts.data_analyst import DataAnalyst
from data_collectors import CompanyDataCollector


class CompanyDataAnalyst(DataAnalyst):
    def __init__(self, company_data_collector=None):
        if company_data_collector == None:
            company_data_collector = CompanyDataCollector()
        super().__init__(company_data_collector)
        self.indicators = {
            # preferred(?) dividends
            # consider change in num of shares (use an average share count?)
            # EPS (average earnings per share) = (Net income - pref. dividends) / num of shares, consider change in num of shares (use an average share count?)
            # CUSTOM: net-income (or equivalent) / (assets + running costs), take into account how much it borrowed as it can increase net-income, how efficiently uses assets to generate income (especially useful for smaller companies)
            # (EPS2 * period2 - EPS1 * period1) / (period1 + period2), average perceived EPS increase rate with linear weight to period
            # EPS2 * e^(period2 / (period1 + period2))
        }
        pass

    def analyze_data(self):
        pass