"""
DataCollector is the superclass, all other classes are subclasses of it.
"""

from data_collectors.data_collector import DataCollector
from data_collectors.government_data_collector import GovernmentDataCollector
from data_collectors.country_data_collector import CountryDataCollector
from data_collectors.market_data_collector import MarketDataCollector
from data_collectors.company_data_collector import CompanyDataCollector