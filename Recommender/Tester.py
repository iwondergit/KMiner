#Tester can test the model using the dataset

import torch
from torch.utils.data import DataLoader

class Trainer(object):
    def __init__(self, model, testDataset, batchSize, shuffle = true, num_workers = 0):
        self.data_loader = DataLoader(dataset=testDataset,
                              batch_size=batchSize,
                              shuffle=shuffle,
                              num_workers=0)
        self.model = model
        self.criterion = None
        self.labelType = torch.FloatTensor
    
    def setCriterion(self, lossFun, para):
        self.criterion = lossFun(**para)
        
    def setLabelType(self, type):
        self.labelType = type
    
    def getModel(self):
        return self.model
    
    def test(self, epochTimes):
        if self.criterion == None:
            print("Need to set criterion and optimizer first.")
            return None
        for epoch in range(epochTimes):
            self.model.test()
            print("epoch:", epoch)
            test_loss = 0
            for i, data in enumerate(self.data_loader, 0):
                # get the inputs
                inputs, labels = data 
                labels = labels.type(self.labelType)
                #print(inputs, labels)

                # wrap them in Variable
                inputs, labels = Variable(inputs), Variable(labels)

                # Forward pass: Compute predicted y by passing x to the model
                y_pred = model(inputs)

                # Compute and print loss
                #print(y_pred, labels)
                loss = self.criterion(y_pred, labels)
                #print(labels.data[0])
                #print(y_pred.data[0])
                #print(epoch, i, loss.data[0])
                test_loss += loss
            test_loss /= len(test_loader.dataset)
            print('Average loss: ' + str(test_loss.data[0]))
