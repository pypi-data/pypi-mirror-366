import torch
import torch.nn as nn
import torch.nn.functional as F
import tokenizers
import numpy as np
import random
import pickle
import itertools
from pathlib import Path
import os
from typing import List, Literal

pre_tokenizers = Literal["Whitespace", "IndividualDigit", "Digits", "BertPreTokenizer", "ByteLevel", "Metaspace", "Punctuation", "UnicodeScripts", "WhitespaceSplit"]

class TokenizerConstructor:
    '''
    simple assembler for tokenizer using the tokenizers library
    tokenizer parameters can be set using strings and list[str]s
    strings used for tokenizer_type, pre_tokenizers, normalizers arguments are the names of those present in the
    tokenizers library. Additionally "IndividualDigits" can be used in normalizers for tokenizers.pre_tokenizers.Digits(individual_digits=True)

    vocab_size attribute returns the tokenizer instance's vocab_size (untrained tokenizer will have vocab_size=None)

    '''
    def __init__(self,
                 min_frequency:int=2,
                 tokenizer_type:Literal["BPE", "WordLevel", "WordPiece", "Unigram"] = "BPE",
                 pre_tokenizers: pre_tokenizers|List[pre_tokenizers]=["Whitespace"],
                 normalizers:list[str]|str=["Lowercase", "NFD", "StripAccents", "Strip"],
                 vocab:dict[str,int] = {},
                 special_tokens:list[str]|str=[],
                 unknown_token_string:str="<unk>",
                 start_token_string:str="<sos>",
                 end_token_string:str="<eos>",
                 pad_token_string:str="<pad>",
                 new_line_token_string:str="\n",
                 vocab_size:int=30000
                 ) -> None:
        self.vocab_size = None

        if isinstance(special_tokens, str):
            special_tokens = [special_tokens]
        self.special_tokens = special_tokens + [token for token in [unknown_token_string, start_token_string, end_token_string, pad_token_string, new_line_token_string] if token not in special_tokens and token is not None]
        self.unknown_token = self.special_tokens.index(unknown_token_string) if unknown_token_string is not None else None
        self.start_token = self.special_tokens.index(start_token_string) if start_token_string is not None else None
        self.end_token = self.special_tokens.index(end_token_string) if end_token_string is not None else None
        self.pad_token = self.special_tokens.index(pad_token_string) if pad_token_string is not None else None
        self.new_line_token = self.special_tokens.index(new_line_token_string) if new_line_token_string is not None else None

        self.start_token_string = start_token_string
        self.end_token_string = end_token_string
        self.pad_token_string = pad_token_string
        self.new_line_token_string = new_line_token_string

        if tokenizer_type == "BPE":
            self.tokenizer_type = tokenizers.Tokenizer(tokenizers.models.BPE(unk_token=unknown_token_string))
            self.trainer = tokenizers.trainers.BpeTrainer(special_tokens=self.special_tokens, min_frequency=min_frequency, vocab_size=vocab_size)
        elif tokenizer_type == "WordLevel":
            self.tokenizer_type = tokenizers.Tokenizer(tokenizers.models.WordLevel(vocab = vocab, unk_token=unknown_token_string))
            self.trainer = tokenizers.trainers.WordLevelTrainer(special_tokens=self.special_tokens, min_frequency=min_frequency, vocab_size=vocab_size)
        elif tokenizer_type == "WordPiece":
            self.tokenizer_type = tokenizers.Tokenizer(tokenizers.models.WordPiece(vocab = vocab, unk_token=unknown_token_string))
            self.trainer = tokenizers.trainers.WordPieceTrainer(special_tokens=self.special_tokens, min_frequency=min_frequency, vocab_size=vocab_size)
        elif tokenizer_type == "Unigram":
            self.tokenizer_type = tokenizers.Tokenizer(tokenizers.models.Unigram())
            self.trainer = tokenizers.trainers.UnigramTrainer(special_tokens=self.special_tokens, min_frequency=min_frequency, vocab_size=vocab_size)
        
        if self.pad_token is not None:
            self.tokenizer_type.enable_padding(pad_id=self.pad_token, pad_token=pad_token_string)

        if isinstance(pre_tokenizers, str):
            pre_tokenizers = [pre_tokenizers]
        sequence = []
        for pre_tok in pre_tokenizers:
            if pre_tok == "Whitespace":
                 sequence.append(tokenizers.pre_tokenizers.Whitespace())
            elif pre_tok == "IndividualDigits":
                sequence.append(tokenizers.pre_tokenizers.Digits(individual_digits=True))
            elif pre_tok == "Digits":
                sequence.append(tokenizers.pre_tokenizers.Digits(individual_digits=False))
            elif pre_tok == "BertPreTokenizer":
                sequence.append(tokenizers.pre_tokenizers.BertPreTokenizer())
            elif pre_tok == "ByteLevel":
                sequence.append(tokenizers.pre_tokenizers.ByteLevel())
            elif pre_tok == "Metaspace":
                sequence.append(tokenizers.pre_tokenizers.Metaspace())
            elif pre_tok == "Punctuation":
                sequence.append(tokenizers.pre_tokenizers.Punctuation())
            elif pre_tok == "UnicodeScripts":
                sequence.append(tokenizers.pre_tokenizers.UnicodeScripts())
            elif pre_tok == "WhitespaceSplit":
                sequence.append(tokenizers.pre_tokenizers.WhitespaceSplit())
        self.tokenizer_type.pre_tokenizer = tokenizers.pre_tokenizers.Sequence(sequence)
        
        if isinstance(normalizers, str):
            normalizers = [normalizers]
        sequence = []
        for norm in normalizers:
            if norm == "Lowercase":
                sequence.append(tokenizers.normalizers.Lowercase())
            elif norm == "NFC":
                sequence.append(tokenizers.normalizers.NFC())
            elif norm == "NFD":
                sequence.append(tokenizers.normalizers.NFD())
            elif norm == "NFKC":
                sequence.append(tokenizers.normalizers.NFKC())
            elif norm == "NFKD":
                sequence.append(tokenizers.normalizers.NFKD())
            elif norm == "Nmt":
                sequence.append(tokenizers.normalizers.Nmt())
            elif norm == "BertNormalizer":
                sequence.append(tokenizers.normalizers.BertNormalizer())
            elif norm == "StripAccents":
                sequence.append(tokenizers.normalizers.StripAccents())
            elif norm == "Strip":
                sequence.append(tokenizers.normalizers.Strip())
            elif norm == "BertNormalizer":
                sequence.append(tokenizers.normalizers.BertNormalizer())
        self.tokenizer_type.normalizer = tokenizers.normalizers.Sequence(sequence)
        

    def train(self, training_paths:list[str]|str) -> None:
        '''
        points to text files to be used for training the tokenizer instance
        '''
        if isinstance(training_paths, str):
            training_paths = [training_paths]
        self.tokenizer_type.train(training_paths, trainer=self.trainer)
        self.vocab_size = self.tokenizer_type.get_vocab_size()

    def encode(self, inp:str) -> list[int]:
        '''
        encodes string using trained tokenizer instance
        '''
        return self.tokenizer_type.encode(inp).ids
    
    def encode_batch(self, inp:list[str], max_length:int=None) -> list[list[int]]:
        '''
        encodes strings in parallel and truncates entries with length > max_length
        '''
        if max_length is not None:
            self.tokenizer_type.enable_truncation(max_length=max_length)
            if self.pad_token is not None:
                self.tokenizer_type.enable_padding(pad_id=self.pad_token, pad_token=self.pad_token_string, length=max_length)
        out = [row.ids for row in self.tokenizer_type.encode_batch(inp)]
        self.tokenizer_type.no_truncation()
        if self.pad_token is not None:
            self.tokenizer_type.enable_padding(pad_id=self.pad_token, pad_token=self.pad_token_string)
        return out
    
    def decode(self, inp:list[int]) -> str:
        '''
        decodes list of tokenz using trained tokenizer instance
        '''
        return self.tokenizer_type.decode(inp)
    

    
