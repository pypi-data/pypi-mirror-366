import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

class Softmax(nn.Module):
    def __init__(self,input_size,output_size,regulazation,lambda_reg):
        super(Softmax,self).__init__()
        self.linear=nn.Linear(input_size,output_size)
        self.regulazation=regulazation
        self.lambda_reg=lambda_reg
    def forward(self,x):
        return self.linear(x)
    def coumpute_res_loss(self):
        if self.regulazation=='l1':
            return self.lambda_res*torch.norm(self.linear.weight,p=1)
        elif self.regulazation=='l2':
            return self.lambda_res*torch.norm(self.linear.weight,p=2)
def train_model(model,train_loader,loss,optimizer,device,epochs=1000):
    model.train()
    for epoch in range(epochs):
        total_loss=0
        for batch_x,batch_y in train_loader:
            batch_x,batch_y=batch_x.to(device),batch_y.to(device)
            out_put=model(batch_x)
            loss=loss(out_put,batch_y)
            reg_loss=model.coumpute_res_loss()
            loss=total_loss+reg_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss+=loss.item()
        if (epoch+1)%100==0:
            print(f'Epoch[{epoch+1}/{epochs}]：loss={loss:.4f}')

def evaluate_model(model,x_test,y_test,device):
    with torch.no_grad:
        x_test_tensor=torch.tensor(x_test,dtype=torch.float64).to(device)
        _,y_pre=torch.max(model(x_test_tensor),dim=1)
        y_pre=y_pre.cpu().numpy()
    accuracy=accuracy_score(y_test,y_pre)
    print(f'准确率:{accuracy:.4f}')

