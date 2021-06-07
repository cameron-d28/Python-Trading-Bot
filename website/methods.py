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
import pickle
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

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
        #need to switch all values to a table and call from the table instead of calling
        #from API each time
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

def loop_through(mysql):
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM CamEliMax_orders'
    cursor.execute(query)
    mysql.connection.commit()
    results = cursor.fetchall()

    for x in results:
        #to keep track of each order
        count = 0
        if x['type'] == 'ai':
            #get list of indicators from mysql
            indicators=x['tech_indicator']
            #get unique_id from mysql
            unique_id=x['unique_id']
            #run through function to get list of indicators
            indicators=get_list(indicators)
            #get new data using list of indicators
            ticker=x['ticker']
            newData=get_new_data(ticker,indicators)
            #get algorithm from second mysql using unique_id
            cur = mysql.connection.cursor()
            query = "SELECT algorithm from CamEliMax_ML where unique_id=%s;"
            queryVars=(unique_id)
            cur.execute(query,queryVars)
            mysql.connection.commit()
            filename = cur.fetchall()

            infile=open(filename,'rb')
            algorithm=pickle.load(infile)
            #run new data through algorithm
            newData=sc.transform(newData)
            result=algorithm.predict(newData)
            #buy or sell given result
            if result==1:
                if x['filled']==0:
                    create_order(ticker, 1, 'market', 'buy', 'gtc')
            elif result==0:
                if x['filled']==1:
                    create_order(ticker, 1, 'market', 'sell', 'gtc')


        else:
            #checks to see if stock is owned
            if x['filled'] == 0:
                own = False
            else:
                own = True
            
            #checks if preset or manual
            if x['type'] == 'preset':
                default = True
            else:
                default = False
            filled = trade(x['tech_indicator'], x['ticker'], default, own)
    
        cursor = mysql.connection.cursor()
        #change if the order is filled or not
        if filled:
            query = "UPDATE CamEliMax_orders SET filled='1' WHERE unique_id=%s"
        else:
            query = "UPDATE CamEliMax_orders SET filled='0' WHERE unique_id=%s"
        unique_id = x['unique_id']
        queryVars = (unique_id,)
        cursor.execute(query, queryVars)
        mysql.connection.commit()
    
    return results

def get_list(tech_ind):
    s = tech_ind.split(",")
    s.pop()
    return s
    
def get_new_data(ticker, indicators):
    toTest=np.array([])
    outputsize='i'
    interval='i'
    timePeriod='i'
    seriesType='i'
    for x in indicators:
        time.sleep(15)
        if x=="MACD":
            outputsize='i'
            interval='daily'
            timePeriod='i'
            seriesType='close'
        if x=="RSI":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='close'
        if x=="SMA":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='close'
        if x=="STOCH":
            outputsize='i'
            interval='daily'
            timePeriod='i'
            seriesType='i'
        if x=="OBV":
            outputsize='i'
            interval='daily'
            timePeriod='i'
            seriesType='i'
        if x=="ADX":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='i'
        if x=="BBANDS":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='close'

        data=get_stock_info(x,ticker, outputsize,interval,timePeriod,seriesType)
        data=data["Technical Analysis: "+x]
        ii=0
        toReturn=0
        if (x=="RSI" or x=="SMA"):
            for day in data:
                if ii==3:
                    break
                num=data[day][x]
                toReturn=toReturn+float(num)
                ii=ii+1
            
            toReturn=toReturn/3
        else:
            for day in data:
                if ii==1:
                    break
                if x=="STOCH":
                    toReturn=data[day]["SlowD"]
                if x=="BBANDS":
                    toReturn=float(data[day]["Real Upper Band"])-float(data[day]["Real Middle Band"])
                else:
                    toReturn=data[day][x]
                ii=ii+1

        toTest=np.append(toTest,np.array(toReturn))
    toTest=toTest.astype(np.float)
    toTest=[toTest.tolist()]
    
