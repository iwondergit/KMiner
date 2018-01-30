#Trainer can train the model using the dataset

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
        self.optimizer = None
        self.labelType = torch.FloatTensor
    
    def setCriterion(self, lossFun, para):
        self.criterion = lossFun(**para)
        
    def setOptimizer(self, optimizer, para):
        self.optimizer = optimizer(self.model.parameter(), **para)
        
    def setLabelType(self, type):
        self.labelType = type
    
    def getModel(self):
        return self.model
    
    def train(self, epochTimes, tester = None):
        if self.criterion == None or self.optimizer == None:
            print("Need to set criterion and optimizer first.")
            return None
        for epoch in range(epochTimes):
            self.model.train()
            print("epoch:", epoch)
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

                # Zero gradients, perform a backward pass, and update the weights.
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
            
            if(tester):
                tester.test()