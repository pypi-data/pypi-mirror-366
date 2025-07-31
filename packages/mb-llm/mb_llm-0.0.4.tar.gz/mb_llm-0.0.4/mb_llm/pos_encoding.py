import torch

__all__ = ['pos_class']

class pos_class():
    """
    Class for positional encoding for LLM's
    Args:
        pos_type : type of positional encoding required. Default : absolute. 
                    {'absolute','relative','rope'}
                    If None, then no positional encoding is applied
    """
    def __init__(self,pos_type='absolute',**kwargs):
        self.pos_type=pos_type
        if self.pos_type=='absolute':
            return self._sinosoidal_pos(**kwargs)
        elif self.pos_type=='relative':
            return self._relative_pos(**kwargs)
        elif self.pos_type=='rope':
            return self._rope_pos(**kwargs)
        else:
            print("Running without positional encoding")
            pass

    def _sinosoidal_pos(self,seq_len=None,d_model=None,dtype=torch.float32):
        """
        Args:
            seq_len : sequence length. Context length of model
            d_model : dimension of model. Model dimension
            dtype : data type of positional encoding
        Returns:
            pos_enc : positional encoding
        """

        pos = torch.arange(seq_len,dtype=dtype).unsqueeze(1) ## position of token
        i_enc = torch.arange(0,d_model,dtype=dtype).unsqueeze(0) ## even indices
        angle_rates = 1 / torch.pow(10000, (i_enc/ d_model)) ## angle rates
        angle_rads  = pos*angle_rates ## angle rates
        
        pos_enc=torch.zeros((seq_len,d_model),dtype=dtype) ## positional encoding
        pos_enc[:,0::2]=torch.sin(angle_rads[:,0::2]) ## even indices
        pos_enc[:,1::2]=torch.cos(angle_rads[:,1::2]) ## odd indices

        return pos_enc
        

    def _relative_pos(self,bais_method=True):
        """
        Applied at each step in Attention mechanism during trianing.
        Args:
            bais_method : bais method to be used. Default : True. (Instead of add at key value, we add bais)
        """
        pass

    def _rope_pos(self):
        """
        Applied at each step in Attention mechanism during trianing.
        """
        pass
