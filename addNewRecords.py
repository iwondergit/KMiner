#Get the data after COB and store them in DB

from Utils.Scraper import Scraper
from Utils.SQLdb import SQLdb
from datetime import datetime, timedelta, date
from urllib.error import HTTPError
import time
from random import random

def validate(r1, r2):
    if r1[5] > r2['close'] * 1.01 or r1[5] < r2['close'] * 0.99:
        return 0
    else:
        return 1
    

def main():
    sourceConnPara = {'dbPath': 'stock.db'}
    sDB = SQLdb('sqlite', sourceConnPara)
    
    # get coockies
    S1 = Scraper('http://xueqiu.com/', parseFunc = lambda x:x)
    S1.getRealTimeData()
    cookie = S1.getCookie()
    
    # get current timestamp
    now = datetime.utcnow() + timedelta(hours = 8)
    now_timestamp = (now - datetime(1970, 1, 1)) / timedelta(seconds=1)
    
    inconsistency = []
    
    try:
        sDB.connect()
        stockInfo = sDB.select('lu_stock', '*')
        for stock in stockInfo:
            oldRecords = sDB.select(stock[1], '*', 'datetime = (select max(datetime) from ' + str(stock[1]) + ')')
            if len(oldRecords) == 0:
                continue
            latestRecord = oldRecords[0]
            #print(latestRecord)
            query = {'symbol':stock[1],
            'period':'1day',
            'type':'before',
            'begin':(latestRecord[0] - 12*3600)*1000,
            'end':now_timestamp*1000}
            #print(query)
            S2 = Scraper('https://xueqiu.com/stock/forchartk/stocklist.json', parseFunc = lambda x:x)
            S2.setQuery(query)
            S2.setCookie(cookie)
            success = False
            time.sleep(random()*4+1)
            sTime = 1
            while(not success):
                try:
                    records = S2.getRealTimeData()
                    success = True
                except HTTPError as e:
                    print("Failed due to: ", e)
                    print("try again after " + str(sTime) + " seconds.")
                    time.sleep(sTime)
                    if sTime<1000:
                        sTime *= 2
                    else:
                        S1.getRealTimeData()
                        cookie = S1.getCookie()
                        S2.setCookie(cookie)
                    
            kLines = records['chartlist']
            #print(kLines)
            if len(kLines) == 0:
                continue
            if validate(latestRecord, kLines[0]):
                for record in kLines[1:]:
                    volumn = record['volume']
                    if volumn == 0:
                        continue
                    ts = int(record['timestamp']/1000)
                    open = record['open']
                    high = record['high']
                    close = record['close']
                    low = record['low']
                    amount = volumn * sum([open, high, close, low])/4
                    rdate = (date.fromtimestamp(ts) + timedelta(days=1)).strftime("%Y/%m/%d")
                    sDB.insert(stock[1], (ts, rdate, open, high, low, close, volumn, amount))
                sDB.commit()
                print(stock[1])
            else:
                inconsistency.append(stock[1])
                continue
        print('Update is down.\n')
        if(len(inconsistency)):
            print('Followings are not updated due to inconsistency:', inconsistency)
    finally:
        sDB.close()
            
            
main()            