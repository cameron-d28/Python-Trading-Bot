from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import requests, json
from alpha_vantage.timeseries import TimeSeries
import sys
from config import *
import alpaca_trade_api as tradeapi
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import yfinance as yf
import numpy as np

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

#list all of our orders
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

#get order from clientid
def client_id(id):
    return API.get_order_by_client_order_id(id)

#get orders
def get_orders(type_of_orders, mysql):
    orders = []

    cursor = mysql.connection.cursor()
    query = 'SELECT ticker, id FROM CamEliMax_orders WHERE type=%s'
    queryVars = (type_of_orders,)
    cursor.execute(query, queryVars)
    mysql.connection.commit()
    results = cursor.fetchall()

    for x in results:
        if x['id'] == '':
            orders.append([x['ticker'], 'N/A', 'N/A'])
        else:
            order = client_id(x['id'])
            orders.append([order.symbol, order.filled_avg_price, order.filled_at])
    
    return orders

#checks to see if ticker is valid
def check_ticker(ticker):
    ticker= yf.Ticker(ticker.upper())
    try:
        ticker.info['symbol']
        return True
    except:
        return False

#finds our daily profits and loss
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


# for index, row in df.iterrows():
#     print(check_ticker(row['Symbol']))
