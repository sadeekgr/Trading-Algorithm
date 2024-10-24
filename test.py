import requests
import json
from secret_codes import secret_codes
API_KEY = secret_codes["Alpaca API Key"]
API_SECRET_KEY = secret_codes["Alpaca API Secret Key"]


url = "https://paper-api.alpaca.markets/v2/assets?status=active"

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET_KEY
}

response = requests.get(url, headers=headers)
data = json.loads(response.text)
for instrument in data:
    if instrument["tradable"] == False:
        data.remove(instrument)
    print(instrument)