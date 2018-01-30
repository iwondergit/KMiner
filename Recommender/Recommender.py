#A recommender can recommend some records based on the model and input records
from torch.autograd import Variable
import torch
import numpy as np

class Recommender(object):
    
    def __init__(self, records, model):
        self.records = records
        self.model = model
        
    def recommend(self, fun, range, top=None):
        resRecords = []
        for record in self.records:
            x = torch.from_numpy(np.array([record[1:]], dtype='float'))
            #print(x)
            x = Variable(x.type(torch.FloatTensor))
            y = self.model.forward(x)
            res = fun(list(y.data[0]))
            if res > range[0] and res < range[1]:
                resRecords.append([record[0], res, y.data[0]])
            #if record[0] == 'SH600565':
                #print(y.data[0])
        resRecords.sort(key=lambda t: t[1], reverse=True)
        if(top):
            resRecords = resRecords[:top]
        return resRecords
        
