import torch
from torch import nn
from torch.nn import functional as F

__all__ = ['MHA']

class MHA(nn.Module):
    """
    Given Q,K,V and mask (Optional), it returns the output of Multi Head Attention.
    Args:
        x : Input
        mask : Mask (Optional)
    Returns:
        output : Output of Multi Head Attention
    """
    def __init__(self,d_model,num_head,seq_len=128,dropout=None):
        """
        Args:
            d_model(int) : dimension of model. Embeddings dimension
            num_head(int) : number of heads
            seq_len(int, optional) : sequence length. Context length of model. Words in a sentence. Longer the sequence, longer the context.
            dropout(float, optional) : dropout rate
        """
        super().__init__()
        self.d_model=d_model
        self.num_head=num_head
        self.d_k=d_model//num_head
        self.q = nn.Linear(d_model,d_model)
        self.k = nn.Linear(d_model,d_model)
        self.v = nn.Linear(d_model,d_model)

        if dropout is not None:
            self.dropout = nn.Dropout(dropout)
        else:
            self.dropout = nn.Dropout(0)
        
        self.out = nn.Linear(d_model,d_model)

    def forward(self,x,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of Multi Head Attention.
        Args:
            x : Input
            mask : Mask (Optional)
        Returns:
            output : Output of Multi Head Attention
        """ 
        B,seq_len,d_model = x.shape
        q = self.q(x)
        k = self.k(x)
        v = self.v(x)
        
        q = q.view(B,seq_len,self.num_head,self.d_k)
        k = k.view(B,seq_len,self.num_head,self.d_k)
        v = v.view(B,seq_len,self.num_head,self.d_k)

        q = q.transpose(1,2) ## [B,num_head,seq_len,d_k] - putting heads ahead of sequence length
        k = k.transpose(1,2)
        v = v.transpose(1,2)

        if mask is None:
            mask = torch.tril(torch.ones((seq_len, seq_len), device=x.device))
            mask = mask.unsqueeze(0).unsqueeze(0) ## [1,1,seq_len,seq_len]

        output,attn_weights = self.scaled_dot_product_attention(q,k,v,mask)

        output = output.transpose(1,2)
        output = output.contiguous().view(B,seq_len,d_model) ## [B,seq_len,d_model] - merging back the MHA heads into a single tensor

        output = self.out(output)
        output = self.dropout(output)

        return output,attn_weights
    
    def scaled_dot_product_attention(self,q,k,v,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of Scaled Dot Product Attention.
        Args:
            q : Query
            k : Key
            v : Value
            mask : Mask (Optional)
        Returns:
            output : Output of Scaled Dot Product Attention
        """
        d_k = q.size(-1)

        scores = q @ k.transpose(-2,-1) / torch.sqrt(torch.tensor(d_k))

        attn_scores = scores.masked_fill(mask==0,float('-inf'))
        attn_weights = F.softmax(attn_scores,dim=-1)
        attn_weights = self.dropout(attn_weights)
        output = attn_weights @ v
        
        return output,attn_weights

class MQA(nn.Module):
    """
    Given Q,K,V and mask (Optional), it returns the output of Multi Query Attention.
    Args:
        x : Input
        mask : Mask (Optional)
    Returns:
        output : Output of Multi Query Attention
    """
    def __init__(self,d_model,num_head,seq_len=None,dropout=None):
        super().__init__()
        self.d_model=d_model
        self.num_head=num_head
        self.d_k=d_model//num_head
        self.q = nn.Linear(d_model,d_model)
        self.k = nn.Linear(d_model,d_model)
        self.v = nn.Linear(d_model,d_model)

        if dropout is not None:
            self.dropout = nn.Dropout(dropout)
        else:
            self.dropout = nn.Dropout(0)
        
        self.out = nn.Linear(d_model,d_model)
    
    def forward(self,x,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of Multi Query Attention.
        Args:
            x : Input
            mask : Mask (Optional)
        Returns:
            output : Output of Multi Query Attention
        """
        B,seq_len,d_model = x.shape
        q = self.q(x)
        k = self.k(x)[:,0:1,:] ## [B,1,d_model] - taking only the first token as key
        v = self.v(x)[:,0:1,:] ## [B,1,d_model] - taking only the first token as value
        
        q = q.view(B,seq_len,self.num_head,self.d_k)
        k = k.view(B,1,self.num_head,self.d_k) ## now it can be reshaped based on taking the 1st token as sequence length
        v = v.view(B,1,self.num_head,self.d_k)

        q = q.transpose(1,2)
        k = k.transpose(1,2)
        v = v.transpose(1,2)

        if mask is None:
            mask = torch.tril(torch.ones((seq_len, seq_len), device=x.device))
            mask = mask.unsqueeze(0).unsqueeze(0) ## [1,1,seq_len,seq_len]

        output,attn_weights = self.new_kv_attention(q,k,v,mask)

        output = output.transpose(1,2)
        output = output.contiguous().view(B,seq_len,d_model)

        output = self.out(output)
        output = self.dropout(output)

        return output,attn_weights

    def new_kv_attention(self,q,k,v,mask=None):
        """
        Given Q,K,V and mask (Optional), it returns the output of New KV Attention.
        Args:
            q : Query
            k : Key
            v : Value
            mask : Mask (Optional)
        Returns:
            output : Output of New KV Attention
        """
        d_k = q.size(-1)
        
        scores = (q@k.transpose(-2,-1))/torch.sqrt(torch.tensor(d_k))* (self.num_head**-0.5) ##scaling factor
        
        if mask is not None:
            scores = scores.masked_fill(mask==0,float('-inf'))

        scores = scores.softmax(dim=-1)

        scores  = self.dropout(scores)
        output = scores@v
        
        return output,scores

