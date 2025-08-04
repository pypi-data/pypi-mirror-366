import torch
import torch.nn as nn


class ResidualBlock(nn.Module):
    """
    Residual Block (ResNet Basic Block)

    Reference: Deep Residual Learning for Image Recognition, Kaiming He et al., CVPR 2016, arXiv:1512.03385
    https://arxiv.org/abs/1512.03385

    Summary: Enables identity mapping and cross-layer information flow, alleviating degradation in deep networks. Core block of ResNet.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        stride (int, optional): Stride for the first convolution. Default: 1.
        downsample (nn.Module, optional): Downsampling layer for the shortcut. Default: None.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self, in_channels, out_channels, stride=1, downsample=None, group_norm=False
    ):
        super().__init__()
        self.conv1 = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        if group_norm:
            self.bn1 = nn.GroupNorm(out_channels, out_channels)
        else:
            self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(
            out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False
        )
        if group_norm:
            self.bn2 = nn.GroupNorm(out_channels, out_channels)
        else:
            self.bn2 = nn.BatchNorm2d(out_channels)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        out = self.relu(out)
        return out


class BottleneckBlock(nn.Module):
    """
    Bottleneck Block (ResNet Bottleneck)

    Reference: Deep Residual Learning for Image Recognition, Kaiming He et al., CVPR 2016, arXiv:1512.03385
    https://arxiv.org/abs/1512.03385

    Summary: Uses 1x1-3x3-1x1 convolutions to improve parameter efficiency in deep networks. Core block of ResNet-50/101/152.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels (before expansion).
        stride (int, optional): Stride for the 3x3 convolution. Default: 1.
        downsample (nn.Module, optional): Downsampling layer for the shortcut. Default: None.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels * expansion, H_out, W_out)
    """

    expansion = 4

    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(
            out_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(
            out_channels, out_channels * self.expansion, kernel_size=1, bias=False
        )
        self.bn3 = nn.BatchNorm2d(out_channels * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        if downsample is None and (
            stride != 1 or in_channels != out_channels * self.expansion
        ):
            self.downsample = nn.Sequential(
                nn.Conv2d(
                    in_channels,
                    out_channels * self.expansion,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(out_channels * self.expansion),
            )
        else:
            self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv3(out)
        out = self.bn3(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        out = self.relu(out)
        return out


class DepthwiseSeparableConv(nn.Module):
    """
    Depthwise Separable Convolution

    Reference: MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications, Andrew G. Howard et al., arXiv:1704.04861, 2017
    https://arxiv.org/abs/1704.04861

    Summary: Factorizes standard convolution into depthwise and pointwise convolutions, greatly reducing parameters and computation. Core block of MobileNet.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        kernel_size (int, optional): Kernel size for depthwise convolution. Default: 3.
        stride (int, optional): Stride for depthwise convolution. Default: 1.
        padding (int, optional): Padding for depthwise convolution. Default: 1.
        bias (bool, optional): Whether to use bias in convolutions. Default: False.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self, in_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False
    ):
        super().__init__()
        self.depthwise = nn.Conv2d(
            in_channels,
            in_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            groups=in_channels,
            bias=bias,
        )
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=bias)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        out = self.depthwise(x)
        out = self.pointwise(out)
        out = self.bn(out)
        out = self.relu(out)
        return out


