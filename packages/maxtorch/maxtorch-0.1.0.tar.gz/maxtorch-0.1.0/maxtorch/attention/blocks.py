import torch
import torch.nn as nn


class SqueezeExcitationBlock(nn.Module):
    """
    Squeeze-and-Excitation Block (SE Block)

    Reference: Squeeze-and-Excitation Networks, Jie Hu et al., CVPR 2018, arXiv:1709.01507
    https://arxiv.org/abs/1709.01507

    Summary: Explicitly models channel-wise dependencies and adaptively recalibrates channel responses to enhance representational power.

    Args:
        channels (int): Number of input/output channels.
        reduction (int, optional): Reduction ratio for the bottleneck. Default: 16.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid(),
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y


class CBAMBlock(nn.Module):
    """
    Convolutional Block Attention Module (CBAM)

    Reference: CBAM: Convolutional Block Attention Module, Sanghyun Woo et al., ECCV 2018, arXiv:1807.06521
    https://arxiv.org/abs/1807.06521

    Summary: Lightweight attention module combining channel and spatial attention, can be seamlessly integrated into existing CNNs to enhance feature representation.

    Args:
        channels (int): Number of input/output channels.
        reduction (int, optional): Reduction ratio for channel attention. Default: 16.
        kernel_size (int, optional): Kernel size for spatial attention. Default: 7.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, channels, reduction=16, kernel_size=7):
        super().__init__()
        # 通道注意力
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.mlp = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
        )
        self.sigmoid_channel = nn.Sigmoid()
        # 空间注意力
        self.conv_spatial = nn.Conv2d(
            2, 1, kernel_size=kernel_size, padding=kernel_size // 2, bias=False
        )
        self.sigmoid_spatial = nn.Sigmoid()

    def forward(self, x):
        # 通道注意力
        b, c, h, w = x.size()
        avg = self.avg_pool(x).view(b, c)
        max_ = self.max_pool(x).view(b, c)
        channel_att = self.mlp(avg) + self.mlp(max_)
        channel_att = self.sigmoid_channel(channel_att).view(b, c, 1, 1)
        x = x * channel_att
        # 空间注意力
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        spatial_att = torch.cat([avg_out, max_out], dim=1)
        spatial_att = self.conv_spatial(spatial_att)
        spatial_att = self.sigmoid_spatial(spatial_att)
        out = x * spatial_att
        return out


class SelfAttention2d(nn.Module):
    """
    Self-Attention 2D (SAGAN/Transformer)

    Reference: Self-Attention Generative Adversarial Networks, Han Zhang et al., ICML 2019, arXiv:1805.08318
    https://arxiv.org/abs/1805.08318

    Summary: Models long-range dependencies in spatial domain via self-attention, improving global modeling for generation and recognition.

    Args:
        in_channels (int): Number of input/output channels.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, in_channels):
        super().__init__()
        self.query_conv = nn.Conv2d(in_channels, in_channels // 8, kernel_size=1)
        self.key_conv = nn.Conv2d(in_channels, in_channels // 8, kernel_size=1)
        self.value_conv = nn.Conv2d(in_channels, in_channels, kernel_size=1)
        self.gamma = nn.Parameter(torch.zeros(1))
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        batch, C, H, W = x.size()
        proj_query = (
            self.query_conv(x).view(batch, -1, H * W).permute(0, 2, 1)
        )  # (B, N, C//8)
        proj_key = self.key_conv(x).view(batch, -1, H * W)  # (B, C//8, N)
        energy = torch.bmm(proj_query, proj_key)  # (B, N, N)
        attention = self.softmax(energy)
        proj_value = self.value_conv(x).view(batch, -1, H * W)  # (B, C, N)
        out = torch.bmm(proj_value, attention.permute(0, 2, 1))  # (B, C, N)
        out = out.view(batch, C, H, W)
        out = self.gamma * out + x
        return out


class NonLocalBlock(nn.Module):
    """
    Non-local Block (Non-local Neural Networks)

    Reference: Non-local Neural Networks, Xiaolong Wang et al., CVPR 2018, arXiv:1711.07971
    https://arxiv.org/abs/1711.07971

    Summary: Captures long-range dependencies by modeling global feature relations, widely used in video understanding and image recognition.

    Args:
        in_channels (int): Number of input/output channels.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, in_channels):
        super().__init__()
        self.in_channels = in_channels
        self.inter_channels = in_channels // 2 if in_channels > 1 else 1
        self.g = nn.Conv2d(in_channels, self.inter_channels, 1)
        self.theta = nn.Conv2d(in_channels, self.inter_channels, 1)
        self.phi = nn.Conv2d(in_channels, self.inter_channels, 1)
        self.W = nn.Conv2d(self.inter_channels, in_channels, 1)
        nn.init.constant_(self.W.weight, 0)
        nn.init.constant_(self.W.bias, 0)
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        batch, C, H, W = x.size()
        g_x = self.g(x).view(batch, self.inter_channels, -1)  # (B, C', N)
        g_x = g_x.permute(0, 2, 1)  # (B, N, C')
        theta_x = self.theta(x).view(batch, self.inter_channels, -1)  # (B, C', N)
        theta_x = theta_x.permute(0, 2, 1)  # (B, N, C')
        phi_x = self.phi(x).view(batch, self.inter_channels, -1)  # (B, C', N)
        f = torch.bmm(theta_x, phi_x)  # (B, N, N)
        f_div_C = self.softmax(f)
        y = torch.bmm(f_div_C, g_x)  # (B, N, C')
        y = y.permute(0, 2, 1).contiguous().view(batch, self.inter_channels, H, W)
        W_y = self.W(y)
        z = W_y + x
        return z


