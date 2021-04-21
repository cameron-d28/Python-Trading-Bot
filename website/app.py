from flask import Flask, render_template, request
app = Flask(__name__)
import requests, json
from alpha_vantage.timeseries import TimeSeries
import sys
from config import *
import alpaca_trade_api as tradeapi
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import io

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': "PKF3D1XLH52F3N738TRN", 'APCA-API-SECRET-KEY': "kp2MNSS18DRt0jX9tlnZff7IBzamzlnbii8gAQJo"}

# ts = TimeSeries(VANTAGE_KEY, output_format='pandas')
# ti = TechIndicators(VANTAGE_KEY, output_format='pandas')

def get_account():
    r =requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)

def get_stock_info(function, symbol, interval):
    r=requests.get("https://www.alphavantage.co/query?function="+function+"&symbol="+symbol+"&interval="+interval+"&apikey="+"CO4XV7QPXCGK547G")
    return json.loads(r.content)

def create_order(symbol, qty, type, side, time_in_force):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    return json.loads(r.content)

def change_in_equity():
    # First, open the API connection
    api = tradeapi.REST(
        'PKF3D1XLH52F3N738TRN',
        'kp2MNSS18DRt0jX9tlnZff7IBzamzlnbii8gAQJo',
        'https://paper-api.alpaca.markets'
        )
    # Get account info
    account = api.get_account()
    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    return f'Today\'s portfolio balance change: ${round(balance_change,2)}'

@app.route("/")
def index():
    return render_template('home.html', change=change_in_equity(), ticker='AAPL', M1='SMA', M2='EMA', M3='RIS')

@app.route("/edit", methods=['POST'])
def edit():
    if request.values.get('pwd')=='Camelimax123':
        return render_template('edit.html')
    else:
        return render_template('home.html', change=change_in_equity(), error='Wrong Password')

@app.route("/preset_vals")
def preset():
    return render_template('preset.html')

@app.route("/manual_vals")
def manual():
    return render_template('manual.html')    