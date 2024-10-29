from data_analysts.data_analyst import DataAnalyst
from data_collectors import CompanyDataCollector

#yfinance, yahooquery, financialmodelingprep, finvizfinance
class CompanyDataAnalyst(DataAnalyst):
    # quarterly reports are unaudited, so annual ones hold far more weight, 8k are for important events
    def __init__(self, company_data_collector=None):
        if company_data_collector == None:
            company_data_collector = CompanyDataCollector()
        super().__init__(company_data_collector)
        self.indicators = {
            # CAGR (5y, 10, 15y)
            # Net Debt / EBITDA
            # FCF Conversion
            # KPI
            # Revenue characteristics (contractual, recurrning, seasonal)
            # capital structure
            # net capital employed
            # net invested capital
            # net equity
            # Insider Transaction (IMPORTANT)
            # Dollar cost average
            # ROE = [ROI + (Debt / Equity) * (ROI - Cost of Debt)] * fiscal and discounting operations index
            # fiscal and discounting operations index = Net Profit / Profit before taxes from continuing operations
            # ROI
            # Net Profit Margin
            # preferred(?) dividends (Payout Ratio (?))
            # sustainability growth rate = ROE*(1-Payout Ratio)
            # ROA (Return on assets)
            # ROCE (Return on capital employed) = EBIT / (Avg. Shareholders' Equity + Avg. Long Term Debt)
            # Operating Profit Margin
            # Asset Turnover Ratio = Revenues / Total Assets
            # EBITDA Margin
            # Quality of Operating Earnings = CFFO / EBIT
            # consider change in num of shares (use an average share count?)
            # EPS (average earnings per share) = (Net income - pref. dividends) / num of shares, consider change in num of shares (use an average share count?)
            # CUSTOM: net-income (or equivalent) / (assets + running costs), take into account how much it borrowed as it can increase net-income, how efficiently uses assets to generate income (especially useful for smaller companies)
            # (EPS2 * period2 - EPS1 * period1) / (period1 + period2), average perceived EPS increase rate with linear weight to period
            # EPS2 * e^(period2 / (period1 + period2))
            # Price to Earnings = Share Price / EPS = Market Capitalization / Net income
            # Enterprise value to EBIT = (Market Capitalization + Total Debt - Cash) / EBIT
            # Enterprise value to sales = (Market Capitalization + Total Debt - Cash) / Revenues
            # Debt to Capital Ratio = Total Liabilities / (Equity + Total Liabilities)
            # Equity Multiplier = Total Assets / Equity
            # Debt Service Cover Ratio = unlevered free cash flow / (Principal + Interest)
            # Loan Life Cover Ratio = ... (on notes, but maybe it's an estimate)
            # net interest margin = avg. interest rate on assets * (assets with fixed rate + assets with floating rate) - avg. interest rate on liabilities * (liabilities with fixed rate + liabilities with floating rate)
            # return on invested capital
            # trade receivables
            # short-term-debt-coverage = CFFO (Cash Flow from Operations) / Current Financial Debt
            # CAPEX
            # CAPEX-Coverage-Ratio
            # simple interest law
            # zero coupon bonds
            # spot interest rates and spot prices
            # pp curve
            # markup
            # extensive and intensive margin
            # Ramsey Boiteux Pricing model
            # Peak Lood Pricing
            # Ror-Aj Model
        }

    def analyze_data(self):
        pass
