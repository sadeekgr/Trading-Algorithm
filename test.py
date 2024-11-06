from datetime import datetime, timedelta
import time, re, requests, json, os, talib
import pandas as pd
from bs4 import BeautifulSoup
from finvizfinance.quote import Statements, finvizfinance
from alpaca.data import TimeFrame, StockHistoricalDataClient, StockLatestTradeRequest, StockLatestQuoteRequest, StockBarsRequest
from secret_codes import secret_codes
from tvDatafeed import TvDatafeed, Interval
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
API_KEY = secret_codes["Alpaca API Key"]
API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]
tv_username = secret_codes["TradingView username"]
tv_password = secret_codes["TradingView password"]


# Original data
data = {
    'timestamp': ['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-05'],
    'price': [100, 102, 104, 105],
    'weight': [1, 2, 1, 3]  # Example weights
}
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Calculate weighted mean price
mean_price = np.average(df['price'], weights=df['weight'])
num_samples = sum(data['weight'])

# Prepare data for regression
X = np.array(range(len(df))).reshape(-1, 1)  # Use indices as independent variable
y = df['price'].values  # Prices as dependent variable
weights = df['weight'].values

# Fit weighted linear regression model
model = LinearRegression()
model.fit(X, y, sample_weight=weights)
df['predicted_price'] = model.predict(X)

# Plotting
plt.figure(figsize=(10, 5))
plt.scatter(df['timestamp'], df['price'], label='Actual Prices', color='blue', alpha=0.6)
plt.plot(df['timestamp'], df['predicted_price'], label='Weighted Regression Line', color='red', linewidth=2)
plt.axhline(mean_price, color='green', linestyle='--', label='Mean Price')
plt.title('Price Over Time with Weighted Linear Regression Line, Mean Price, and Samples')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