def create_mask(row:list, block_size:int) -> list[bool]:
    '''
    creates a mask list of length block_size for row, asuming mask does cover the entire row input
    '''
    mask = [1]*len(row) + [0]*(block_size - len(row))
    return mask

def pre_process_data(data:str, start_token_string:str, end_token_string:str) -> list[int]:
    '''
    returns data with the tokenizer's start and end tokens added to each row if they exist
    '''
    if start_token_string is None and end_token_string is None:
        return data
    else:
        for i in range(len(data)):
            if start_token_string is not None:
                data[i] = start_token_string + data[i]
            if end_token_string is not None:
                data[i] = data[i] + end_token_string
            
    return data

def safe_stack(tensor_list:list[torch.tensor]) -> torch.tensor:
    '''
    torch stack with check to ensure tensors are valid in input list
    returns torch.stack(out_list) for all valid torch tensors in tensor_list. raises error if no valid tensors
    '''
    out_list = [row for row in tensor_list if isinstance(row, torch.Tensor)]
    if len(out_list) == 0:
        raise ValueError("no valid tensors in list.")
    return torch.stack(out_list)


class DataProcessor:
    '''
    data processor can be instantiated by specifying the tokenizer(s) for decoder and encoder data
    '''
    def __init__(self,
                 dec_tokenizer:TokenizerConstructor,
                 enc_tokenizer:TokenizerConstructor=None
                 ) -> None:
        self.dec_tokenizer = dec_tokenizer
        self.enc_tokenizer = enc_tokenizer

    def process_list(self,
                     dec_data:list[str]|str,
                     dec_max_block_size:int=None,
                     dec_create_masks:bool=True,
                     enc_data:list[str]=None,
                     enc_max_block_size:int=None,
                     enc_create_masks:bool=True,
                     save_path:str = "."
                     ) -> None:
        '''
        processes raw data in the form of list[str] or str for decoder and encoder simultaneously and
        saves them to save_path as .pt files.
            - encoder and decoder input data should have matching input and outputs so enc_data[n] should have its corresponding
            decoder data at dec_data[n].
            - max block size can be specified for both input and output, default takes the max
            block size provided in the data respectively. If data length > max_length, the data is trimmed.
        '''

        if isinstance(dec_data, str):
            dec_data = [dec_data]
        dec_data_length = len(dec_data)
        dec_data = pre_process_data(dec_data, self.dec_tokenizer.start_token_string, self.dec_tokenizer.end_token_string)

        if enc_data is not None:
            if self.enc_tokenizer is None:
                self.enc_tokenizer = self.dec_tokenizer

            enc_data_length = len(enc_data)
            if dec_data_length != enc_data_length:
                raise Exception(f"decoder data and encoder data lengths do not match. decoder_data_length is {dec_data_length}, encoder_data_length is {enc_data_length}")
            enc_data = pre_process_data(enc_data, self.enc_tokenizer.start_token_string, self.enc_tokenizer.end_token_string)

        print("processing data")
        dec_out_list = self.dec_tokenizer.encode_batch(dec_data, max_length=dec_max_block_size)
        if dec_create_masks:
            mask_tokenizer = TokenizerConstructor(min_frequency=1, tokenizer_type="WordLevel", vocab={str(self.dec_tokenizer.pad_token): 0, "<unk>": 1}, special_tokens=["<pad>", "<unk>"], unknown_token_string="<unk>", start_token_string=None, end_token_string=None, pad_token_string=None)
            dec_mask_list = mask_tokenizer.encode_batch([str(i).replace("[", "").replace("]", "").replace(",", "") for i in dec_out_list])

        if enc_data is not None:
            enc_out_list = self.enc_tokenizer.encode_batch(enc_data, max_length=enc_max_block_size)
            if enc_create_masks:
                mask_tokenizer = TokenizerConstructor(min_frequency=1, tokenizer_type="WordLevel", vocab={str(self.enc_tokenizer.pad_token): 0, "<unk>": 1}, special_tokens=["<pad>", "<unk>"], unknown_token_string="<unk>", start_token_string=None, end_token_string=None, pad_token_string=None)
                enc_mask_list = mask_tokenizer.encode_batch([str(i).replace("[", "").replace("]", "").replace(",", "") for i in enc_out_list])

        dec_out_list = torch.tensor(dec_out_list, dtype=torch.long)
        Path(save_path).mkdir(parents=True, exist_ok=True)
        torch.save(dec_out_list, os.path.join(save_path, "decoder_data.pt"))
        if dec_create_masks:
            dec_mask_list = torch.tensor(dec_mask_list, dtype=torch.long)
            torch.save(dec_mask_list, os.path.join(save_path, "decoder_mask_data.pt"))
        if enc_data is not None:
            enc_out_list = torch.tensor(enc_out_list, dtype=torch.long)
            torch.save(enc_out_list, os.path.join(save_path, "encoder_data.pt"))
            if enc_create_masks:
                enc_mask_list = torch.tensor(enc_mask_list, dtype=torch.long)
                torch.save(enc_mask_list, os.path.join(save_path, "encoder_mask_data.pt"))


