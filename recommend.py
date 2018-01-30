# recommend a stock 

from datetime import datetime, timedelta
from Utils.SQLdb import SQLdb
from Utils.dataTrans import addNewMetrics, genRecord
from Recommender.Recommender import Recommender
from Recommender.Model3 import Model
import pickle

sourceConnPara = {'dbPath': 'stock.db'}

x_index = [1, 2, 3, 4, 6, 7, 8, 9, 10, 12, 13, 14]
y_index = [-2]
modelFileName = 'model3.pk'

def getRawData(sDB, endDate, startDate = '2010/01/01', kLines = None):
    records = {}
    try:
        sDB.connect()
        stockInfo = sDB.select('lu_stock', '*')
        if(kLines):
            for stock in stockInfo:
                records1 = sDB.select(stock[1], '*', "datetime <= '" + endDate + "'")
                records[stock[1]] = records1[-kLines:]
        else:
            for stock in stockInfo:
                records[stock[1]] = sDB.select(stock[1], '*', "datetime >= '" + startDate + "' and '" + "datetime <= '" + endDate + "'")
    finally:
        sDB.close()
    return records
        
def valueFun(l):
    #print(l)
    w = [-18, -12, -6, 0, 6, 12, 18]
    lp = sum(l[:3])<0.25
    return lp*sum([a*b for a, b in zip(w, l)])
    
def main():
    sDB = SQLdb('sqlite', sourceConnPara)
    now = datetime.utcnow()
    now = datetime(2017, 10, 13, 10)
    kLines = 200
    with open(modelFileName, 'rb') as fp:
        model = pickle.load(fp)
    finalRecords = []

    
    #check if we need to get current data
    if (now.hour + 8) < 16:
        #get new data from web
        
        #get old data from DB
        endDate = (now - timedelta(days = 1)).date().strftime("%Y/%m/%d")
        records = getRawData(sDB, endDate = endDate, kLines=kLines)
    else:
        #get data from DB
        endDate = now.date().strftime("%Y/%m/%d")
        records = getRawData(sDB, endDate = endDate, kLines=kLines)
        #print(records['SZ300585'])
        for stock in records.keys():
            if len(records[stock]) < kLines or records[stock][-1][1] < (now - timedelta(days = 30)).date().strftime("%Y/%m/%d"):
                continue
            #ignore those percent larger than 9.5
            #if records[stock][-1][5] > records[stock][-2][5]*1.095:
            #    continue
            keys = ['open', 'high', 'low', 'close', 'volumn', 'amount']
            [newKeys, newRecords] = addNewMetrics(keys, records[stock])
            record = genRecord(newRecords[-10:], x_index, None, 7, None)
            record.insert(0, str(stock))
            #if stock == "SH600565":
                #print(newRecords[-10:])
                #print(record)
            finalRecords.append(record)
    recommender = Recommender(finalRecords, model)
    res = recommender.recommend(valueFun, [0, 18], top=20)
    print(res)
    
main()