class ECABlock(nn.Module):
    """
    Efficient Channel Attention Block (ECA)

    Reference: ECA-Net: Efficient Channel Attention for Deep Convolutional Neural Networks, Qilong Wang et al., CVPR 2020, arXiv:1910.03151
    https://arxiv.org/abs/1910.03151

    Summary: Lightweight channel attention module using local cross-channel interaction via 1D convolution, no dimensionality reduction.

    Args:
        channels (int): Number of input/output channels.
        k_size (int, optional): Kernel size for 1D convolution. Default: 3.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, channels, k_size=3):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(
            1, 1, kernel_size=k_size, padding=(k_size - 1) // 2, bias=False
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, 1, c)  # (B, 1, C)
        y = self.conv(y)
        y = self.sigmoid(y).view(b, c, 1, 1)
        return x * y


class GCBlock(nn.Module):
    """
    Global Context Block (GC Block)

    Reference: GCNet: Non-local Networks Meet Squeeze-Excitation Networks and Beyond, Yue Cao et al., ICCV 2019, arXiv:1904.11492
    https://arxiv.org/abs/1904.11492

    Summary: Captures global context via context modeling and feature fusion, combining non-local and SE mechanisms efficiently.

    Args:
        in_channels (int): Number of input/output channels.
        ratio (int, optional): Bottleneck ratio for transform. Default: 16.
        pooling_type (str, optional): 'att' for attention pooling, 'avg' for average pooling. Default: 'att'.
        fusion_types (tuple of str, optional): Types of feature fusion, e.g., ('channel_add', 'channel_mul'). Default: ('channel_add',).

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(
        self, in_channels, ratio=16, pooling_type="att", fusion_types=("channel_add",)
    ):
        super().__init__()
        assert pooling_type in ["att", "avg"]
        assert all([f in ["channel_add", "channel_mul"] for f in fusion_types])
        self.in_channels = in_channels
        self.ratio = ratio
        self.pooling_type = pooling_type
        self.fusion_types = fusion_types
        if pooling_type == "att":
            self.conv_mask = nn.Conv2d(in_channels, 1, kernel_size=1)
            self.softmax = nn.Softmax(dim=2)
        else:
            self.avg_pool = nn.AdaptiveAvgPool2d(1)
        hidden_channels = max(1, in_channels // ratio)
        self.channel_add_conv = (
            nn.Sequential(
                nn.Conv2d(in_channels, hidden_channels, kernel_size=1),
                nn.LayerNorm([hidden_channels, 1, 1]),
                nn.ReLU(inplace=True),
                nn.Conv2d(hidden_channels, in_channels, kernel_size=1),
            )
            if "channel_add" in fusion_types
            else None
        )
        self.channel_mul_conv = (
            nn.Sequential(
                nn.Conv2d(in_channels, hidden_channels, kernel_size=1),
                nn.LayerNorm([hidden_channels, 1, 1]),
                nn.ReLU(inplace=True),
                nn.Conv2d(hidden_channels, in_channels, kernel_size=1),
            )
            if "channel_mul" in fusion_types
            else None
        )

    def spatial_pool(self, x):
        b, c, h, w = x.size()
        if self.pooling_type == "att":
            input_x = x.view(b, c, h * w)
            context_mask = self.conv_mask(x)
            context_mask = context_mask.view(b, 1, h * w)
            context_mask = self.softmax(context_mask)
            context_mask = context_mask.expand(b, c, h * w)
            context = torch.sum(input_x * context_mask, 2, keepdim=True)
            context = context.view(b, c, 1, 1)
        else:
            context = self.avg_pool(x)
        return context

    def forward(self, x):
        context = self.spatial_pool(x)
        out = x
        if self.channel_mul_conv is not None:
            channel_mul_term = torch.sigmoid(self.channel_mul_conv(context))
            out = out * channel_mul_term
        if self.channel_add_conv is not None:
            channel_add_term = self.channel_add_conv(context)
            out = out + channel_add_term
        return out


class CoordinateAttention(nn.Module):
    """
    Coordinate Attention Block

    Reference: Coordinate Attention for Efficient Mobile Network Design, Qibin Hou et al., CVPR 2021, arXiv:2103.02907
    https://arxiv.org/abs/2103.02907

    Summary: Encodes channel attention along spatial (height and width) directions separately, enabling precise object localization and efficient attention.

    Args:
        in_channels (int): Number of input/output channels.
        reduction (int, optional): Reduction ratio for bottleneck. Default: 32.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, in_channels, reduction=32):
        super().__init__()
        self.pool_h = nn.AdaptiveAvgPool2d((None, 1))
        self.pool_w = nn.AdaptiveAvgPool2d((1, None))
        mid_channels = max(8, in_channels // reduction)
        self.conv1 = nn.Conv2d(
            in_channels, mid_channels, kernel_size=1, stride=1, padding=0
        )
        self.bn1 = nn.BatchNorm2d(mid_channels)
        self.act = nn.ReLU(inplace=True)
        self.conv_h = nn.Conv2d(
            mid_channels, in_channels, kernel_size=1, stride=1, padding=0
        )
        self.conv_w = nn.Conv2d(
            mid_channels, in_channels, kernel_size=1, stride=1, padding=0
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, c, h, w = x.size()
        x_h = self.pool_h(x).permute(0, 1, 3, 2)  # (B, C, 1, H)
        x_w = self.pool_w(x)  # (B, C, W, 1)
        y = torch.cat([x_h, x_w], dim=3)  # (B, C, 1, H+W)
        y = self.conv1(y)
        y = self.bn1(y)
        y = self.act(y)
        x_h, x_w = torch.split(y, [h, w], dim=3)
        x_h = x_h.permute(0, 1, 3, 2)  # (B, C, H, 1)
        x_w = x_w  # (B, C, W, 1)
        a_h = self.sigmoid(self.conv_h(x_h))
        a_w = self.sigmoid(self.conv_w(x_w))
        out = x * a_h * a_w
        return out


class PerformerBlock(nn.Module):
    """
    Performer Attention Block

    Reference: Rethinking Attention with Performers, Krzysztof Choromanski et al., ICLR 2021, arXiv:2009.14794
    https://arxiv.org/abs/2009.14794

    Summary: Approximates softmax attention with linear complexity using random feature maps, enabling efficient long-sequence modeling.

    Args:
        dim (int): Input and output feature dimension.
        num_heads (int): Number of attention heads.
        dim_head (int, optional): Dimension per head. Default: None (dim // num_heads).
        dropout (float, optional): Dropout rate. Default: 0.0.
        nb_features (int, optional): Number of random features for kernel approximation. Default: 256.

    Input:
        x (Tensor): Shape (B, N, dim)
    Output:
        out (Tensor): Shape (B, N, dim)
    """

    def __init__(self, dim, num_heads, dim_head=None, dropout=0.0, nb_features=256):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.dim_head = dim_head or (dim // num_heads)
        self.nb_features = nb_features
        self.to_q = nn.Linear(dim, num_heads * self.dim_head)
        self.to_k = nn.Linear(dim, num_heads * self.dim_head)
        self.to_v = nn.Linear(dim, num_heads * self.dim_head)
        self.dropout = nn.Dropout(dropout)
        self.proj = nn.Linear(num_heads * self.dim_head, dim)

    def prm_exp(self, x):
        # Positive random features for softmax kernel approximation
        # x: (B, N, num_heads, dim_head)
        # Returns: (B, N, num_heads, nb_features)
        B, N, H, D = x.shape
        w = torch.randn(D, self.nb_features, device=x.device) / (D**0.5)
        x_proj = torch.einsum("bnhd,df->bnhf", x, w)
        return torch.exp(x_proj)

    def forward(self, x):
        B, N, _ = x.shape
        q = self.to_q(x).view(B, N, self.num_heads, self.dim_head)
        k = self.to_k(x).view(B, N, self.num_heads, self.dim_head)
        v = self.to_v(x).view(B, N, self.num_heads, self.dim_head)
        q_prime = self.prm_exp(q)
        k_prime = self.prm_exp(k)
        D_inv = 1.0 / (
            torch.einsum("bnhf,bnhf->bnh", q_prime, k_prime.sum(dim=1, keepdim=True))
            + 1e-6
        )
        context = torch.einsum("bnhf,bnhd->bnhfd", k_prime, v).sum(dim=1)
        out = torch.einsum("bnhf,bnhfd,bnh->bnhd", q_prime, context, D_inv)
        out = out.reshape(B, N, self.num_heads * self.dim_head)
        out = self.proj(self.dropout(out))
        return out
