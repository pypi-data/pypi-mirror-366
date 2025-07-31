from pyclbr import Class
import torch
from torch import nn

__all__ = []


class Activations(nn.Module):
    def __init__(self,activation_type='relu'):
        super().__init__()
        self.activation_type=activation_type
        if self.activation_type=='relu':
            self.activation=nn.ReLU()
        if self.activation_type=='gelu':
            self.activation=nn.GELU()
        if self.activation_type=='silu':
            self.activation=nn.SiLU()

    def forward(self,x):
        return self.activation(x)
    
## original implementation of GLU.
## chuncking input into two parts and applying sigmoid on second part and multiplying with first part
class GLU(nn.Module):
    def __init__(self,dim=-1):
        super().__init__()
        self.dim = dim

    def forward(self,x):
        a,b = x.chunk(2,dim=self.dim)
        return a*torch.sigmoid(b)
    