class InvertedResidualBlock(nn.Module):
    """
    Inverted Residual Block (MobileNetV2/V3 Core)

    Reference: MobileNetV2: Inverted Residuals and Linear Bottlenecks, Mark Sandler et al., CVPR 2018, arXiv:1801.04381
    https://arxiv.org/abs/1801.04381

    Summary: Expands channels, applies depthwise separable convolution, then projects back. Core block of MobileNetV2/V3.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        stride (int): Stride for depthwise convolution.
        expand_ratio (int): Expansion ratio for hidden dimension.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(self, in_channels, out_channels, stride, expand_ratio):
        super().__init__()
        hidden_dim = in_channels * expand_ratio
        self.use_res_connect = stride == 1 and in_channels == out_channels

        layers = []
        if expand_ratio != 1:
            # 1x1 pointwise conv (expand)
            layers.append(nn.Conv2d(in_channels, hidden_dim, 1, 1, 0, bias=False))
            layers.append(nn.BatchNorm2d(hidden_dim))
            layers.append(nn.ReLU6(inplace=True))
        # 3x3 depthwise conv
        layers.append(
            nn.Conv2d(
                hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False
            )
        )
        layers.append(nn.BatchNorm2d(hidden_dim))
        layers.append(nn.ReLU6(inplace=True))
        # 1x1 pointwise conv (project)
        layers.append(nn.Conv2d(hidden_dim, out_channels, 1, 1, 0, bias=False))
        layers.append(nn.BatchNorm2d(out_channels))
        self.conv = nn.Sequential(*layers)

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)


class DenseBlock(nn.Module):
    """
    Dense Block (DenseNet Core)

    Reference: Densely Connected Convolutional Networks (DenseNet), Gao Huang et al., CVPR 2017, arXiv:1608.06993
    https://arxiv.org/abs/1608.06993

    Summary: Each layer receives input from all previous layers, enabling feature reuse and efficient gradient flow. Core block of DenseNet.

    Args:
        in_channels (int): Number of input channels.
        growth_rate (int): Growth rate of output channels per layer.
        num_layers (int): Number of layers in the block.
        bn_size (int, optional): Bottleneck size. Default: 4.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, in_channels + growth_rate * num_layers, H, W)
    """

    def __init__(self, in_channels, growth_rate, num_layers, bn_size=4):
        super().__init__()
        self.layers = nn.ModuleList()
        channels = in_channels
        for i in range(num_layers):
            self.layers.append(self._make_layer(channels, growth_rate, bn_size))
            channels += growth_rate

    def _make_layer(self, in_channels, growth_rate, bn_size):
        return nn.Sequential(
            nn.BatchNorm2d(in_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels, bn_size * growth_rate, kernel_size=1, bias=False),
            nn.BatchNorm2d(bn_size * growth_rate),
            nn.ReLU(inplace=True),
            nn.Conv2d(
                bn_size * growth_rate, growth_rate, kernel_size=3, padding=1, bias=False
            ),
        )

    def forward(self, x):
        features = [x]
        for layer in self.layers:
            new_feat = layer(torch.cat(features, 1))
            features.append(new_feat)
        return torch.cat(features, 1)


class FireModule(nn.Module):
    """
    Fire Module (SqueezeNet Core)

    Reference: SqueezeNet: AlexNet-level accuracy with 50x fewer parameters and <0.5MB model size, Forrest N. Iandola et al., arXiv:1602.07360, 2016
    https://arxiv.org/abs/1602.07360

    Summary: Squeezes channels with 1x1 conv, then expands with 1x1 and 3x3 convs. Core block of SqueezeNet.

    Args:
        in_channels (int): Number of input channels.
        squeeze_channels (int): Number of squeeze (1x1) channels.
        expand1x1_channels (int): Number of expand 1x1 channels.
        expand3x3_channels (int): Number of expand 3x3 channels.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, expand1x1_channels + expand3x3_channels, H, W)
    """

    def __init__(
        self, in_channels, squeeze_channels, expand1x1_channels, expand3x3_channels
    ):
        super().__init__()
        self.squeeze = nn.Conv2d(in_channels, squeeze_channels, kernel_size=1)
        self.squeeze_activation = nn.ReLU(inplace=True)
        self.expand1x1 = nn.Conv2d(squeeze_channels, expand1x1_channels, kernel_size=1)
        self.expand3x3 = nn.Conv2d(
            squeeze_channels, expand3x3_channels, kernel_size=3, padding=1
        )
        self.expand_activation = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.squeeze_activation(self.squeeze(x))
        out1 = self.expand1x1(x)
        out2 = self.expand3x3(x)
        out = torch.cat([out1, out2], 1)
        out = self.expand_activation(out)
        return out


class VisionTransformerBlock(nn.Module):
    """
    Vision Transformer Block (ViT)

    Reference: An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale, Alexey Dosovitskiy et al., ICLR 2021, arXiv:2010.11929
    https://arxiv.org/abs/2010.11929

    Summary: Splits image into patches, applies linear projection and position encoding, then stacks Transformer encoder layers for image recognition.

    Args:
        embed_dim (int): Embedding dimension.
        num_heads (int): Number of attention heads.
        ff_dim (int): Feedforward network dimension.
        dropout (float, optional): Dropout rate. Default: 0.1.

    Input:
        x (Tensor): Shape (B, N, embed_dim), N = number of patches
    Output:
        out (Tensor): Shape (B, N, embed_dim)
    """

    def __init__(self, embed_dim, num_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.encoder = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=dropout,
            batch_first=True,
        )

    def forward(self, x):
        # x: (B, N, C)  N为patch数，C为embed_dim
        return self.encoder(x)


class ResNeXtBlock(nn.Module):
    """
    ResNeXt Block (Grouped Convolution Residual Block)

    Reference: Aggregated Residual Transformations for Deep Neural Networks (ResNeXt), Saining Xie et al., CVPR 2017, arXiv:1611.05431
    https://arxiv.org/abs/1611.05431

    Summary: Uses grouped convolutions to improve model expressiveness and efficiency. Core block of ResNeXt.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        stride (int, optional): Stride for the 3x3 convolution. Default: 1.
        cardinality (int, optional): Number of groups. Default: 32.
        base_width (int, optional): Base width for each group. Default: 4.
        downsample (nn.Module, optional): Downsampling layer for the shortcut. Default: None.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        stride=1,
        cardinality=32,
        base_width=4,
        downsample=None,
    ):
        super().__init__()
        D = max(1, int(math.floor(out_channels * (base_width / 64.0))))
        C = cardinality
        self.conv1 = nn.Conv2d(in_channels, D * C, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(D * C)
        self.conv2 = nn.Conv2d(
            D * C, D * C, kernel_size=3, stride=stride, padding=1, groups=C, bias=False
        )
        self.bn2 = nn.BatchNorm2d(D * C)
        self.conv3 = nn.Conv2d(D * C, out_channels, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv3(out)
        out = self.bn3(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        out = self.relu(out)
        return out


import math


class GhostModule(nn.Module):
    """
    Ghost Module (GhostNet Core)

    Reference: GhostNet: More Features from Cheap Operations, Kai Han et al., CVPR 2020, arXiv:1911.11907
    https://arxiv.org/abs/1911.11907

    Summary: Generates redundant features using cheap operations after a primary convolution, improving efficiency in lightweight networks. Core block of GhostNet.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        kernel_size (int, optional): Kernel size for primary convolution. Default: 1.
        ratio (int, optional): Ratio of output channels for primary conv. Default: 2.
        dw_kernel_size (int, optional): Kernel size for depthwise conv. Default: 3.
        stride (int, optional): Stride for primary conv. Default: 1.
        relu (bool, optional): Whether to use ReLU activation. Default: True.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size=1,
        ratio=2,
        dw_kernel_size=3,
        stride=1,
        relu=True,
    ):
        super().__init__()
        init_channels = int(out_channels / ratio)
        new_channels = out_channels - init_channels
        self.primary_conv = nn.Sequential(
            nn.Conv2d(
                in_channels,
                init_channels,
                kernel_size,
                stride,
                kernel_size // 2,
                bias=False,
            ),
            nn.BatchNorm2d(init_channels),
            nn.ReLU(inplace=True) if relu else nn.Identity(),
        )
        self.cheap_operation = nn.Sequential(
            nn.Conv2d(
                init_channels,
                new_channels,
                dw_kernel_size,
                1,
                dw_kernel_size // 2,
                groups=init_channels,
                bias=False,
            ),
            nn.BatchNorm2d(new_channels),
            nn.ReLU(inplace=True) if relu else nn.Identity(),
        )

    def forward(self, x):
        x1 = self.primary_conv(x)
        x2 = self.cheap_operation(x1)
        out = torch.cat([x1, x2], dim=1)
        return out[
            :,
            : self.primary_conv[0].out_channels + self.cheap_operation[0].out_channels,
            ...,
        ]


class SpatialPyramidPooling(nn.Module):
    """
    Spatial Pyramid Pooling (SPP)

    Reference: Spatial Pyramid Pooling in Deep Convolutional Networks for Visual Recognition, Kaiming He et al., ECCV 2014, arXiv:1406.4729
    https://arxiv.org/abs/1406.4729

    Summary: Applies multi-scale pooling and concatenates features, enabling input-size-invariant representations. Widely used in detection (e.g., YOLO).

    Args:
        pool_sizes (tuple of int, optional): Output sizes for each pooling level. Default: (1, 2, 4).

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, N), N = sum of all pooled features per channel
    """

    def __init__(self, pool_sizes=(1, 2, 4)):
        super().__init__()
        self.pool_sizes = pool_sizes

    def forward(self, x):
        b, c, h, w = x.size()
        features = [x]
        for size in self.pool_sizes:
            pool = nn.functional.adaptive_max_pool2d(x, output_size=(size, size))
            features.append(pool.view(b, c, -1))
        out = torch.cat([features[0].view(b, c, -1)] + features[1:], dim=2)
        out = out.view(b, c, -1)
        return out


class ASPPBlock(nn.Module):
    """
    Atrous Spatial Pyramid Pooling Block (ASPP)

    Reference: Rethinking Atrous Convolution for Semantic Image Segmentation (DeepLabV3), Liang-Chieh Chen et al., arXiv:1706.05587
    https://arxiv.org/abs/1706.05587

    Summary: Uses parallel atrous convolutions at multiple rates to capture multi-scale context. Core module of DeepLab series.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        atrous_rates (tuple of int, optional): Dilation rates for parallel convolutions. Default: (6, 12, 18).

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H, W)
    """

    def __init__(self, in_channels, out_channels, atrous_rates=(6, 12, 18)):
        super().__init__()
        self.convs = nn.ModuleList()
        # 1x1卷积分支
        self.convs.append(
            nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, bias=False),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(inplace=True),
            )
        )
        # 多尺度空洞卷积分支
        for rate in atrous_rates:
            self.convs.append(
                nn.Sequential(
                    nn.Conv2d(
                        in_channels,
                        out_channels,
                        3,
                        padding=rate,
                        dilation=rate,
                        bias=False,
                    ),
                    nn.BatchNorm2d(out_channels),
                    nn.ReLU(inplace=True),
                )
            )
        # 全局池化分支
        self.global_pool = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )
        self.project = nn.Sequential(
            nn.Conv2d(
                (len(atrous_rates) + 2) * out_channels, out_channels, 1, bias=False
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        res = [conv(x) for conv in self.convs]
        # 全局池化分支
        gp = self.global_pool(x)
        gp = nn.functional.interpolate(
            gp, size=x.shape[2:], mode="bilinear", align_corners=True
        )
        res.append(gp)
        x = torch.cat(res, dim=1)
        x = self.project(x)
        return x


class PANetBlock(nn.Module):
    """
    Path Aggregation Network Block (PANet)

    Reference: Path Aggregation Network for Instance Segmentation, Shu Liu et al., CVPR 2018, arXiv:1803.01534
    https://arxiv.org/abs/1803.01534

    Summary: Enhances information flow in both top-down and bottom-up paths, improving multi-scale feature fusion for detection and segmentation.

    Args:
        in_channels_list (list of int): Number of input channels for each feature level.
        out_channels (int): Number of output channels for each feature level.

    Input:
        inputs (list of Tensor): List of feature maps from high to low resolution, each of shape (B, C_i, H_i, W_i)
    Output:
        outs (list of Tensor): List of fused feature maps, each of shape (B, out_channels, H_i, W_i)
    """

    def __init__(self, in_channels_list, out_channels):
        super().__init__()
        self.lateral_convs = nn.ModuleList(
            [
                nn.Conv2d(in_channels, out_channels, 1)
                for in_channels in in_channels_list
            ]
        )
        self.smooth_convs = nn.ModuleList(
            [
                nn.Conv2d(out_channels, out_channels, 3, padding=1)
                for _ in in_channels_list
            ]
        )
        self.bottom_up_convs = nn.ModuleList(
            [
                nn.Conv2d(out_channels, out_channels, 3, stride=2, padding=1)
                for _ in range(len(in_channels_list) - 1)
            ]
        )

    def forward(self, inputs):
        # Top-down path (FPN style)
        laterals = [l_conv(x) for l_conv, x in zip(self.lateral_convs, inputs)]
        for i in range(len(laterals) - 1, 0, -1):
            upsample = nn.functional.interpolate(
                laterals[i], size=laterals[i - 1].shape[2:], mode="nearest"
            )
            laterals[i - 1] += upsample
        # Bottom-up path
        outs = [self.smooth_convs[i](laterals[i]) for i in range(len(laterals))]
        for i in range(len(outs) - 1):
            down = self.bottom_up_convs[i](outs[i])
            outs[i + 1] += down
        return outs


class BiFPNBlock(nn.Module):
    """
    Bi-directional Feature Pyramid Network Block (BiFPN)

    Reference: EfficientDet: Scalable and Efficient Object Detection, Mingxing Tan et al., CVPR 2020, arXiv:1911.09070
    https://arxiv.org/abs/1911.09070

    Summary: Fuses multi-scale features in both top-down and bottom-up directions with learnable weights, improving feature representation for detection.

    Args:
        in_channels_list (list of int): Number of input channels for each feature level.
        out_channels (int): Number of output channels for each feature level.
        num_layers (int, optional): Number of BiFPN layers to stack. Default: 1.

    Input:
        inputs (list of Tensor): List of feature maps from high to low resolution, each of shape (B, C_i, H_i, W_i)
    Output:
        outs (list of Tensor): List of fused feature maps, each of shape (B, out_channels, H_i, W_i)
    """

    def __init__(self, in_channels_list, out_channels, num_layers=1):
        super().__init__()
        self.num_layers = num_layers
        self.out_channels = out_channels
        self.input_convs = nn.ModuleList(
            [
                nn.Conv2d(in_channels, out_channels, 1)
                for in_channels in in_channels_list
            ]
        )
        self.bifpn_layers = nn.ModuleList(
            [BiFPNLayer(len(in_channels_list), out_channels) for _ in range(num_layers)]
        )

    def forward(self, inputs):
        feats = [conv(x) for conv, x in zip(self.input_convs, inputs)]
        for layer in self.bifpn_layers:
            feats = layer(feats)
        return feats


class BiFPNLayer(nn.Module):
    def __init__(self, num_levels, out_channels):
        super().__init__()
        self.num_levels = num_levels
        self.w1 = nn.Parameter(torch.ones(num_levels - 1, 2))
        self.w2 = nn.Parameter(torch.ones(num_levels - 1, 2))
        self.eps = 1e-4
        self.convs = nn.ModuleList(
            [
                nn.Conv2d(
                    out_channels,
                    out_channels,
                    3,
                    padding=1,
                    groups=out_channels,
                    bias=False,
                )
                for _ in range(num_levels)
            ]
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, feats):
        # Top-down pathway
        td = [feats[-1]]
        for i in range(self.num_levels - 2, -1, -1):
            w = self.relu(self.w1[i])
            w = w / (w.sum() + self.eps)
            up = nn.functional.interpolate(
                td[0], size=feats[i].shape[2:], mode="nearest"
            )
            td.insert(0, w[0] * feats[i] + w[1] * up)
        # Bottom-up pathway
        bu = [td[0]]
        for i in range(1, self.num_levels):
            w = self.relu(self.w2[i - 1])
            w = w / (w.sum() + self.eps)
            down = nn.functional.max_pool2d(bu[-1], 2)
            bu.append(w[0] * td[i] + w[1] * down)
        outs = [self.convs[i](bu[i]) for i in range(self.num_levels)]
        return outs


class PSPModule(nn.Module):
    """
    Pyramid Scene Parsing Module (PSPModule)

    Reference: Pyramid Scene Parsing Network, Hengshuang Zhao et al., CVPR 2017, arXiv:1612.01105
    https://arxiv.org/abs/1612.01105

    Summary: Aggregates context information at multiple spatial scales using parallel pooling, improving scene parsing and segmentation.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        pool_sizes (tuple of int, optional): Output sizes for each pooling level. Default: (1, 2, 3, 6).

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H, W)
    """

    def __init__(self, in_channels, out_channels, pool_sizes=(1, 2, 3, 6)):
        super().__init__()
        self.stages = nn.ModuleList(
            [
                nn.Sequential(
                    nn.AdaptiveAvgPool2d(output_size=ps),
                    nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False),
                    nn.BatchNorm2d(out_channels),
                    nn.ReLU(inplace=True),
                )
                for ps in pool_sizes
            ]
        )
        self.bottleneck = nn.Sequential(
            nn.Conv2d(
                in_channels + len(pool_sizes) * out_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        h, w = x.size(2), x.size(3)
        pyramids = [x]
        for stage in self.stages:
            out = stage(x)
            out = nn.functional.interpolate(
                out, size=(h, w), mode="bilinear", align_corners=True
            )
            pyramids.append(out)
        output = torch.cat(pyramids, dim=1)
        output = self.bottleneck(output)
        return output


class SwinTransformerBlock(nn.Module):
    """
    Swin Transformer Block

    Reference: Swin Transformer: Hierarchical Vision Transformer using Shifted Windows, Ze Liu et al., ICCV 2021, arXiv:2103.14030
    https://arxiv.org/abs/2103.14030

    Summary: Applies self-attention within local windows and shifts windows between layers, enabling hierarchical and efficient vision transformers.

    Args:
        dim (int): Number of input/output channels.
        num_heads (int): Number of attention heads.
        window_size (int): Window size for local self-attention.
        shift_size (int, optional): Shift size for window partition. Default: 0 (no shift).
        mlp_ratio (float, optional): Ratio of MLP hidden dim to embedding dim. Default: 4.0.
        dropout (float, optional): Dropout rate. Default: 0.0.
        attn_dropout (float, optional): Attention dropout rate. Default: 0.0.
        drop_path (float, optional): Stochastic depth rate. Default: 0.0.

    Input:
        x (Tensor): Shape (B, H, W, C)
    Output:
        out (Tensor): Shape (B, H, W, C)
    """

    def __init__(
        self,
        dim,
        num_heads,
        window_size,
        shift_size=0,
        mlp_ratio=4.0,
        dropout=0.0,
        attn_dropout=0.0,
        drop_path=0.0,
    ):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.window_size = window_size
        self.shift_size = shift_size
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(
            dim, num_heads, dropout=attn_dropout, batch_first=True
        )
        self.drop_path = nn.Identity()  # For simplicity, no stochastic depth here
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, int(dim * mlp_ratio)),
            nn.GELU(),
            nn.Linear(int(dim * mlp_ratio), dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        # x: (B, H, W, C)
        B, H, W, C = x.shape
        x = x.view(B, H * W, C)
        shortcut = x
        x = self.norm1(x)
        attn_out, _ = self.attn(x, x, x)
        x = shortcut + attn_out
        x = x + self.mlp(self.norm2(x))
        x = x.view(B, H, W, C)
        return x


class ConvNeXtBlock(nn.Module):
    """
    ConvNeXt Block

    Reference: A ConvNet for the 2020s, Zhuang Liu et al., CVPR 2022, arXiv:2201.03545
    https://arxiv.org/abs/2201.03545

    Summary: Modernizes the ResNet block with depthwise conv, large kernel, layer norm, and pointwise convs, achieving state-of-the-art performance.

    Args:
        dim (int): Number of input/output channels.
        drop_path (float, optional): Stochastic depth rate. Default: 0.0.
        layer_scale_init_value (float, optional): Initial value for layer scale. Default: 1e-6.

    Input:
        x (Tensor): Shape (B, C, H, W)
    Output:
        out (Tensor): Shape (B, C, H, W)
    """

    def __init__(self, dim, drop_path=0.0, layer_scale_init_value=1e-6):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim)
        self.norm = nn.LayerNorm(dim, eps=1e-6)
        self.pwconv1 = nn.Linear(dim, 4 * dim)
        self.act = nn.GELU()
        self.pwconv2 = nn.Linear(4 * dim, dim)
        self.gamma = nn.Parameter(
            layer_scale_init_value * torch.ones((dim)), requires_grad=True
        )
        self.drop_path = nn.Identity()  # For simplicity, no stochastic depth here

    def forward(self, x):
        shortcut = x
        x = self.dwconv(x)
        x = x.permute(0, 2, 3, 1)  # (B, H, W, C)
        x = self.norm(x)
        x = self.pwconv1(x)
        x = self.act(x)
        x = self.pwconv2(x)
        x = self.gamma * x
        x = x.permute(0, 3, 1, 2)  # (B, C, H, W)
        x = shortcut + self.drop_path(x)
        return x


class CBAMBlock(nn.Module):
    """
    Convolutional Block Attention Module (CBAM)

    Reference: CBAM: Convolutional Block Attention Module, Sanghyun Woo et al., ECCV 2018, arXiv:1807.06521
    https://arxiv.org/abs/1807.06521

    Summary: Combines Channel and Spatial attention mechanisms to improve feature representation.

    Args:
        channels (int): Number of input/output channels.
        reduction_ratio (int, optional): Channel reduction ratio. Default: 16.
        kernel_size (int, optional): Kernel size for spatial attention. Default: 7.

    Input:
        x (Tensor): Shape (B, channels, H, W)
    Output:
        out (Tensor): Shape (B, channels, H, W)
    """

    def __init__(self, channels, reduction_ratio=16, kernel_size=7):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc1 = nn.Conv2d(
            channels, channels // reduction_ratio, kernel_size=1, bias=False
        )
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Conv2d(
            channels // reduction_ratio, channels, kernel_size=1, bias=False
        )
        self.sigmoid_channel = nn.Sigmoid()

        self.conv_after_concat = nn.Conv2d(
            2, 1, kernel_size=kernel_size, padding=kernel_size // 2, bias=False
        )
        self.sigmoid_spatial = nn.Sigmoid()

    def forward(self, x):
        # Channel attention
        avg_out = self.fc2(self.relu(self.fc1(self.avg_pool(x))))
        max_out = self.fc2(self.relu(self.fc1(self.max_pool(x))))
        channel_out = self.sigmoid_channel(avg_out + max_out)

        # Spatial attention
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out = torch.max(x, dim=1, keepdim=True)[0]
        spatial_out = torch.cat([avg_out, max_out], dim=1)
        spatial_out = self.conv_after_concat(spatial_out)
        spatial_out = self.sigmoid_spatial(spatial_out)

        # Combine channel and spatial attention
        out = x * channel_out * spatial_out
        return out


class CoordinateAttention(nn.Module):
    """
    Coordinate Attention (CA)

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


