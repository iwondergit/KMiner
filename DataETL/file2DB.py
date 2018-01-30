#read data from files and save to sqlite DB

import os
import time
import datetime
import sys
sys.path.append('C:\\python\\Utils')
from SQLdb import SQLdb

def main():
    
    connPara = {'dbPath': 'stock.db'}
    db = SQLdb('sqlite', connPara)
    try:
        db.connect()
        db.create('lu_stock', ['id', 'code', 'dataCount', 'startDate'], ['INTEGER', 'TEXT', 'INTEGER', 'TEXT'])
        filePath = "C:\\python\\DataETL\\Data\\20171020"
        id = 0
        for filename in os.listdir(filePath):
            if(filename.startswith("SH") or filename.startswith("SZ")):
                id += 1
                with open(os.path.join(filePath, filename), 'r') as fp:
                    cols = ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volumn', 'amount']
                    coltypes = ['INTEGER', 'TEXT', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL', 'REAL']
                    tableName = filename.split('.')[0].replace('#', '')
                    db.create(tableName, cols, coltypes)
                    recordCount = 0
                    for line in fp:
                        value = line.replace('\n', '').split('\t')
                        if(value[0].startswith('20') or value[0].startswith('19')):
                            if int(value[5]) == 0:
                                continue
                            recordCount += 1
                            value[2:-1] = [float(nm) for nm in value[2:-1]]
                            value.insert(0, time.mktime(datetime.datetime.strptime(value[0], "%Y/%m/%d").timetuple()))
                            db.insert(tableName, tuple(value))
                            if(recordCount == 1):
                                startDate = value[0]
                    db.insert('lu_stock', (id, tableName, recordCount, startDate))
                    db.commit()
                    #print(db.select(tableName, '*'))
            print(tableName + " finished.\n")
    finally:
        db.close()
main()
