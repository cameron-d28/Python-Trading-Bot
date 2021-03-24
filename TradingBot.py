from numpy.lib.histograms import _histogram_dispatcher
import requests, json
from alpha_vantage.timeseries import TimeSeries
from config import *
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import io

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY }

ts = TimeSeries(VANTAGE_KEY, output_format='pandas')
ti = TechIndicators(VANTAGE_KEY, output_format='pandas')

def get_account():
    r =requests.get(ACCOUNT_URL, headers=HEADERS)
    return json.loads(r.content)

def get_stock_info(symbol, interval):
    data, meta = ts.get_intraday(symbol, interval)
    d = [meta, data]
    return d

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

def trade(indicator, symbol, default):
    if indicator == 'rsi':
        rsi = get_tech_val(symbol,'daily', 1, 'rsi')
        if default:
            #sell if RSI above 80 (overbought) buy if RSI below 30 (oversold)
            if rsi >= 70:
                create_order(symbol,1, 'market', 'sell', 'gtc')
                print(symbol + ' was overbought we sell 1 share')
            elif rsi <= 30:
                create_order(symbol, 1, 'market', 'buy', 'gtc')
                print(symbol + ' was oversold we bought 1 share')
            else:
                print(symbol + ' was within range did not buy or sell')
        else:
            #sell if RSI above high (overbought) buy if RSI below low (oversold)
            high = int(input('What should your overbought RSI value be: '))
            low = int(input('What should your oversold RSI value be: '))
            if rsi >= high:
                create_order(symbol,1, 'market', 'sell', 'gtc')
                print(symbol + ' was overbought we sold 1 share')
            elif rsi <= low:
                create_order(symbol, 1, 'market', 'buy', 'gtc')
                print(symbol + ' was oversold we bought 1 share')
            else:
                print(symbol + ' was within range did not buy or sell')
    # elif indicator == 'sma':
    #     short_sma = get_tech_val(symbol, 'daily', 10, 'sma')
    #     long_sma = get_tech_val(symbol, 'daily' 100, 'sma')
    #     if 

    # elif indicator == 'ema':

    # elif indicator == 'vwap':



#demo
response=get_stock_info('AAPL', '1min')
#response=get_tech_indicator('AAPL', 'daily', 'rsi')
#response=get_tech_val('AAPL', 'daily', 10, 'rsi')
print(response)
#trade('rsi', 'MSFT', True)

