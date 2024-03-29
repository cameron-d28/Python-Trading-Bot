from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from numpy.lib.histograms import _histogram_dispatcher
from pandas._libs.tslibs import Timestamp
import requests, json
from alpha_vantage.timeseries import TimeSeries
from config2 import *
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import alpaca_trade_api as tradeapi
import io

#database access
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2021.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2021'
app.config['MYSQL_PASSWORD'] = 'm545CS42021'
app.config['MYSQL_DB'] = '2021project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#secret Key
app.config['SECRET_KEY'] = 'gshdnfjaebkashgdfhjkageads'
MYSQL = MySQL(app)

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY }
API = tradeapi.REST(
        'PKF3D1XLH52F3N738TRN',
        'kp2MNSS18DRt0jX9tlnZff7IBzamzlnbii8gAQJo',
        'https://paper-api.alpaca.markets'
        )

ts = TimeSeries(VANTAGE_KEY, output_format='pandas')
ti = TechIndicators(VANTAGE_KEY, output_format='pandas')

def get_account():
    r =requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)

def get_stock_info(symbol, interval):
    data, meta = ts.get_intraday(symbol, interval)
    d = [meta, data]
    return d

def get_order(ticker):
    return API.get_order_by_client_order_id(ticker)

def list_orders(): 
    # Get the last 100 of our closed orders
    closed_orders = API.list_orders(
    status='closed',
    limit=100,
    nested=True  # show nested multi-leg orders
    )

    # Get the closed orders
    closed_aapl_orders = [o for o in closed_orders]
    
    return closed_aapl_orders

def get_tech_indicator(symbol, interval, choice):
    choice = choice.lower()
    #statistic showing if overbought or over sold
    if choice == 'rsi':
        data, meta = ti.get_rsi(symbol, interval, 20, 'close')
        d = [meta, data]
        return d
    #ti showing the moving average
    elif choice == 'sma':
        data, meta = ti.get_sma(symbol, interval, 20, 'close')
        d = [meta, data]
        return d
    #ti showing the exponential average
    elif choice == 'ema':
        data, meta = ti.get_ema(symbol, interval, 20, 'close')
        d = [meta, data]
        return d
    #ti showing the volume weighted average
    elif choice == 'vwap':
        data, meta = ti.get_vwap(symbol, interval, 20, 'close')
        d = [meta, data]
        return d
        
def get_tech_val(symbol, interval, num, choice):
    vals = []
    d = get_tech_indicator(symbol, interval, choice)
    counter = 0
    for date, ind in d[1].items():
        for i in ind:
            if counter >= (len(d[1])-num):
                vals.insert(0, i)
            counter += 1
    if num == 1:
        return vals[0]
    else:
        return vals

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

def trade(indicator, symbol, default, owned):
    #turning comma seperated string to list
    if not default:
        info = indicator.split(",") 
        indicator = info[0]
        high = info[1]
        low = info[2]


    if indicator == 'rsi':
        rsi = get_tech_val(symbol,'daily', 1, 'rsi')
        if default:
            #sell if RSI above 80 (overbought) buy if RSI below 30 (oversold)
            if rsi >= 80:
                if owned == True:
                    print(symbol + ' would be bought but it is already owned')
                else:
                    #create_order(symbol,1, 'market', 'sell', 'gtc')
                    print(symbol + ' was overbought we sell 1 share')
                    owned = False
            elif rsi <= 30:
                if owned == False:
                    print(symbol + ' would be sold but it is not owned')
                else:
                    #create_order(symbol, 1, 'market', 'buy', 'gtc')
                    print(symbol + ' was oversold we bought 1 share')
                    owned = True
            else:
                print(symbol + ' was within range did not buy or sell')
        else:
            #sell if RSI above high (overbought) buy if RSI below low (oversold)
            if rsi >= high:
                if owned == True:
                    print(symbol + ' would be bought but it is already owned')
                else:
                    #create_order(symbol,1, 'market', 'sell', 'gtc')
                    print(symbol + ' was overbought we sold 1 share')
                    owned = False
            elif rsi <= low:
                if owned == False:
                    print(symbol + ' would be sold but it is not owned')
                else:
                    #create_order(symbol, 1, 'market', 'buy', 'gtc')
                    print(symbol + ' was oversold we bought 1 share')
                    owned = True
            else:
                print(symbol + ' was within range did not buy or sell')
    return owned
    # elif indicator == 'sma':
    #     short_sma = get_tech_val(symbol, 'daily', 10, 'sma')
    #     long_sma = get_tech_val(symbol, 'daily' 100, 'sma')
    #     if 

    # elif indicator == 'ema':

    # elif indicator == 'vwap':

def loop_through(mysql):
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM CamEliMax_orders'
    cursor.execute(query)
    mysql.connection.commit()
    results = cursor.fetchall()
    return results


print(loop_through(MYSQL))







# orders = list_orders()
# # # print(z)
# for x in orders:
#   print(x.client_order_id)
#   print(get_order(x.client_order_id))
# print('\n')


#demo
#response=get_stock_info('AAPL', '1min')
#response=get_tech_indicator('AAPL', 'daily', 'rsi')
#response=get_tech_val('AAPL', 'daily', 10, 'rsi')
#print(response)
#trade('rsi', 'MSFT', True)

