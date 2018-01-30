#read raw data from DB and add additional metrics



import os
import time
import datetime
import sys
sys.path.append('C:\\python\\Utils')
from dataTrans import genRecord
from SQLdb import SQLdb
import numpy as np
import random

def getTrainTestSet(sourceConnPara, targetConnPara):
    sDB = SQLdb('sqlite', sourceConnPara)
    trainDB = SQLdb('sqlite', targetConnPara)

    testRate = 0.05
    kLineN = 10
    x_index = [2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15]
    x_label = ['open', 'high', 'low', 'close', 'amount', 'MA5', 'MA10', 'MA20', 'DIF', 'DEA', 'MACD']
    y_index = [-2]
    y_label = ['CiF3']
    xRef = 8
    yRef = 5
    
    try:
        sDB.connect()
        trainDB.connect()
        
        rowHeaders = ['id', 'code', 'datetime']
        rowTypes = ['INTEGER', 'TEXT', 'TEXT']
        for i in range(kLineN):
            label = 'D' + str(i+1)
            rowHeaders += [t + label for t in x_label]
            rowTypes += ['REAL'] * len(x_label)
        rowHeaders += y_label
        rowTypes += ['REAL']
        trainDB.create('train', rowHeaders, rowTypes)
        trainDB.create('test', rowHeaders, rowTypes)
        
        stockInfo = sDB.select('lu_stock', '*')
        trainID = 0
        testID = 0
        for stock in stockInfo:
            records = sDB.select(stock[1], '*')
            if records[0][8] == 0:
                records = records[60:]
            for i in range(len(records)-kLineN):
                recordSlice = records[i:i+kLineN]
                if(sum(sum(t<=0 for t in ta[2:5]) for ta in recordSlice) > 0): #abandon the record since there're 0 and negative in it
                    i = i + kLineN
                else:
                    record = genRecord(recordSlice, x_index, y_index, xRef, yRef)
                    record.insert(0, stock[1])
                    record.insert(1, records[i+kLineN-1][1])
                    if(random.random() > testRate):
                        record.insert(0, trainID)
                        trainDB.insert('train', tuple(record))
                        trainID+=1
                    else:
                        record.insert(0, testID)
                        trainDB.insert('test', tuple(record))
                        testID+=1
            print(stock[1])
            trainDB.commit()
        
    finally:
        sDB.close()
        trainDB.close()

def main():
    sourceConnPara = {'dbPath': 'HS4MA_MACD.db'}
    targetConnPara = {'dbPath': 'trainCiF3.db'}
    getTrainTestSet(sourceConnPara, targetConnPara)
    
main()