def create_algorithm(ticker,indicators,threshold,unique_id,mysql):
    ii=0
    for x in indicators:
        time.sleep(15)
        if x=="MACD":
            outputsize='i'
            interval='daily'
            timePeriod='i'
            seriesType='close'
        if x=="RSI":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='close'
        if x=="SMA":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='close'
        if x=="STOCH":
            outputsize='i'
            interval='daily'
            timePeriod='i'
            seriesType='i'
        if x=="OBV":
            outputsize='i'
            interval='daily'
            timePeriod='i'
            seriesType='i'
        if x=="ADX":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='i'
        if x=="BBANDS":
            outputsize='i'
            interval='daily'
            timePeriod='50'
            seriesType='close'

        data=get_stock_info(x,ticker, outputsize,interval,timePeriod,seriesType)
        data=data["Technical Analysis: "+x]

        dataValues=np.array([])

        if (x=="RSI" or x=="SMA"):
            for day in data:
                dataValues=np.append(dataValues,np.array([data[day][x]]))
            
            dataValues=dataValues.astype(np.float)
            dataValues=getAverageValue(dataValues,3)
        
        else:
            if x=="STOCH":
                for day in data:
                    dataValues=np.append(dataValues,np.array([data[day]['SlowD']]))
            if x=="BBANDS":
                for day in data:
                    dataValues=np.append(dataValues,np.array([float(data[day]["Real Upper Band"])-float(data[day]["Real Middle Band"])]))
            else:
                for day in data:
                    dataValues=np.append(dataValues,np.array([data[day][x]]))

            dataValues=dataValues.astype(np.float)
            dataValues=np.delete(dataValues,[0])

        if ii==0:
            stocks=pd.DataFrame(dataValues,columns=[x])
        else:
            dataValues=pd.Series(dataValues)
            stocks.insert(loc=ii,column=x,value=dataValues)
        ii=ii+1
    
    pChangeResponse=get_stock_info('TIME_SERIES_DAILY_ADJUSTED',ticker,'full','i','i','i')
    pChangeResponse=pChangeResponse["Time Series (Daily)"]
    closeValues=np.array([])
    aa=0
    while aa<(len(dataValues)):
        for day in pChangeResponse:
            closeValues=np.append(closeValues,np.array([pChangeResponse[day]["5. adjusted close"]]))
            ii=ii+1
    closeValues=closeValues.astype(np.float)
    changes=np.diff(closeValues)
    closeValues=np.delete(closeValues, [0])
    changesP=np.divide(changes,closeValues)*(-100)
    changesP=pd.Series(changesP)
    stocks.insert(loc=ii,column="pChange",value=changesP)

    stocks=stocks.dropna()
    min=stocks['pChange'].min()
    max=stocks['pChange'].max()
    bins=[min,-1,threshold, max]
    group_names=['bad','nothing','good']
    stocks['pChange']=pd.cut(stocks['pChange'], bins=bins, labels=group_names)

    label_quality=LabelEncoder()
    stocks['pChange']=label_quality.fit_transform(stocks['pChange'])

    X=stocks.drop(['pChange'], axis=1)
    y=stocks['pChange']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state= 42)

    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    rfc = RandomForestClassifier(n_estimators=500)
    rfc.fit(X_train, y_train)

    #PICKLE
    filename=ticker+str(unique_id)
    outfile=open(filename,'wb')
    pickle.dump(rfc,outfile)
    outfile.close()

    cur = mysql.connection.cursor()
    query = "INSERT INTO CamEliMax_ML(ticker,algorithm,unique_id) VALUES (%s,%s,%s);"
    queryVars=(ticker,filename,unique_id)
    cur.execute(query,queryVars)
    mysql.connection.commit()


def getAverageValue(values,days):
    ii=0
    toReturn=np.array([])
    while ii<(len(values)-days):
        toAdd=0
        for x in range (days):
            toAdd=toAdd+values[ii+(x+1)]
        toAdd=toAdd/days
        toReturn=np.append(toReturn,np.array([toAdd]))
        ii=ii+1
    return toReturn




        

# for index, row in df.iterrows():
#     print(check_ticker(row['Symbol']))
