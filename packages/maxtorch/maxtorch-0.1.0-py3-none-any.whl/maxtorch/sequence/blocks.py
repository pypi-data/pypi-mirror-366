import torch
import torch.nn as nn


class TransformerEncoderBlock(nn.Module):
    """
    Transformer Encoder Block

    Reference: Attention Is All You Need, Ashish Vaswani et al., NeurIPS 2017, arXiv:1706.03762
    https://arxiv.org/abs/1706.03762

    Summary: Composed of multi-head self-attention and feedforward network, widely used for sequence modeling in NLP, CV, etc.

    Args:
        embed_dim (int): Embedding dimension.
        num_heads (int): Number of attention heads.
        ff_dim (int): Feedforward network dimension.
        dropout (float, optional): Dropout rate. Default: 0.1.

    Input:
        x (Tensor): Shape (B, N, embed_dim)
        attn_mask (Tensor, optional): Attention mask. Default: None.
    Output:
        out (Tensor): Shape (B, N, embed_dim)
    """

    def __init__(self, embed_dim, num_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(
            embed_dim, num_heads, dropout=dropout, batch_first=True
        )
        self.norm1 = nn.LayerNorm(embed_dim)
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.ReLU(inplace=True),
            nn.Linear(ff_dim, embed_dim),
        )
        self.norm2 = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, attn_mask=None):
        # x: (B, N, C)
        attn_output, _ = self.self_attn(x, x, x, attn_mask=attn_mask)
        x = self.norm1(x + self.dropout(attn_output))
        ff_output = self.ff(x)
        x = self.norm2(x + self.dropout(ff_output))
        return x


class TransformerDecoderBlock(nn.Module):
    """
    Transformer Decoder Block

    Reference: Attention Is All You Need, Ashish Vaswani et al., NeurIPS 2017, arXiv:1706.03762
    https://arxiv.org/abs/1706.03762

    Summary: Contains self-attention, encoder-decoder attention, and feedforward network. Widely used for sequence-to-sequence modeling (e.g., translation, generation).

    Args:
        embed_dim (int): Embedding dimension.
        num_heads (int): Number of attention heads.
        ff_dim (int): Feedforward network dimension.
        dropout (float, optional): Dropout rate. Default: 0.1.

    Input:
        x (Tensor): Shape (B, N, embed_dim)
        memory (Tensor): Shape (B, M, embed_dim)
        tgt_mask (Tensor, optional): Target attention mask. Default: None.
        memory_mask (Tensor, optional): Memory attention mask. Default: None.
    Output:
        out (Tensor): Shape (B, N, embed_dim)
    """

    def __init__(self, embed_dim, num_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(
            embed_dim, num_heads, dropout=dropout, batch_first=True
        )
        self.norm1 = nn.LayerNorm(embed_dim)
        self.cross_attn = nn.MultiheadAttention(
            embed_dim, num_heads, dropout=dropout, batch_first=True
        )
        self.norm2 = nn.LayerNorm(embed_dim)
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.ReLU(inplace=True),
            nn.Linear(ff_dim, embed_dim),
        )
        self.norm3 = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, memory, tgt_mask=None, memory_mask=None):
        # x: (B, N, C), memory: (B, M, C)
        attn_output, _ = self.self_attn(x, x, x, attn_mask=tgt_mask)
        x = self.norm1(x + self.dropout(attn_output))
        cross_output, _ = self.cross_attn(x, memory, memory, attn_mask=memory_mask)
        x = self.norm2(x + self.dropout(cross_output))
        ff_output = self.ff(x)
        x = self.norm3(x + self.dropout(ff_output))
        return x


class LSTMBlock(nn.Module):
    """
    LSTM Block (Long Short-Term Memory)

    Reference: Long Short-Term Memory, Sepp Hochreiter, Jürgen Schmidhuber, Neural Computation 1997
    https://www.bioinf.jku.at/publications/older/2604.pdf

    Summary: Recurrent neural network unit that effectively captures long-range dependencies. Widely used for sequence modeling and NLP.

    Args:
        input_size (int): Number of input features.
        hidden_size (int): Number of hidden units.
        num_layers (int, optional): Number of stacked LSTM layers. Default: 1.
        batch_first (bool, optional): If True, input/output tensors are (B, T, C). Default: True.
        bidirectional (bool, optional): If True, becomes a bidirectional LSTM. Default: False.
        dropout (float, optional): Dropout rate between layers. Default: 0.0.

    Input:
        x (Tensor): Shape (B, T, C) if batch_first else (T, B, C)
        hx (tuple, optional): Initial hidden and cell states. Default: None.
    Output:
        out (Tensor): Output features (B, T, hidden_size * num_directions)
        (h_n, c_n) (tuple): Final hidden and cell states
    """

    def __init__(
        self,
        input_size,
        hidden_size,
        num_layers=1,
        batch_first=True,
        bidirectional=False,
        dropout=0.0,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=batch_first,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0.0,
        )

    def forward(self, x, hx=None):
        # x: (B, T, C) if batch_first else (T, B, C)
        out, (h_n, c_n) = self.lstm(x, hx) if hx is not None else self.lstm(x)
        return out, (h_n, c_n)


class GRUBlock(nn.Module):
    """
    GRU Block (Gated Recurrent Unit)

    Reference: Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation, Kyunghyun Cho et al., EMNLP 2014, arXiv:1406.1078
    https://arxiv.org/abs/1406.1078

    Summary: Simpler, parameter-efficient recurrent unit compared to LSTM. Widely used for sequence modeling and NLP.

    Args:
        input_size (int): Number of input features.
        hidden_size (int): Number of hidden units.
        num_layers (int, optional): Number of stacked GRU layers. Default: 1.
        batch_first (bool, optional): If True, input/output tensors are (B, T, C). Default: True.
        bidirectional (bool, optional): If True, becomes a bidirectional GRU. Default: False.
        dropout (float, optional): Dropout rate between layers. Default: 0.0.

    Input:
        x (Tensor): Shape (B, T, C) if batch_first else (T, B, C)
        hx (Tensor, optional): Initial hidden state. Default: None.
    Output:
        out (Tensor): Output features (B, T, hidden_size * num_directions)
        h_n (Tensor): Final hidden state
    """

    def __init__(
        self,
        input_size,
        hidden_size,
        num_layers=1,
        batch_first=True,
        bidirectional=False,
        dropout=0.0,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=batch_first,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0.0,
        )

    def forward(self, x, hx=None):
        # x: (B, T, C) if batch_first else (T, B, C)
        out, h_n = self.gru(x, hx) if hx is not None else self.gru(x)
        return out, h_n
