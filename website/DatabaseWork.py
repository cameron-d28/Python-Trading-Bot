import requests, json
import numpy as np
import pandas as pd
import time
import pickle
from alpha_vantage.timeseries import TimeSeries
from config import *
import matplotlib.pyplot as plt 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY }

ticker='ZG'

def get_stock_info(function, symbol, interval, timePeriod, seriesType):
    r=requests.get("https://www.alphavantage.co/query?function="+function+"&symbol="+symbol+"&interval="+interval+"&time_period="+timePeriod+"&series_type="+seriesType+"&apikey="+VANTAGE_KEY)
    return json.loads(r.content)

def get_stock_infoV(function, symbol, outputsize):
    r=requests.get("https://www.alphavantage.co/query?function="+function+"&symbol="+symbol+"&outputsize="+outputsize+"&apikey="+VANTAGE_KEY)
    return json.loads(r.content)

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

#MACDV

MACDVResponse=get_stock_info('MACD',ticker,'daily','i','close')

MACDVResponse=MACDVResponse["Technical Analysis: MACD"]

    
MACDVValues=np.array([])
for day in MACDVResponse:
    MACDVValues=np.append(MACDVValues,np.array([MACDVResponse[day]["MACD"]]))

MACDVValues=MACDVValues.astype(np.float)
MACDVValues=np.delete(MACDVValues,[0])

stocks=pd.DataFrame(MACDVValues,columns=['MACDV'])


#MACDH

MACDHValues=np.array([])
for day in MACDVResponse:
    MACDHValues=np.append(MACDHValues,np.array([MACDVResponse[day]["MACD_Hist"]]))

MACDHValues=MACDHValues.astype(np.float)
MACDHValues=np.delete(MACDHValues,[0])
MACDHValues=pd.Series(MACDHValues)

stocks.insert(loc=1,column="MACDH",value=MACDHValues)

#RSI

RSIResponse=get_stock_info('RSI',ticker,'daily','50','close')

RSIResponse=RSIResponse["Technical Analysis: RSI"]
RSIValues=np.array([])

for day in RSIResponse:
    RSIValues=np.append(RSIValues,np.array([RSIResponse[day]["RSI"]]))

RSIValues=RSIValues.astype(np.float)
RSIAverages=getAverageValue(RSIValues,3)
RSIAverages=pd.Series(RSIAverages)

stocks.insert(loc=2,column="RSI",value=RSIAverages)


#SMA
SMAResponse=get_stock_info('SMA',ticker,'daily','50','close')

SMAResponse=SMAResponse["Technical Analysis: SMA"]
SMAValues=np.array([])

for day in SMAResponse:
    SMAValues=np.append(SMAValues,np.array([SMAResponse[day]["SMA"]]))

SMAValues=SMAValues.astype(np.float)
SMAAverages=getAverageValue(SMAValues,3)

SMAAverages=pd.Series(SMAAverages)

stocks.insert(loc=3,column="SMA",value=SMAAverages)


#STOCH
STOCHResponse=get_stock_info('STOCH',ticker,'daily','i','i')

STOCHResponse=STOCHResponse["Technical Analysis: STOCH"]
STOCHValues=np.array([])
for day in STOCHResponse:
    STOCHValues=np.append(STOCHValues,np.array([STOCHResponse[day]["SlowD"]]))

STOCHValues=STOCHValues.astype(np.float)    
    
STOCHValues=np.delete(STOCHValues,[0])

STOCHValues=pd.Series(STOCHValues)

stocks.insert(loc=4,column="STOCH",value=STOCHValues)


#OBV
OBVResponse=get_stock_info('OBV',ticker,'daily','i','i')

OBVResponse=OBVResponse["Technical Analysis: OBV"]
OBVValues=np.array([])
for day in OBVResponse:
    OBVValues=np.append(OBVValues,np.array([OBVResponse[day]["OBV"]]))

OBVValues=OBVValues.astype(np.float)
OBVValues=np.delete(OBVValues,[0])

OBVValues=pd.Series(OBVValues)

stocks.insert(loc=5,column="OBV",value=OBVValues)


#ADX
time.sleep(60)
ADXResponse=get_stock_info('ADX',ticker,'daily','50','i')


ADXResponse=ADXResponse["Technical Analysis: ADX"]
ADXValues=np.array([])
for day in ADXResponse:
    ADXValues=np.append(ADXValues,np.array([ADXResponse[day]["ADX"]]))

ADXValues=ADXValues.astype(np.float)
ADXValues=np.delete(ADXValues,[0])

ADXValues=pd.Series(ADXValues)

stocks.insert(loc=6,column="ADX",value=ADXValues)


#BBD
BBDResponse=get_stock_info('BBANDS',ticker,'daily','50','close')

BBDResponse=BBDResponse["Technical Analysis: BBANDS"]
BBDValues=np.array([])
for day in BBDResponse:
    diff=float(BBDResponse[day]["Real Upper Band"])-float(BBDResponse[day]["Real Middle Band"])
    BBDValues=np.append(BBDValues,np.array([diff]))
    
BBDValues=np.delete(BBDValues,[0])

BBDValues=pd.Series(BBDValues)

stocks.insert(loc=7,column="BBD",value=BBDValues)


#BBM
BBMValues=np.array([])
for day in BBDResponse:
    BBMValues=np.append(BBMValues,np.array([BBDResponse[day]["Real Middle Band"]]))

BBMValues=BBMValues.astype(np.float) 
BBMValues=np.delete(BBMValues,[0])

BBMValues=pd.Series(BBMValues)

stocks.insert(loc=8,column="BBM",value=BBMValues)



#Volume
volumeResponse=get_stock_infoV('TIME_SERIES_DAILY_ADJUSTED',ticker,'full')

