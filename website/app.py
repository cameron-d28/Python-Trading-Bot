from flask_mysqldb import MySQL
from flask import Flask, render_template, request
import requests, json
import numpy as np
import heapq
from config import *
from alpha_vantage.timeseries import TimeSeries

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY }

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2021.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2021'
app.config['MYSQL_PASSWORD'] = 'm545CS42021'
app.config['MYSQL_DB'] = '2021project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route("/")
def index():
    closeValues=np.array([])
    response=get_stock_info('TIME_SERIES_DAILY_ADJUSTED','AAPL','i','i','i')
    for day in response["Time Series (Daily)"]:
        closeValues=np.append(closeValues,np.array([response["Time Series (Daily)"][day]["5. adjusted close"]]))
    closeValues=closeValues.astype(np.float)
    changes=np.diff(closeValues)
    closeValues=np.delete(closeValues,0)
    changes=(changes/closeValues)*(-100)
    largest=heapq.nlargest(5, range(len(changes)), changes.take)
    smallest=heapq.nsmallest(5, range(len(changes)), changes.take)
    
    RSIresponse=get_stock_info('RSI','AAPL','daily','20','close')
    RSIValues=np.array([])
    ii=0
    for day in RSIresponse["Technical Analysis: RSI"]:
        if ii==103:
            break
        else:
            RSIValues=np.append(RSIValues, np.array([RSIresponse["Technical Analysis: RSI"][day]["RSI"]]))
            ii=ii+1
    RSIValues=np.delete(RSIValues,0)
    cursor = mysql.connection.cursor()
    getPrevRSI(smallest,changes,RSIValues,cursor)
    return render_template('index.html')


def get_stock_info(function, symbol, interval, timePeriod, seriesType):
    r=requests.get("https://www.alphavantage.co/query?function="+function+"&symbol="+symbol+"&interval="+interval+"&time_period="+timePeriod+"&series_type="+seriesType+"&apikey="+VANTAGE_KEY)
    return json.loads(r.content)

def getPrevRSI(iList,changes,RSIValues,cursor):
    for index in iList:
        toAdd=["AAPL",changes[index]]
        for ii in range(3):
            toAdd.append(RSIValues[index+ii])
        query = 'INSERT INTO CamEliMax_TradingBot(Ticker,NetGain,RSI1,RSI2,RSI3) VALUES (%s,%s,%s,%s,%s);'
        queryVars=tuple(toAdd)
        cursor.execute(query,queryVars)
        mysql.connection.commit()