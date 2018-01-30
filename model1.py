import torch
import numpy as np
from torch.autograd import Variable
from Utils.SQLdb import SQLdb
import random
from torch.utils.data import Dataset, DataLoader
import pickle
from pathlib import Path
from Recommender.Model2 import Model

#model parameters here
batchSize = 1
epochTimes = 100
epochSize = 200000
testSize = 10000


def getData(db, tbName, size, maxSize, threshold):
    ids = [random.randrange(maxSize) for t in range(size)]
    if len(ids)>1:
        records=db.select(tbName, '*', 'id in ' + str(tuple(ids)))
    else:
        records=db.select(tbName, '*', 'id = ' + str(ids[0]))
    #print(records[0])
    x = [list(t[3:-1]) for t in records]
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
    def __init__(self, test = 0):
        sourceConnPara = {'dbPath': 'trainCiF1.db'}
        if(test):
            tbName = 'test'
        else:
            tbName = 'train'
        threshold = [-7, -3, -1, 1, 3, 7]

        #connect to DB
        db = SQLdb('sqlite', sourceConnPara)
        try:
            db.connect()
            trainRecordSize = db.select(tbName, 'count(*)')
            trainRecordSize = trainRecordSize[0][0]
            self.x_data, self.y_data = getData(db, tbName, epochSize, trainRecordSize, threshold)
            self.len = len(self.y_data)
            self.x_data = torch.FloatTensor(self.x_data)
            self.y_data = torch.FloatTensor(self.y_data)
        finally:    
            db.close()

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len

# our model
model = Model()

#load from file
if(Path('model2.pk').is_file()):
    with open('model2.pk', 'rb') as fp:
        model = pickle.load(fp)

# Construct our loss function and an Optimizer. The call to model.parameters()
# in the SGD constructor will contain the learnable parameters of the two
# nn.Linear modules which are members of the model.
criterion = torch.nn.MSELoss(size_average=True)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

#get test data
testDataset = StockDataset(1)
test_loader = DataLoader(dataset=testDataset,
                              batch_size=batchSize,
                              shuffle=True,
                              num_workers=0)

# Training loop
for epoch in range(epochTimes):
    model.train()
    trainDataset = StockDataset()
    train_loader = DataLoader(dataset=trainDataset,
                              batch_size=batchSize,
                              shuffle=True,
                              num_workers=1)
    print("epoch:", epoch)
    for i, data in enumerate(train_loader, 0):
        # get the inputs
        inputs, labels = data 
        labels = labels.type(torch.FloatTensor)
        #print(inputs, labels)

        # wrap them in Variable
        inputs, labels = Variable(inputs), Variable(labels)

        # Forward pass: Compute predicted y by passing x to the model
        y_pred = model(inputs)

        # Compute and print loss
        #print(y_pred, labels)
        loss = criterion(y_pred, labels)
        #print(labels.data[0])
        #print(y_pred.data[0])
        #print(epoch, i, loss.data[0])

        # Zero gradients, perform a backward pass, and update the weights.
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

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


    #write the model to file
    with open('model2.pk', 'wb') as fp:
        pickle.dump(model, fp)
    print("saved.")

        