def get_valid_samples(random_samples:torch.Tensor,
                      masks:torch.Tensor,
                      block_size:int
                      ) -> list[int]:
    '''
    returns list of len(random_samples) with values corresponding to index values of masks that ensure minimum masked
    values when taking sample of length block_size
    '''
    valid_samples = [0 if sum(masks[row_num]) <= block_size else random.randint(0, sum(masks[row_num]) - block_size) for row_num in random_samples]
    return valid_samples
                
def get_batch(data:torch.Tensor,
                random_samples:torch.Tensor,
                masks:torch.Tensor=None,
                block_size:int=None,
                get_offset:bool=True
                ) -> tuple[torch.tensor]:
    '''
    returns random batches from data tensor using random sample for data selection.
        - returns corresponding batch offset by 1 unless get_offset=False
        - returns corresponding masks batch if masks data is specified
    '''
    batch_size = len(random_samples)
    if block_size is not None and block_size != data.shape[1]:
        if block_size >= data.shape[1]:
            raise Exception(f"specified block size ({block_size}) is larger than input tensor length ({data.shape[1]})")

        if masks is not None:
            random_point = get_valid_samples(random_samples, masks, block_size)
        else:
            random_point = torch.randint(data.shape[1] - block_size, (batch_size,))
        batch_in = safe_stack([data[random_samples[i]][random_point[i]:random_point[i]+block_size-int(get_offset)] for i in range(batch_size)])
        masks_in = safe_stack([masks[random_samples[i]][random_point[i]:random_point[i]+block_size-int(get_offset)] for i in range(batch_size)]) if masks is not None else None
        batch_out = safe_stack([data[random_samples[i]][1+random_point[i]:random_point[i]+block_size] for i in range(batch_size)]) if get_offset else None
    else:
        block_size = data.shape[1]
        batch_in = safe_stack([data[row_num][:block_size-int(get_offset)] for row_num in random_samples])
        masks_in = safe_stack([masks[row_num][:block_size-int(get_offset)] for row_num in random_samples]) if masks is not None else None
        batch_out = safe_stack([data[row_num][1:block_size] for row_num in random_samples]) if get_offset else None

    return batch_in, batch_out, masks_in

