#get future prices from sina

from Utils.Scraper import Scraper
import threading

stockList = ["JM1801", "RB1801"]
baseURL = "http://hq.sinajs.cn/list="

def parseFunc(instr):
    dict = {}
    splits =  str(instr).split('\"')[1].split(',')
    dict['code'] = splits[0]
    dict['price'] = float(splits[8])
    dict['closePrice'] = float(splits[10])
    dict['abs_diff'] = dict['price'] - dict['closePrice']
    dict['rel_diff'] = round(dict['abs_diff'] / dict['closePrice'] * 10000)/100
    return dict

scraperDict = {}
for stock in stockList:
    scraperDict[stock] = Scraper(baseURL + stock, parseFunc = parseFunc)

def printprice():
    threading.Timer(60, printprice).start()
    dataList = []
    for stock in stockList:
        data = scraperDict[stock].getRealTimeData()
        dataList.append(data["rel_diff"])
    print(dataList)

printprice()
