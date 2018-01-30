'''

@author: hzdz
'''
import pickle
import numpy as np

class CalMetrics(object):
    '''
    classdocs
    '''


    def __init__(self, fileName):
        '''
        Constructor
        '''
        with open(fileName, 'rb') as file:
            data = pickle.load(file)
            self.keys = data[0]
            self.data = data[1]
    
    def calculate(self, metric, *paras):
        if metric == 'lastC' :
            method = self.calLastC
            metricName = 'lastC'
            source = self.data[:,self.keys["close"]]
        elif metric == 'ma':
            method = self.calMA
            metricName = 'MA' + str(paras[0])
            source = self.data[:,self.keys["close"]]
        elif metric == 'macd':
            method = self.calMACD
            metricName = ['dif', 'dea', 'macd']
            source = self.data[:,self.keys["close"]]
        elif metric == 'HiF':
            method = self.calHighinFuture
            metricName = 'HiF' + str([paras[0]])
            source = self.data[:,self.keys['high']]
        else:
            return
        self.data = np.column_stack((self.data, method(source, paras)))
        if metricName.__class__ == list:
            for metricN in metricName:
                self.keys[metricN] = len(self.keys)
        else:
            self.keys[metricName] = len(self.keys)
    
    def calLastC(self, data, paras):
        lastC = data
        lastC = np.hstack((np.zeros(1), lastC[:-1]))
        return lastC
    
    def calMA(self, data, paras):
        n = paras[0]
        ret = np.cumsum(np.asarray(data, float))
        ret[n:] = ret[n:] - ret[:-n]
        ret[:n-1] = 0
        return np.transpose(ret[:] / n)
    
    def calMACD(self, data, paras):
        if len(paras) == 0:
            paras = [12, 26, 9]
        short = paras[0]
        long = paras[1]
        mid = paras[2]
        dif = self.calEMA(data, short) - self.calEMA(data, long)
        dea = self.calEMA(dif, mid)
        macd = (dif - dea)*2
        return np.column_stack((dif, dea, macd))

    def calEMA(self, data, paras):
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
    
    def calHighinFuture(self, data, paras):
        data = np.asarray(data, float)
        res = [None]*len(data)
        days = paras[0]
        for i in range(len(data)-days):
            res[i] = np.max(data[i+1:i+1+days])
        return np.array(res)

if __name__ == '__main__':
    inFilePath = "E:\python study\stock\data\DayLine\\TrainingSet\\SH#600000.pkl"
    outFilePath = "E:\python study\stock\data\DayLine\\TrainingSet\\SH#600000_1.pkl"
    cal = CalMetrics(inFilePath)
    cal.calculate('HiF', 3)
    print(cal.data)
    with open(outFilePath, 'wb') as file: 
        pickle.dump([cal.keys,cal.data], file, pickle.HIGHEST_PROTOCOL)