volumeResponse=volumeResponse["Time Series (Daily)"]

#VALUE
closeValues=np.array([])
volumeValues=np.array([])
ii=0
while ii<(len(RSIAverages)+1):
    for day in volumeResponse:
        closeValues=np.append(closeValues,np.array([volumeResponse[day]["5. adjusted close"]]))
        volumeValues=np.append(volumeValues,np.array([volumeResponse[day]["6. volume"]]))
        ii=ii+1
closeValues=closeValues.astype(np.float)
changes=np.diff(closeValues)
closeValues=np.delete(closeValues, [0])
changesP=np.divide(changes,closeValues)*(-100)
volumeValues=volumeValues.astype(np.float)

volumeValues=np.delete(volumeValues,[0])
volumeValues=pd.Series(volumeValues)
changesP=pd.Series(changesP)

stocks.insert(loc=9,column="Volume",value=volumeValues)
stocks.insert(loc=10,column="pChange",value=changesP)

#MACHINE LEARNING STUFF
stocks=stocks.dropna()
print(stocks.isnull().sum())
bins=[-52,0.8, 14]
group_names=['bad','good']
stocks['pChange']=pd.cut(stocks['pChange'], bins=bins, labels=group_names)
print(stocks['pChange'].unique())
print(stocks['pChange'].value_counts())


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
pred_rfc=rfc.predict(X_test)

'''
#PICKLE
filename='algorithm'
outfile=open(filename,'wb')
pickle.dump(rfc,outfile)
outfile.close()

infile=open(filename,'rb')
new_rfc=pickle.load(infile)
'''

print(classification_report(y_test, pred_rfc))
print(confusion_matrix(y_test, pred_rfc))


#Moving Average Convergence/Divergence ('MACD',ticker,'daily','i','close') - V then H
#Relative Strength Index ('RSI',ticker,'daily','50','close')
#Simple Moving Average ('SMA',ticker,'daily','50','close')
#Stochastic Oscillator ('STOCH',ticker,'daily','i','i')
#On Balance Volume ('OBV',ticker,'daily','i','i')
#Average Directional Movement ('ADX',ticker,'daily','50','i')
#Bollinger Bands ('BBANDS',ticker,'daily','50','close') - D then M
#Volume 


toTest=np.array([])

#get MACD
MACDVResponse=get_stock_info('MACD',ticker,'daily','i','close')
MACDVResponse=MACDVResponse["Technical Analysis: MACD"]
ii=0
for day in MACDVResponse:
    if ii==1:
        break
    toTest=np.append(toTest,np.array([MACDVResponse[day]["MACD"]]))
    toTest=np.append(toTest,np.array([MACDVResponse[day]["MACD_Hist"]]))
    ii=ii+1

#get RSI
RSIResponse=get_stock_info('RSI',ticker,'daily','50','close')
RSIResponse=RSIResponse["Technical Analysis: RSI"]
ii=0
toReturn=0
for day in RSIResponse:
    if ii==3:
        break
    num=RSIResponse[day]["RSI"]
    toReturn=toReturn+float(num)
    ii=ii+1
toReturn=toReturn/3
toTest=np.append(toTest,np.array(toReturn))

#get SMA
time.sleep(60)
SMAResponse=get_stock_info('SMA',ticker,'daily','50','close')
SMAResponse=SMAResponse["Technical Analysis: SMA"]
ii=0
toReturn=0
for day in SMAResponse:
    if ii==3:
        break
    num=SMAResponse[day]["SMA"]
    toReturn=toReturn+float(num)
    ii=ii+1

toReturn=toReturn/3
toTest=np.append(toTest,np.array(toReturn))

#get STOCH
STOCHResponse=get_stock_info('STOCH',ticker,'daily','i','i')
STOCHResponse=STOCHResponse["Technical Analysis: STOCH"]
ii=0
for day in STOCHResponse:
    if ii==1:
        break
    toTest=np.append(toTest,np.array([STOCHResponse[day]["SlowD"]]))
    ii=ii+1

#get OBV
OBVResponse=get_stock_info('OBV',ticker,'daily','i','i')
OBVResponse=OBVResponse["Technical Analysis: OBV"]
ii=0
for day in OBVResponse:
    if ii==1:
        break
    toTest=np.append(toTest,np.array([OBVResponse[day]["OBV"]]))
    ii=ii+1

#get ADX
ADXResponse=get_stock_info('ADX',ticker,'daily','50','i')
ADXResponse=ADXResponse["Technical Analysis: ADX"]
ii=0
for day in ADXResponse:
    if ii==1:
        break
    toTest=np.append(toTest,np.array([ADXResponse[day]["ADX"]]))
    ii=ii+1

#get BBANDS
BBDResponse=get_stock_info('BBANDS',ticker,'daily','50','close')
BBDResponse=BBDResponse["Technical Analysis: BBANDS"]
ii=0
for day in BBDResponse:
    if ii==1:
        break
    diff=float(BBDResponse[day]["Real Upper Band"])-float(BBDResponse[day]["Real Middle Band"])
    toTest=np.append(toTest,np.array([diff]))
    toTest=np.append(toTest,np.array([BBDResponse[day]["Real Middle Band"]]))
    ii=ii+1

#get Volume
time.sleep(60)
volumeResponse=get_stock_info('TIME_SERIES_DAILY_ADJUSTED',ticker,'i','i','i')
volumeResponse=volumeResponse["Time Series (Daily)"]
ii=0
ends=np.array([])
for day in volumeResponse:
    if ii==1:
        break
    toTest=np.append(toTest,np.array([volumeResponse[day]["6. volume"]]))
    ii=ii+1

toTest=toTest.astype(np.float)
toTest=[toTest.tolist()]
toTest=sc.transform(toTest)
result=rfc.predict(toTest)
print(result)


