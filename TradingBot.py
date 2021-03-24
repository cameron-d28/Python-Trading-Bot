import requests, json
from alpha_vantage.timeseries import TimeSeries
from config import *

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY }

def get_account():
    r =requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)

def get_stock_info(function, symbol, interval):
    r=requests.get("https://www.alphavantage.co/query?function="+function+"&symbol="+symbol+"&interval="+interval+"&apikey="+VANTAGE_KEY)
    return json.loads(r.content)

def create_order(symbol, qty, type, side, time_in_force:
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    return json.loads(r.content)

#response=create_order("AAPL", 1, "market", "buy", "gtc")
response=get_stock_info('TIME_SERIES_DAILY_ADJUSTED','AAPL','5min')
for day in response["Time Series (Daily)"]:
    print(response["Time Series (Daily)"][day]["2. high"])

     
#print(json.dumps(response, indent=4))