#!/usr/bin/env python
# -*-coding:utf-8 -*-
""" Script for training pytorch Resnets


"""

import os
import sys
import argparse
from utils import get_dataset

import logging                                                                      # NOQA E402
import numpy as np                                                                  # NOQA E402
import pandas as pd                                                                 # NOQA E402
import utils

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

THISFILE_PATH = os.path.abspath(__file__)
DATAIN_PATH = os.path.join( os.path.abspath(os.path.join(THISFILE_PATH, os.pardir, os.pardir)), 'datain')

def main(args):

    # Handle device used
    assert args.device in ['cpu', 'gpu'], "Please select only 'cpu' or 'gpu' as device"
    device_name = args.device
    if args.device == 'gpu':
        # check if GPU is available
        if torch.cuda.is_available():
            device_name = f"{device_name}:0"
        else:
            raise ValueError("There is no gpu available, please use cpu")
    device = torch.device(device_name)

    # Load data
    (x_train, y_train), _ = get_dataset(args.dataset)

    # Convert data to PyTorch tensors and create DataLoader
    batch_size = int(args.batch_size)
    data_tensor = torch.from_numpy(x_train).permute(0, 3, 1, 2).float()
    labels_tensor = torch.tensor(y_train, dtype=torch.long)
    train_set = torch.utils.data.TensorDataset(data_tensor, labels_tensor)
    trainloader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=False, num_workers=2)

    # Load ResNet model
    if args.resnet_size == 'resnet50':
        model = torchvision.models.resnet50(pretrained=False)
    elif args.resnet_size == 'resnet101':
        model = torchvision.models.resnet101(pretrained=False)
    elif args.resnet_size == 'resnet152':
        model = torchvision.models.resnet152(pretrained=False)
    else:
        print('Unsupported ResNet model')
        quit()

    # Change the output layer to have 10 classes instead of 1000
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(np.unique(y_train)))

    # Send model to GPU(CPU)
    model.to(device)

    # Define the loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # Train the model
    n_epochs = int(args.epochs)
     
    for epoch in range(n_epochs):  # number of epochs
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            # Get the inputs and labels
            inputs, labels = data

            # send data to GPU
            inputs, labels = inputs.to(device), labels.to(device)

            # Zero the parameter gradients
            optimizer.zero_grad()

            # Forward + backward + optimize
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # Print statistics
            running_loss += loss.item()
            if i % 100 == 99:    # print every 100 mini-batches
                print('[%d, %5d] loss: %.3f' %
                    (epoch + 1, i + 1, running_loss / 100))
                running_loss = 0.0

    print('Finished Training')


def parse_args():
    '''
    Parses all script arguments.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset', type=str, default=None,
                        help='Dataset to train NN on, one in ["MNIST", "CIFAR10", "CIFAR100"]')
    parser.add_argument('--resnet_size', type=str, default='resnet50',
                        help='Size for Resnet, one in ["resnet50", "resnet101", "resnet152"]')
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of epochs to train the NN, if not provided set to default')
    parser.add_argument('--batch_size', type=int, default=128,
                        help='Batch size, if not provided set to default')
    parser.add_argument('--device', type=str, default='GPU',
                        help='Device: cpu or gpu')
    # parser.add_argument('--out_dir', type=str, default=None,
    #                     help='Path where to save training data')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)