def top_kp_filter(logits: torch.Tensor,
                  top_k: int = None,
                  top_p: float = None
                  ) -> torch.Tensor:
    '''
    Returns predicted token by filtering output logits using top_k and/or top_p (nucleus) filtering.
    
    Args:
        logits: (batch_size, vocab_size) tensor of raw logits.
        top_k: keep only top_k tokens with highest logits.
        top_p: keep the smallest set of tokens with cumulative probability >= top_p.
    '''
    logits = logits.clone()  # avoid modifying input logits in-place

    # Apply top-p filtering if specified
    if top_p is not None:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
        probs = F.softmax(sorted_logits, dim=-1)
        cumulative_probs = torch.cumsum(probs, dim=-1)

        # Remove tokens with cumulative probability above threshold (except first token)
        sorted_mask = cumulative_probs > top_p
        sorted_mask[..., 1:] = sorted_mask[..., :-1].clone()
        sorted_mask[..., 0] = False

        # Mask tokens to remove by setting logits to -inf
        indices_to_remove = sorted_mask.scatter(1, sorted_indices, sorted_mask)
        logits[indices_to_remove] = float('-inf')

    # Apply top-k filtering if specified
    if top_k is not None:
        top_k = min(top_k, logits.size(-1))  # safety check
        topk_logits, topk_indices = torch.topk(logits, top_k, dim=-1)
        topk_probs = F.softmax(topk_logits, dim=-1).cpu().numpy()

        # For each batch, sample from top_k candidates
        selected = []
        for i in range(topk_probs.shape[0]):
            candidate = np.random.choice(topk_indices[i].cpu().numpy(), 1, p=topk_probs[i])
            selected.append(candidate[0])
        selected = torch.tensor(selected, dtype=torch.long)

    else:
        # If only top_p is specified, sample from entire filtered logits
        probs = F.softmax(logits, dim=-1).cpu().numpy()
        selected = []
        for i in range(probs.shape[0]):
            candidate = np.random.choice(len(probs[i]), 1, p=probs[i])
            selected.append(candidate[0])
        selected = torch.tensor(selected, dtype=torch.long)

    return selected



class SelfAttention(nn.Module):
    '''
    single self attention block of size head_size.
    triangle_mask=True to apply look-ahead mask of size block_size.
    '''
    def __init__(self,
                 head_size:int,
                 n_embed:int,
                 dropout:float,
                 block_size:int=0,
                 triangle_mask:bool=True
                 ) -> None:
        super().__init__()
        self.key = nn.Linear(n_embed, head_size, bias=False)
        self.query = nn.Linear(n_embed, head_size, bias=False)
        self.value = nn.Linear(n_embed, head_size, bias=False)
        self.triangle_mask = triangle_mask
        self.block_size = block_size

        if self.triangle_mask and self.block_size >= 0:
            self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

        self.dropout = nn.Dropout(dropout)

    def forward(self,
                k:torch.Tensor,
                q:torch.Tensor,
                v:torch.Tensor,
                mask:torch.Tensor=None
                ) -> torch.tensor:
        '''
        k, q and v are key, tensors to get key, query and value tensors.
        custom mask tensor can be applied.
        '''
        _,T,_ = k.shape

        k = self.key(k)
        q = self.query(q)
        v = self.value(v)

        wei = q @ k.transpose(-2,-1) * k.shape[-1]**-0.5
        if self.triangle_mask and self.block_size >= 0:
            wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
        if mask is not None:
            wei = wei.masked_fill(mask.unsqueeze(1)==0, float("-inf"))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)

        out = wei @ v
        return out

class MultiHeadAttention(nn.Module):
    '''
        multi-head attention block consisting of num_heads SelfAttention blocks and a linear layer to
        rejoin outputs.
        specified head_size, n_embed, dropout, block_size and triangle_mask values are passed through to
        SelfAttention blocks
    '''
    def __init__(self,
                 num_heads:int,
                 head_size:int,
                 n_embed:int,
                 dropout:float=0.1,
                 block_size:int=0,
                 triangle_mask:bool=True
                 ) -> None:
        super().__init__()
        self.heads = nn.ModuleList([SelfAttention(head_size, n_embed, dropout, block_size=block_size, triangle_mask=triangle_mask) for _ in range(num_heads)])
        self.proj = nn.Linear(head_size * num_heads, n_embed)
        self.dropout = nn.Dropout(dropout)

    def forward(self,
                k:torch.Tensor,
                q:torch.Tensor,
                v:torch.Tensor,
                mask:torch.Tensor=None
                ) -> torch.tensor:
        '''
        k, q and v are key, tensors to get key, query and value tensors.
        custom mask tensor can be applied.
        '''
        out = torch.cat([h(k, q, v, mask=mask) for h in self.heads], dim=-1)
        out = self.dropout(self.proj(out))
        return out
    
