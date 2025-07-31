import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from PIL import Image
from RBFInterpolator import RBFInterpolator
from torchvision.utils import save_image

def positional_encoding(L=5):
    def EmbeddingFunction(x):
        FrequencyRepresentation = [x]
        for y in range(L):
            FrequencyRepresentation += [torch.sin(2 ** y * x), torch.cos(2 ** y * x)]
        return torch.cat(FrequencyRepresentation, dim=1)

    return EmbeddingFunction, 2 * L + 1

class LearnedRadialBasisFunction(nn.Module):
    def __init__(self, dims=[16, 32, 64]):
        super(LearnedRadialBasisFunction, self).__init__()
        
        self.pos_enc, self.pos_enc_dim = positional_encoding(L=5)

        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(self.pos_enc_dim, dims[0]))

        for i in range(len(dims) - 1):
            self.layers.append(nn.Linear(dims[i], dims[i + 1]))
            self.layers.append(nn.ReLU())

        self.output = nn.Linear(dims[-1], 1)
    
    def forward(self, x):
        x = self.pos_enc(x)
        for layer in self.layers:
            x = layer(x)
        return self.output(x)

def train():

    return

if __name__ == "__main__":
    train()
