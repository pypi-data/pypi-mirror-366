import torch
import torch.nn as nn


class GroupNorm(nn.Module):
    """
    Group Normalization (GroupNorm)

    Reference: Group Normalization, Yuxin Wu, Kaiming He, ECCV 2018, arXiv:1803.08494
    https://arxiv.org/abs/1803.08494

    Summary: Normalizes features within groups of channels, providing stable training for small batch sizes and strong regularization.

    Args:
        num_groups (int): Number of groups to separate the channels into.
        num_channels (int): Number of channels expected in input.
        eps (float, optional): Value added to denominator for numerical stability. Default: 1e-5.
        affine (bool, optional): If True, adds learnable scale and bias. Default: True.

    Input:
        x (Tensor): Shape (B, C, ...)
    Output:
        out (Tensor): Shape (B, C, ...)
    """

    def __init__(self, num_groups, num_channels, eps=1e-5, affine=True):
        super().__init__()
        self.group_norm = nn.GroupNorm(num_groups, num_channels, eps=eps, affine=affine)

    def forward(self, x):
        return self.group_norm(x)


class SwitchableNorm(nn.Module):
    """
    Switchable Normalization (SwitchableNorm)

    Reference: Switchable Normalization for Learning-to-Normalize Deep Representation, Ping Luo et al., CVPR 2019, arXiv:1806.10779
    https://arxiv.org/abs/1806.10779

    Summary: Learns to combine BatchNorm, InstanceNorm, and LayerNorm adaptively for each channel, improving generalization and stability.

    Args:
        num_features (int): Number of channels/features.
        eps (float, optional): Value added to denominator for numerical stability. Default: 1e-5.
        momentum (float, optional): Momentum for running mean/var (for BatchNorm). Default: 0.1.
        affine (bool, optional): If True, adds learnable scale and bias. Default: True.
        using_moving_average (bool, optional): If True, use running stats for BatchNorm. Default: True.
        using_bn (bool, optional): If True, include BatchNorm in the switch. Default: True.

    Input:
        x (Tensor): Shape (B, C, ...)
    Output:
        out (Tensor): Shape (B, C, ...)
    """

    def __init__(
        self,
        num_features,
        eps=1e-5,
        momentum=0.1,
        affine=True,
        using_moving_average=True,
        using_bn=True,
    ):
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.affine = affine
        self.using_moving_average = using_moving_average
        self.using_bn = using_bn
        self.weight = nn.Parameter(torch.ones(3))
        self.mean_weight = nn.Parameter(torch.ones(3))
        self.var_weight = nn.Parameter(torch.ones(3))
        if affine:
            self.gamma = nn.Parameter(torch.ones(1, num_features, 1, 1))
            self.beta = nn.Parameter(torch.zeros(1, num_features, 1, 1))
        if using_bn:
            self.register_buffer("running_mean", torch.zeros(1, num_features, 1, 1))
            self.register_buffer("running_var", torch.ones(1, num_features, 1, 1))

    def forward(self, x):
        N, C = x.size(0), x.size(1)
        # Instance Norm
        mean_in = x.view(N, C, -1).mean(-1, keepdim=True).view(N, C, 1, 1)
        var_in = x.view(N, C, -1).var(-1, keepdim=True, unbiased=False).view(N, C, 1, 1)
        # Layer Norm
        mean_ln = x.view(N, -1).mean(-1, keepdim=True).view(N, 1, 1, 1)
        var_ln = x.view(N, -1).var(-1, keepdim=True, unbiased=False).view(N, 1, 1, 1)
        # Batch Norm
        if self.using_bn:
            if self.training or not self.using_moving_average:
                mean_bn = x.view(N, C, -1).mean((0, 2), keepdim=True).view(1, C, 1, 1)
                var_bn = (
                    x.view(N, C, -1)
                    .var((0, 2), keepdim=True, unbiased=False)
                    .view(1, C, 1, 1)
                )
                if self.training:
                    self.running_mean = (
                        1 - self.momentum
                    ) * self.running_mean + self.momentum * mean_bn.detach()
                    self.running_var = (
                        1 - self.momentum
                    ) * self.running_var + self.momentum * var_bn.detach()
            else:
                mean_bn = self.running_mean
                var_bn = self.running_var
        else:
            mean_bn = torch.zeros_like(mean_in)
            var_bn = torch.ones_like(var_in)
        # Softmax weights
        mean_weight = torch.softmax(self.mean_weight, 0)
        var_weight = torch.softmax(self.var_weight, 0)
        mean = (
            mean_weight[0] * mean_in
            + mean_weight[1] * mean_ln
            + mean_weight[2] * mean_bn
        )
        var = var_weight[0] * var_in + var_weight[1] * var_ln + var_weight[2] * var_bn
        out = (x - mean) / (var + self.eps).sqrt()
        if self.affine:
            out = out * self.gamma + self.beta
        return out


class DropBlock2D(nn.Module):
    """
    DropBlock Regularization (2D)

    Reference: DropBlock: A regularization method for convolutional networks, Golnaz Ghiasi et al., NeurIPS 2018, arXiv:1810.12890
    https://arxiv.org/abs/1810.12890

    Summary: Regularization technique that drops contiguous regions (blocks) of feature maps, improving generalization for convolutional networks.

    Args:
        block_size (int): Size of the block to drop.
        drop_prob (float): Probability of dropping a block.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, block_size, drop_prob):
        super().__init__()
        self.block_size = block_size
        self.drop_prob = drop_prob

    def forward(self, x):
        if not self.training or self.drop_prob == 0.0:
            return x
        gamma = self._compute_gamma(x)
        mask = (torch.rand(x.shape[0], *x.shape[2:], device=x.device) < gamma).float()
        mask = mask.unsqueeze(1)
        block_mask = self._compute_block_mask(mask)
        countM = block_mask.numel()
        count_ones = block_mask.sum().item()
        return block_mask * x * (countM / (count_ones + 1e-7))

    def _compute_block_mask(self, mask):
        block_mask = nn.functional.max_pool2d(
            input=mask,
            kernel_size=(self.block_size, self.block_size),
            stride=(1, 1),
            padding=self.block_size // 2,
        )
        block_mask = 1 - block_mask
        return block_mask

    def _compute_gamma(self, x):
        B, C, H, W = x.shape
        return (
            self.drop_prob
            / (self.block_size**2)
            * (H * W)
            / ((H - self.block_size + 1) * (W - self.block_size + 1))
        )