class FeedForward(nn.Module):
    '''
    feed forward layer used after multi-head attention consisting of 2 lieanr layers with
    a ReLU in between. Linear layers expand from n_embed to n_embed * expansion_factor and
    back to n_embed.
    '''
    def __init__(self,
                 n_embed:int,
                 expansion_factor:int,
                 dropout:float=0.1
                 ) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embed, expansion_factor * n_embed),
            nn.ReLU(),
            nn.Linear(expansion_factor * n_embed, n_embed),
            nn.Dropout(dropout),
        )

    def forward(self,
                x:torch.Tensor
                ) -> torch.tensor:
        return self.net(x)
    
class EncoderBlock(nn.Module):
    '''
    encoder block consists of a sequence of multi-head attention, LayerNorm, feed-forward, LayerNorm
    head_size is calculated from n_embed // n_head
    '''
    def __init__(self,
                 n_embed:int,
                 n_head:int,
                 expansion_factor:int,
                 dropout:float=0.1
                 ) -> None:
        super().__init__()
        head_size = n_embed // n_head
        self.sa = MultiHeadAttention(n_head, head_size, n_embed, dropout, triangle_mask=False)
        self.ffwd = FeedForward(n_embed, expansion_factor, dropout)
        self.ln1 = nn.LayerNorm(n_embed)
        self.ln2 = nn.LayerNorm(n_embed)

    def forward(self,
                x:torch.Tensor,
                mask:torch.Tensor=None
                ) -> tuple[torch.tensor]:
        att = self.sa(x, x, x, mask=mask)
        x = self.ln1(att + x)
        ff = self.ffwd(x)
        out = self.ln2(ff + x)
        return out, mask
    

class DecoderBlock(nn.Module):
    '''
    decoder block consists of a sequence of multi-head attention, LayerNorm, feed-forward, LayerNorm
    if cross-attention is True, a multi-head attention block and layerNorm is added before feed-forward
    taking specified enc_k and enc_v tensors as value and key tensors. These values should be the output
    of an encoder block.
    head_size is calculated from n_embed // n_head
    '''
    def __init__(self,
                 n_embed:int,
                 n_head:int,
                 expansion_factor:int,
                 cross_attention:bool=False,
                 block_size:int=0,
                 dropout:float=0.1
                 ) -> None:
        super().__init__()
        head_size = n_embed // n_head
        self.sa = MultiHeadAttention(n_head, head_size, n_embed, dropout, block_size=block_size, triangle_mask=True)
        self.ffwd = FeedForward(n_embed, expansion_factor, dropout)
        self.ln1 = nn.LayerNorm(n_embed)
        self.ln2 = nn.LayerNorm(n_embed)
        if cross_attention:
            self.ca = MultiHeadAttention(n_head, head_size, n_embed, dropout, triangle_mask=False)
            self.ln3 = nn.LayerNorm(n_embed)
        else:
            self.ca = None

    def forward(self,
                x:torch.Tensor,
                enc_k:torch.Tensor,
                enc_v:torch.Tensor,
                mask_out:bool=None,
                mask_in:torch.Tensor=None
                ) -> tuple[torch.tensor]:
        att = self.sa(x, x, x, mask=mask_out)
        x = self.ln1(att + x)
        if self.ca is not None:
            catt = self.ca(enc_k, x, enc_v, mask=mask_in)
            x = self.ln3(catt + x)
        ff = self.ffwd(x)
        out = self.ln2(ff + x)
        return out, enc_k, enc_v, mask_out, mask_in
    
class MySequential(nn.Sequential):
    '''
    MySequential serves the same purpose as nn.Sequential but allows for multiple inputs and outputs
    '''
    def forward(self, *input):
        for module in self._modules.values():
            input = module(*input)
        return input

