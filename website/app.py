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
from methods import list_orders, check_ticker, change_in_equity, get_orders

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


@app.route("/")
def index():
    return render_template('index.html', change=change_in_equity(), ticker='AAPL', M1='SMA', M2='EMA', M3='RIS')

@app.route("/home", methods=['POST', 'GET'])
def edit():
    if request.values.get('pwd')=='Camelimax123':
        return render_template('edit.html', change=change_in_equity())
    else:
        return render_template('home.html', change=change_in_equity() , error='Wrong Password')

@app.route("/preset_vals", methods=['POST', 'GET'])
def preset():
    orders = get_orders('preset', MYSQL)

    if request.method == 'GET':
        return render_template('preset.html', orders = orders)
    else:
        ticker=request.form.get('ticker')
        type=request.form.get('type')
        qty=int(request.form.get('qty'))
        tech_ind=request.form.get('tech_ind')

        if check_ticker(ticker) == False:
            return render_template('preset.html', orders = orders, reload=True, error='ticker')
        elif qty > 10: 
            return render_template('preset.html', orders = orders, reload=True, error='qty')
        else:
            cursor = MYSQL.connection.cursor()
            #INSERT stock information into database
            query = "INSERT INTO CamEliMax_orders (ticker, type, qty, tech_indicator) VALUES (%s, %s, %s, %s)"
            queryVars = (ticker, type, qty, tech_ind)
            cursor.execute(query, queryVars)
            MYSQL.connection.commit()
            return render_template('preset.html', orders = orders, reload=True, error='none')

@app.route("/manual_vals", methods=['POST', 'GET'])
def manual():
    orders = get_orders('manual', MYSQL)

    if request.method == 'GET':
        return render_template('manual.html', orders = orders)
    else:
        ticker=request.form.get('ticker')
        type=request.form.get('type')
        qty=int(request.form.get('qty'))
        tech_ind=request.form.get('tech_ind')
        high=request.form.get('high')
        low=request.form.get('low')

        if check_ticker(ticker) == False:
            return render_template('manual.html', orders = orders, reload=True, error='ticker')
        elif qty > 10: 
            return render_template('manual.html', orders = orders, reload=True, error='qty')
        else:
            cursor = MYSQL.connection.cursor()
            #INSERT stock information into database
            query = "INSERT INTO CamEliMax_orders (ticker, type, qty, tech_indicator) VALUES (%s, %s, %s, %s)"
            queryVars = (ticker, type, qty, tech_ind)
            cursor.execute(query, queryVars)
            MYSQL.connection.commit()
            return render_template('manual.html', orders = orders, reload=True, error='none')   

@app.route("/ai", methods=['POST', 'GET'])
def ai():
    orders = get_orders('ai', MYSQL)

    #test
    rsi=request.form.get('rsi')
    vol=request.form.get('vol')
    stoch_osc=request.form.get('stoch_osc')
    sma=request.form.get('sma')
    on_balance_vol=request.form.get('on_balance_vol')
    mov_avg_con=request.form.get('moving_avg_con')
    bol_bands=request.form.get('bol_bands')
    avg_dir_movement=request.form.get('avg_dir_movement')

    if request.method == 'GET':
        return render_template('ai.html', orders = orders)
    else:
        ticker=request.form.get('ticker')
        # tech_inde=would have to check if each tech ind is true or not
        percent_threshold=request.form.get('percent_threshold')

        if check_ticker(ticker) == False:
            return render_template('ai.html', orders = orders, reload=True, error='ticker')
        else: 
            return render_template('ai.html', orders = orders, reload=True, error='none')

@app.route('/test', methods=['POST', 'GET'])
def test():
    orders =  get_orders('preset', MYSQL)
    #need to organize orders to input
    return render_template('test.html', orders = orders, reload=True, error='none')



        

# @app.route('/add_preset_order', methods=['POST'])
# def order():
#     #request data from form to input to mySQL
    
    

