#data transformation functions
import numpy as np

def addNewMetrics(keys, records):
    recordsData = np.array([list(t[2:]) for t in records])
    [keys, recordsData] = calculate(keys, recordsData, 'lastC')
    [keys, recordsData] = calculate(keys, recordsData, 'ma', 5)
    [keys, recordsData] = calculate(keys, recordsData, 'ma', 10)
    [keys, recordsData] = calculate(keys, recordsData, 'ma', 20)
    [keys, recordsData] = calculate(keys, recordsData, 'ma', 60)
    [keys, recordsData] = calculate(keys, recordsData, 'macd')
    [keys, recordsData] = calculate(keys, recordsData, 'HiF', 3)
    [keys, recordsData] = calculate(keys, recordsData, 'HiF', 5)
    [keys, recordsData] = calculate(keys, recordsData, 'CiF', 1)
    [keys, recordsData] = calculate(keys, recordsData, 'CiF', 3)
    [keys, recordsData] = calculate(keys, recordsData, 'CiF', 5)
    recordsData = np.column_stack((np.array([t[1] for t in records]), recordsData))
    keys.insert(0, 'datetime')
    return [keys, recordsData]

def calculate(keys, recordsData, metric, *paras):
    if metric == 'lastC' :
        method = calLastC
        metricName = 'lastC'
        source = recordsData[:,keys.index("close")]
    elif metric == 'ma':
        method = calMA
        metricName = 'MA' + str(paras[0])
        source = recordsData[:,keys.index("close")]
    elif metric == 'macd':
        method = calMACD
        metricName = ['dif', 'dea', 'macd']
        source = recordsData[:,keys.index("close")]
    elif metric == 'HiF':
        method = calHighinFuture
        metricName = 'HiF' + str(paras[0])
        source = recordsData[:,keys.index('high')]
    elif metric == 'CiF':
        method = calCloseinFuture
        metricName = 'CiF' + str(paras[0])
        source = recordsData[:,keys.index('close')]
    else:
        return
    recordsData = np.column_stack((recordsData, method(source, paras)))
    if isinstance(metricName, list):
        for metricN in metricName:
            keys.append(metricN)
    else:
        keys.append(metricName)
    return [keys, recordsData]

def calLastC(data, paras):
    lastC = data
    lastC = np.hstack((np.zeros(1), lastC[:-1]))
    return lastC

def calMA(data, paras):
    n = paras[0]
    ret = np.cumsum(np.asarray(data, float))
    ret[n:] = ret[n:] - ret[:-n]
    ret[:n-1] = 0
    return np.transpose(ret[:] / n)

def calMACD(data, paras):
    if len(paras) == 0:
        paras = [12, 26, 9]
    short = paras[0]
    long = paras[1]
    mid = paras[2]
    dif = calEMA(data, short) - calEMA(data, long)
    dea = calEMA(dif, mid)
    macd = (dif - dea)*2
    return np.column_stack((dif, dea, macd))

def calEMA(data, paras):
    data = np.asarray(data, float)
    if paras.__class__ == list :
        window = paras[0]
    else:
        window = paras
    if len(data) < 2 * window:
        raise ValueError("data is too short")
    a = 2.0 / (window + 1)
    b = (window - 1) / (window + 1)
    y = [0]
    for x in data[1:] :
        y.append(a*x+b*y[-1])
    return np.transpose(np.array(y))

def calHighinFuture(data, paras):
    data = np.asarray(data, float)
    res = [None]*len(data)
    days = paras[0]
    for i in range(len(data)-days):
        res[i] = np.max(data[i+1:i+1+days])
    return np.array(res)    
    
def calCloseinFuture(data, paras):
    data = np.asarray(data, float)
    res = [None]*len(data)
    days = paras[0]
    for i in range(len(data)-days):
        res[i] = np.max(data[i+1:i+1+days])
    return np.array(res)   
    
def normalize(l):
    volMax = max([l[t*11+4] for t in range(10)])
    difMax = max([abs(l[t*11+8]) for t in range(10)])
    deaMax = max([abs(l[t*11+9]) for t in range(10)])
    difdeaMax = max(difMax, deaMax)
    macdMax = max([abs(l[t*11+10]) for t in range(10)])
    for i in range(10):
        l[i*11+0], l[i*11+1], l[i*11+2], l[i*11+3] = [(l[i*11+t]-1)*10 for t in range(4)]
        l[i*11+4] = l[i*11+4]/volMax
        l[i*11+5], l[i*11+6], l[i*11+7] = [(l[i*11+t+5]-1)*10 for t in range(3)]
        l[i*11+8] = l[i*11+8]/difdeaMax
        l[i*11+9] = l[i*11+9]/difdeaMax
        l[i*11+10] = l[i*11+10]/macdMax
    return l
        
def genRecord(records, x, y, xRef, yRef):
    res = []
    for record in records:
        for i in [t for t in x if t != xRef]:
            res.append(record[i]/record[xRef])
    res = normalize(res)
    if(y != None): 
        res.append(record[y[0]]/record[yRef])    
    return res

