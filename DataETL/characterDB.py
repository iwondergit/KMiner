#read raw data from DB and add additional metrics



import os
import time
import datetime
import sys
sys.path.append('C:\\python\\Utils')
from dataTrans import addNewMetrics
from SQLdb import SQLdb
import numpy as np

def addToDB(sourceConnPara, targetConnPara):
    sDB = SQLdb('sqlite', sourceConnPara)
    tDB = SQLdb('sqlite', targetConnPara)
    recordLimit = 100
    dateLimit = '2012/01/01'
    try:
        sDB.connect()
        tDB.connect()
        
        tDB.create('lu_stock', ['id', 'code', 'recordCount', 'startDate'], ['INTEGER', 'TEXT', 'INTEGER', 'TEXT'])
        stockInfo = sDB.select('lu_stock', '*')
        stockID = 0
        for stock in stockInfo:
            if(stock[2] < recordLimit):
                continue
            stockID += 1
            records = sDB.select(stock[1], '*')
            keys = ['open', 'high', 'low', 'close', 'volumn', 'amount']
            [keys, recordsData] = addNewMetrics(keys, records)
            keys.insert(0, 'id')
            recordCount1 = (sDB.select(stock[1], 'count(*)', "datetime < " + dateLimit))[0][0]
            recordsData = recordsData[recordCount1:-20]
            recordCount = len(recordsData)
            recordsData = np.column_stack((list(range(recordCount)), recordsData))
            startDate = recordsData[0][0]
            tDB.insert('lu_stock', (stockID, stock[1], recordCount, startDate))
            tDB.create(stock[1], keys, ['INTEGER', 'TEXT'] + ['REAL'] * (len(keys)-2))
            tDB.insert(stock[1], recordsData.tolist())
            print(stock[1])
        tDB.commit()
        
    finally:
        sDB.close()
        tDB.close()
        

def main():
    sourceConnPara = {'dbPath': 'stock.db'}
    targetConnPara = {'dbPath': 'HS4MA_MACD.db'}
    addToDB(sourceConnPara, targetConnPara)
    
main()