class RoboConstructor(nn.Module):
    '''
    RoboConstructor assembles an encoder-decoder or decoder-only transformer.
    if the enc_* variables are not specified, or enc_n_blocks==0, the transformer will be decoder-only.
        - if any of the dec_* variables are not specified (except dec_expansion_factor) an error will occur.
        - if enc_n_blocks > 0 and any of the enc_* variables are not specified (except enc_expansion_factor and enc_block_size) an error will occur.
    dropout can be specified, default=0.1.
    if device is not specified, device will default to first available among ("cuda", "mps", "cpu")
    '''
    def __init__(self,
                 n_embed:int,
                 dec_n_blocks:int,
                 dec_n_head:int,
                 dec_vocab_size:int,
                 dec_block_size:int,
                 dec_expansion_factor:int=4,
                 enc_n_blocks:int=0,
                 enc_n_head:int=None,
                 enc_vocab_size:int=None,
                 enc_block_size:int=None,
                 enc_expansion_factor:int=4,
                 dropout:float=0.1,
                 device:str=None
                 ) -> None:
        super().__init__()
        self.n_embed = n_embed
        self.dec_n_blocks = dec_n_blocks
        self.dec_n_head = dec_n_head
        self.dec_vocab_size = dec_vocab_size
        self.dec_block_size = dec_block_size
        self.dec_expansion_factor = dec_expansion_factor
        self.dropout = dropout
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device
        self.dec_token_embedding_table = nn.Embedding(dec_vocab_size, n_embed)
        self.dec_positional_embedding_table = nn.Embedding(dec_block_size, n_embed)

        if enc_n_blocks != 0:
            self.enc_n_blocks = enc_n_blocks
            self.enc_n_head = enc_n_head
            self.enc_expansion_factor = enc_expansion_factor
            self.enc_vocab_size = enc_vocab_size
            self.enc_block_size = enc_block_size
            self.cross_attention = True
            self.enc_token_embedding_table = nn.Embedding(enc_vocab_size, n_embed)
            self.enc_positional_embedding_table = nn.Embedding(enc_block_size, n_embed)
            self.encoder_blocks = MySequential(*[EncoderBlock(n_embed, enc_n_head, enc_expansion_factor, dropout=dropout) for _ in range(enc_n_blocks)])
        else:
            self.cross_attention = False
            self.enc_n_blocks = None
            self.enc_n_head = None
            self.enc_expansion_factor = None
            self.enc_vocab_size = None
            self.enc_block_size = None
            self.enc_token_embedding_table = None
            self.enc_positional_embedding_table = None
            self.encoder_blocks = None

        self.decoder_blocks = MySequential(*[DecoderBlock(n_embed, dec_n_head, dec_expansion_factor, cross_attention=self.cross_attention, block_size=self.dec_block_size, dropout=dropout) for _ in range(dec_n_blocks)])
        self.ln = nn.LayerNorm(n_embed)
        self.lid = nn.Linear(n_embed, dec_vocab_size)

        self.apply(self._init_weights)

    def _init_weights(self, module) -> None:
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self,
                dec_in:torch.Tensor,
                dec_mask:torch.Tensor=None,
                enc_in:torch.Tensor=None,
                enc_mask:torch.Tensor=None
                ) -> torch.tensor:
        _, dec_T = dec_in.shape
        if enc_in is not None:
            _, enc_T = enc_in.shape

        dec_tok_emb = self.dec_token_embedding_table(dec_in)
        dec_pos_emb = self.dec_positional_embedding_table(torch.arange(dec_T, device=self.device))
        dec_x = dec_tok_emb + dec_pos_emb

        if self.cross_attention:
            enc_tok_emb = self.enc_token_embedding_table(enc_in)
            enc_pos_emb = self.enc_positional_embedding_table(torch.arange(enc_T, device=self.device))
            enc_x = enc_tok_emb + enc_pos_emb


            enc_out, enc_mask = self.encoder_blocks(enc_x, enc_mask)
        else:
            enc_out = None

        x, _, _, _, _ = self.decoder_blocks(dec_x, enc_out, enc_out, dec_mask, enc_mask)
        x = self.ln(x)
        proj_output = self.lid(x)

        return proj_output
    
    
    def prep_data(self,
                  batch_size:int,
                  dec_data:str,
                  dec_block_size:int,
                  dec_masks:str=None,
                  enc_data:str=None,
                  enc_block_size:int=None,
                  enc_masks:str=None
                  ) -> tuple[torch.tensor]:
        '''
        returns a batch of specified batch_size, from dec_data (and dec_masks, enc_data and enc_masks if specified)
            - if encoder is configured in this instance, enc_data must be specified.
            - dec_block_size must be specified.
            - if enc_block_size is not specified, the entire block_size of enc_data will be used.
            this method is for use in train_robo()
        '''
        random_samples = torch.randint(dec_data.shape[0], (batch_size,))

        dec_train_batch_in, dec_train_batch_out, dec_train_masks_in = get_batch(dec_data, random_samples, masks=dec_masks, block_size=dec_block_size, get_offset=True)
        dec_train_batch_in = dec_train_batch_in.to(self.device)
        dec_train_batch_out = dec_train_batch_out.to(self.device) if dec_train_batch_out is not None else None
        dec_train_masks_in = dec_train_masks_in.to(self.device) if dec_train_masks_in is not None else None

        if self.cross_attention:
            enc_train_batch_in, _, enc_train_masks_in = get_batch(enc_data, random_samples, masks=enc_masks, block_size=enc_block_size, get_offset=False)
            enc_train_batch_in = enc_train_batch_in.to(self.device)
            enc_train_masks_in = enc_train_masks_in.to(self.device) if enc_train_masks_in is not None else None
        else:
            enc_train_batch_in = None
            enc_train_masks_in = None

        return dec_train_batch_in, dec_train_batch_out, dec_train_masks_in, enc_train_batch_in, enc_train_masks_in

            
    def train_robo(self,
              max_iters:int,
              eval_interval:int,
              batch_size:int,
              training_dir_path:str,
              eval_dir_path:str=None,
              eval_iters:int=3,
              learning_rate:float=1e-4,
              pad_token:int=None,
              dec_tokenizer:TokenizerConstructor=None,
              save_path:str=None,
              label_smoothing:float=0.1,
              optimizer_state_dict_path:str=None
              ) -> None:
        '''
        trains the RoboConstructor instance transformer.
            - training parameters can be specified such as max_iters, eval_interval, batch_size, eval_iters, learning_rate, label_smoothing.
            - paths must be specified for decoder training data (and encoder training data if encoder-decoder transformer)
            - optional paths to specify: decoder and encoder masks, decoder and encoder validation data, decoder and encoder validation masks data
            - if neither pad_token or tokenizer is specified (or tokenizer has no pad_token), any padding in labels will contribute towards the loss
            which may cause unwanted results. Specifying pad_token and/or tokenizer allows loss to be calculated while ignoring any padding in labels
            - specify save_path to save the model as a .pkl file every eval_interval iterations using the save_component function.
        '''
        
        dec_training_path = os.path.join(training_dir_path, "decoder_data.pt")
        dec_training_data = torch.load(dec_training_path, weights_only=True)

        dec_eval_path = os.path.join(eval_dir_path, "decoder_data.pt")
        dec_eval_data = torch.load(dec_eval_path, weights_only=True) if os.path.isfile(dec_eval_path) else None

        dec_training_masks_path = os.path.join(training_dir_path, "decoder_mask_data.pt")
        dec_training_masks_data = torch.load(dec_training_masks_path, weights_only=True) if os.path.isfile(dec_training_masks_path) else None

        dec_eval_masks_path = os.path.join(eval_dir_path, "decoder_mask_data.pt")
        dec_eval_masks_data = torch.load(dec_eval_masks_path, weights_only=True) if os.path.isfile(dec_eval_masks_path) else None

        enc_training_path = os.path.join(training_dir_path, "encoder_data.pt")
        enc_training_data = torch.load(enc_training_path, weights_only=True) if os.path.isfile(enc_training_path) else None

        enc_eval_path = os.path.join(eval_dir_path, "encoder_data.pt")
        enc_eval_data = torch.load(enc_eval_path, weights_only=True) if os.path.isfile(enc_eval_path) else None

        enc_training_masks_path = os.path.join(training_dir_path, "encoder_mask_data.pt")
        enc_training_masks_data = torch.load(enc_training_masks_path, weights_only=True) if os.path.isfile(enc_training_masks_path) else None

        enc_eval_masks_path = os.path.join(eval_dir_path, "encoder_mask_data.pt")
        enc_eval_masks_data = torch.load(enc_eval_masks_path, weights_only=True) if os.path.isfile(enc_eval_masks_path) else None

        if pad_token is None and dec_tokenizer is not None:
            pad_token = dec_tokenizer.pad_token

        self.to(self.device)

        if pad_token is not None:
            loss_fn = nn.CrossEntropyLoss(ignore_index=pad_token, label_smoothing=label_smoothing).to(self.device)
        else:
            loss_fn = nn.CrossEntropyLoss(label_smoothing=label_smoothing).to(self.device)
        print(sum(p.numel() for p in self.parameters())/1e6, "M parameters")
        optimizer = torch.optim.AdamW(self.parameters(), lr=learning_rate)
        if optimizer_state_dict_path is not None:
            opt_path = os.path.join(optimizer_state_dict_path, "opt.pt")
            if os.path.isfile(opt_path):
                optimizer.load_state_dict(torch.load(opt_path))
                for param_group in optimizer.param_groups:
                    param_group["lr"] = learning_rate
                    
        @torch.no_grad()
        def estimate_loss() -> dict:
            out = {}
            self.eval()
            losses = torch.zeros(eval_iters)
            for k in range(eval_iters):
                dec_x, dec_y, dec_mask, enc_x, enc_mask = self.prep_data(batch_size, dec_training_data, dec_masks=dec_training_masks_data, dec_block_size=self.dec_block_size, enc_data=enc_training_data, enc_masks=enc_training_masks_data, enc_block_size=self.enc_block_size)
                proj_output = self(dec_x, dec_mask, enc_x, enc_mask)
                losses[k] = loss_fn(proj_output.view(-1, self.dec_vocab_size), dec_y.view(-1))
            out["train"] = losses.mean()
            if dec_eval_data is not None:
                for k in range(eval_iters):
                    dec_x, dec_y, dec_mask, enc_x, enc_mask = self.prep_data(batch_size, dec_eval_data, dec_masks=dec_eval_masks_data, dec_block_size=self.dec_block_size, enc_data=enc_eval_data, enc_masks=enc_eval_masks_data, enc_block_size=self.enc_block_size)
                    proj_output = self(dec_x, dec_mask, enc_x, enc_mask)
                    losses[k] = loss_fn(proj_output.view(-1, self.dec_vocab_size), dec_y.view(-1))
                out["eval"] = losses.mean()
            else:
                out["eval"] = np.nan
            self.train()
            return out
        
        self.train()
        for iter in range(max_iters):
            if iter % eval_interval == 0 or iter == max_iters-1:
                losses = estimate_loss()
                print(f"step {iter}: train loss {losses['train']:.4f}, eval loss {losses['eval']:.4f}")
                if save_path is not None:
                    save_component(self, save_path=save_path)
                if optimizer_state_dict_path is not None:
                    torch.save(optimizer.state_dict(), os.path.join(optimizer_state_dict_path, "opt.pt"))

            dec_x, dec_y, dec_mask, enc_x, enc_mask = self.prep_data(batch_size, dec_training_data, dec_masks=dec_training_masks_data, dec_block_size=self.dec_block_size, enc_data=enc_training_data, enc_masks=enc_training_masks_data, enc_block_size=self.enc_block_size)
            proj_output = self(dec_x, dec_mask, enc_x, enc_mask)
            loss = loss_fn(proj_output.view(-1, self.dec_vocab_size), dec_y.view(-1))
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        self.eval()

    def generate(self,
                inputs:list[int]|str,
                max_new_tokens:int=None,
                dec_tokenizer:TokenizerConstructor=None,
                enc_tokenizer:TokenizerConstructor=None,
                dec_start_token:int=None,
                enc_start_token:int=None,
                dec_end_token:int=None,
                enc_end_token:int=None,
                separator_token:int=None,
                new_line_token:int=None,
                temperature:float=1,
                top_k:int=None,
                top_p:float=None
                ) -> list[int]|str:
        '''
        uses the tranformer model from the RoboConstructor instance to generate an output from an input.
            - input can be in the form of a string if input tokenizer is specified (enc_tokenizer for encoder-decoder and dec_tokenizder for decoder-only),
            otherwise, it must be in the form of a list of tokens.
            - if dec_tokenizer is specified, output will be a string.
            - new tokens are generated until the dec_end_token (or dec_tokenizer.end_token) is generated, or the number of tokens generated == max_new_tokens.
            - if input tokenizer is not specified, or input tokenizer.start_token is None, enc_start_token must be specified for an encoder-decoder model.
            - separator_token is used to separate the input and generated tokens for a decoder-only model. If this value is not specified, there
            will be no distinction between input tokens and generated tokens to the transformer, even if dec_tokenizer is specified.
            - if new_line_token is not specified, output will be returned in one line, without any "\n" line separators.
            - temperature, top_k and top_p can be specified to adjust the output.
        '''
        max_new_tokens = self.dec_block_size if max_new_tokens is None else max_new_tokens

        if self.cross_attention:
            if enc_tokenizer is not None:
                if enc_start_token is None:
                    enc_start_token = enc_tokenizer.start_token
                if enc_end_token is None:
                    enc_end_token = enc_tokenizer.end_token
                if isinstance(inputs, str):
                    inputs = enc_tokenizer.encode(inputs)

        if dec_tokenizer is not None:
            if dec_start_token is None:
                dec_start_token = dec_tokenizer.start_token
            if dec_end_token is None:
                dec_end_token = dec_tokenizer.end_token
            if new_line_token is None:
                new_line_token = dec_tokenizer.new_line_token
        if not self.cross_attention and isinstance(inputs, str):
            inputs = dec_tokenizer.encode(inputs)


        if self.cross_attention:
            enc_input = torch.tensor([[enc_start_token] + inputs + [enc_end_token]], dtype=torch.long, device=self.device)
            idx = torch.tensor([[dec_start_token]], dtype=torch.long, device=self.device)
        else:
            enc_input = None
            if separator_token is not None:
                idx = torch.tensor([[dec_start_token] + inputs + [separator_token]], dtype=torch.long, device=self.device)
            else:
                idx = torch.tensor([[dec_start_token] + inputs], dtype=torch.long, device=self.device)

        self.eval()
        for _ in range(1, max_new_tokens):
            idx_cond = idx[:, -self.dec_block_size:] if idx.shape[1] > self.dec_block_size else idx
            
            proj_output = self(idx_cond, enc_in=enc_input)

            logits = proj_output[:, -1, :]
            probabilities = F.log_softmax(logits/temperature, dim=-1)

            if top_k is None and top_p is None:
                idx_next = torch.max(probabilities, dim=-1).indices.unsqueeze(0)
            else:
                idx_next = top_kp_filter(probabilities, top_k=top_k, top_p=top_p).unsqueeze(0).to(self.device)
            idx = torch.cat((idx, idx_next), dim=-1)
            if idx_next[0] == dec_end_token:
                break
        
        if dec_tokenizer is None:
            return idx[0].tolist()
        else:
            if new_line_token is not None:
                return "\n".join([dec_tokenizer.decode(list(y)) for x, y in itertools.groupby(idx[0].tolist(), lambda z: z == 0) if not x])
            else:
                return dec_tokenizer.decode(idx[0].tolist())
    

def save_component(component, save_path:str) -> None:
    '''
    saves component (such as TokenizerConstructor or RoboConstructor) as .pkl file.
    '''
    save_path = save_path + ".pkl" if save_path[-4:] != ".pkl" else save_path
    with open(save_path, "wb") as comp:
        pickle.dump(component, comp, pickle.HIGHEST_PROTOCOL)

def load_component(load_path:str):
    '''
    loads saved .pkl file into variable.
    '''
    load_path = load_path + ".pkl" if load_path[-4:] != ".pkl" else load_path
    with open(load_path, "rb") as comp:
        loaded_component = pickle.load(comp)
    return loaded_component
