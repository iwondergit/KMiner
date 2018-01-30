import torch
import numpy as np
from torch.autograd import Variable

class Model(torch.nn.Module):

    def __init__(self):
        """
        In the constructor we instantiate two nn.Linear module
        """
        super(Model, self).__init__()
        self.l1 = torch.nn.Linear(110, 200)
        self.l2 = torch.nn.Linear(200, 50)
        self.l3 = torch.nn.Linear(50, 6)

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
        out2 = self.sigmoid(self.l2(out1))
        #out3 = self.sigmoid(self.l3(out2))
        #out4 = self.sigmoid(self.l4(out3))
        #out5 = self.sigmoid(self.l5(out4))
        y_pred = self.softmax(self.l3(out2))
        return y_pred

