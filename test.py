import torch
import numpy as np
from torch.autograd import Variable
from Utils.SQLdb import SQLdb
import random
from torch.utils.data import Dataset, DataLoader
import pickle
from pathlib import Path

#model parameters here
batchSize = 1
epochTimes = 10
testSize = 10000


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

def getData(db, size, threshold):
    records=db.select('train', '*', "date > '20170101'")
    #print(records[0])
    x = [normalize(list(t[3:-1])) for t in records]
    #print(x[0])
    y1 = [(t[-1]-1) for t in records]
    y=[]
    for v in y1:
        res = [0] * len(threshold)
        res.append(1)
        for i, t in enumerate(threshold):
            if v*100 < t:
                res[i] = 1
                res[len(threshold)] = 0
                break
        y.append(res)
    return (x, y)

class StockDataset(Dataset):
    """ Diabetes dataset."""

    # Initialize your data, download, etc.
    def __init__(self):
        sourceConnPara = {'dbPath': 'train.db'}
        tbName = 'train'
        threshold = [3, 7, 10, 15, 20]

        #connect to DB
        db = SQLdb('sqlite', sourceConnPara)
        try:
            db.connect()
            self.x_data, self.y_data = getData(db, epochSize, threshold)
            self.len = len(self.y_data)
            self.x_data = torch.FloatTensor(self.x_data)
            self.y_data = torch.FloatTensor(self.y_data)
        finally:    
            db.close()

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len





class Model(torch.nn.Module):

    def __init__(self):
        """
        In the constructor we instantiate two nn.Linear module
        """
        super(Model, self).__init__()
        self.l1 = torch.nn.Linear(110, 200)
        self.l2 = torch.nn.Linear(200, 100)
        self.l3 = torch.nn.Linear(100, 40)
        self.l4 = torch.nn.Linear(40, 10)
        self.l5 = torch.nn.Linear(10, 6)

        self.sigmoid = torch.nn.Sigmoid()
        self.softmax = torch.nn.Softmax()
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        """
        In the forward function we accept a Variable of input data and we must return
        a Variable of output data. We can use Modules defined in the constructor as
        well as arbitrary operators on Variables.
        """
        out1 = self.sigmoid(self.l1(x))
        out2 = self.relu(self.l2(out1))
        out3 = self.sigmoid(self.l3(out2))
        out4 = self.sigmoid(self.l4(out3))
        y_pred = self.softmax(self.l5(out4))
        return y_pred

#load from file
if(Path('model1.pk').is_file()):
    fp = open('model1.pk', 'rb')
    model = pickle.load(fp)
    fp.close()


#get test data
testDataset = StockDataset()
test_loader = DataLoader(dataset=testDataset,
                              batch_size=batchSize,
                              shuffle=True,
                              num_workers=0)

# Training loop
for epoch in range(epochTimes):

    #test the result on test set
    model.eval()
    test_loss = 0
    correct = 0
    for i, data in enumerate(test_loader, 0):
        # get the inputs
        inputs, labels = data 
        labels = labels.type(torch.FloatTensor)

        # wrap them in Variable
        inputs, labels = Variable(inputs), Variable(labels)

        # Forward pass: Compute predicted y by passing x to the model
        y_pred = model(inputs)
        if(i<10):
            print(labels.data[0])
            print(y_pred.data[0])

        # Compute and print loss
        loss = criterion(y_pred, labels)
        test_loss += loss

    test_loss /= len(test_loader.dataset)
    print('Average loss after ' + str(epoch) + ': ' + str(test_loss.data[0]))

   