class FPNBlock(nn.Module):
    """
    Feature Pyramid Network Block (FPN)

    Reference: Feature Pyramid Networks for Object Detection, Tsung-Yi Lin et al., CVPR 2017, arXiv:1612.03144
    https://arxiv.org/abs/1612.03144

    Summary: Combines features from different scales to improve object detection and segmentation.

    Args:
        in_channels_list (list of int): Number of input channels for each feature level.
        out_channels (int): Number of output channels for the final fused feature.

    Input:
        inputs (list of Tensor): List of feature maps from high to low resolution, each of shape (B, C_i, H_i, W_i)
    Output:
        out (Tensor): Shape (B, out_channels, H_i, W_i) for each input level
    """

    def __init__(self, in_channels_list, out_channels):
        super().__init__()
        self.lateral_convs = nn.ModuleList(
            [
                nn.Conv2d(in_channels, out_channels, 1)
                for in_channels in in_channels_list
            ]
        )
        self.smooth_convs = nn.ModuleList(
            [
                nn.Conv2d(out_channels, out_channels, 3, padding=1)
                for _ in in_channels_list
            ]
        )

    def forward(self, inputs):
        # Top-down path (FPN style)
        laterals = [l_conv(x) for l_conv, x in zip(self.lateral_convs, inputs)]
        for i in range(len(laterals) - 1, 0, -1):
            upsample = nn.functional.interpolate(
                laterals[i], size=laterals[i - 1].shape[2:], mode="nearest"
            )
            laterals[i - 1] += upsample
        # Bottom-up path
        outs = [self.smooth_convs[i](laterals[i]) for i in range(len(laterals))]
        return outs
