## file for tokenizers exprementations

from typing import List,Union
from tqdm import tqdm
import re
from collections import defaultdict
from torch.nn import Embedding
import torch

__all__ = ['tokenizers']

ADVANCED_TOKENIZER_REGEX = re.compile(
    r"""(
        (?:https?://|www\.)\S+                 | # URLs
        \w+(?:'\w+)?                           | # Words with optional apostrophes (e.g., don't)
        \d+\.\d+|\d+                           | # Numbers (float or int)
        [.,!?;:()\[\]{}"“”‘’`~<>^&*+=/\\|@#-]  | # Punctuation and symbols
        [\u2600-\u26FF\u2700-\u27BF\u1F300-\u1F6FF]+ | # Emoji ranges
        \S                                     # Any non-space character
    )""",
    re.VERBOSE | re.UNICODE
)


class tokenizers():
    def __init__(self,tokenizers_type='basic',special_tokens_in_dict=True,d_model=128):
        """
        Given a list of words or string, it returns a dictionary of words and their corresponding ids.
        Args:
            tokenizers_type : type of tokenizers
            special_tokens_in_dict : whether to include special tokens in dictionary
            d_model : dimension of model. Embeddings dimension
        Returns (self):    
            dictionary : dictionary of words and their corresponding ids
            inverse dictionary : inverse dictionary of words and their corresponding ids
            embeddings : embeddings of words
        """
        self.tokenizers_type=tokenizers_type
        self.d_model=d_model
        if special_tokens_in_dict:
            self.dict={'<s>':0,'</s>':1,'<pad>':2,'<mask>':3,'<unk>':4,'<sep>':5,'<cls>':6,'<eos>':7,'<bos>':8}
            self.inv_dict={0:'<s>',1:'</s>',2:'<pad>',3:'<mask>',4:'<unk>',5:'<sep>',6:'<cls>',7:'<eos>',8:'<bos>'}
        else:
            self.dict={}
            self.inv_dict={}
    
    def get_tokenizers(self,*args,**kwargs):
        if self.tokenizers_type=='basic':
            return self._basic_tokens(*args,**kwargs)
        elif self.tokenizers_type=='byte_pair':
            return self._byte_pair_tokens(*args,**kwargs)

    def _pre_tokenizer(self,words:Union[List[str],str]):
        """
        Given a list of words or string, it returns a list of words.
        Args:
            words : list of words or string
        Returns:    
            list_of_words : list of words
        """
        assert isinstance(words, (list, str)), "Input should be a list of words or string"
        if isinstance(words,str):
            words = ADVANCED_TOKENIZER_REGEX.findall(words)
            words = [i.lower() for i in words if i.strip()]
        elif isinstance(words,list):
            words = [ADVANCED_TOKENIZER_REGEX.findall(i) for i in words]
            words = [i.lower() for j in words for i in j if i.strip()]
        return words

    def _basic_tokens(self,words:Union[List[str],str]):
        """
        Given a list of words or string, it returns a dictionary of words and their corresponding ids.
        Args:
            words : list of words or string
        """
        
        assert isinstance(words, (list,str)), "Input should be a list of words or string"
        if len(words)==0:
            raise ValueError("List of words is empty")
        
        words = self._pre_tokenizer(words)

        for i in tqdm(words,desc="Building dictionary",total=len(words)):
            if i not in self.dict:
                self.dict[i]=len(self.dict)  ## adding new word to dictionary. Starts from 9 if special tokens are added
                self.inv_dict[len(self.dict)-1]=i

    def _basic_encoder(self,prompt:Union[List[str],str]):
        """
        Given a list of words, it returns a list of ids.
        Args:
            prompt : list of words or string
        Returns:    
            list_of_prompt : list of ids
        """

        assert isinstance(prompt, (list,str)), "Input should be a list of words or string"
        if isinstance(prompt,str):
            prompt = [i.lower() for i in prompt.split(' ') if i not in ['','\n','\t','\r']]
        elif isinstance(prompt,list):
            prompt = [i.lower() for i in prompt if i not in ['','\n','\t','\r']]

        res=[]
        for i in tqdm(prompt,desc="Encoding prompt",total=len(prompt)):
            if i not in self.dict:
                res.append(self.dict['<unk>'])
            else:
                res.append(self.dict[i])
        return res

    def _basic_decoder(self,prompt_id:List[int]):
        """
        Given a list of ids, it returns a list of words.
        Args:
            prompt_id : list of ids
        Returns:    
            list_of_prompt : list of words
        """

        assert isinstance(prompt_id, list), "Input should be a list of ids"
        res=[]
        for i in tqdm(prompt_id,desc="Decoding prompt",total=len(prompt_id)):
            if i not in self.dict.values():
                res.append(self.dict['<unk>'])
            else:
                res.append(self.inv_dict[i])
        return res

    def _byte_pair_tokens(self,words:Union[List[str],str],max_iter=100):
        """
        Given a list of words or string, it returns a dictionary of words and their corresponding ids using BPE.
        Args:
            words : list of words or string
            max_iter : maximum number of iterations
        """

        assert isinstance(words, (list,str)), "Input should be a list of words or string"
        if len(words)==0:
            raise ValueError("List of words is empty")
        
        words = self._pre_tokenizer(words)
        
        final_pairs=list(self.dict.keys())
        words_new = words.copy()
        words_new = [' '.join(list(i))+' </w>' for i in words_new]
        for _ in tqdm(range(max_iter),total=max_iter):
            pairs = defaultdict(int)
            for i in range(len(words_new)):
                ax = words_new[i].split()  
                for j in range(len(ax)-1):
                    pairs[(ax[j],ax[j+1])]+=1
            best_pair = max(pairs,key=pairs.get)
            final_pairs.append(''.join(best_pair))
            val1 = ' '.join(best_pair)
            val2 = ''.join(best_pair)
            words_new = [i.replace(val1,val2) for i in words_new]
                
        self.dict = {i:j for i,j in zip(final_pairs,range(len(final_pairs)))}
        self.inv_dict = {j:i for i,j in self.dict.items()}
        
    def _init_embeddings(self):
        """
        Initializes embeddings function from torch with len(self.dict) and self.d_model ##embeddings dimension
        """
        self.emb= torch.nn.Embedding(len(self.dict),self.d_model)
        
    def _convert_ids_to_embeddings(self,ids:List[int]):
        """
        Given a list of ids, it returns a list of embeddings.
        Args:
            ids : list of ids
        Returns:    
            list_of_embeddings : list of embeddings
        """
        assert isinstance(ids, list), "Input should be a list of ids"
        return self.emb(torch.tensor(ids))

