import torch
import torch.nn as nn
import torch.nn.functional as F


class UNet(nn.Module):
    """
    U-Net: Convolutional Networks for Biomedical Image Segmentation

    出处: U-Net: Convolutional Networks for Biomedical Image Segmentation, Olaf Ronneberger et al., MICCAI 2015, arXiv:1505.04597
    论文链接: https://arxiv.org/abs/1505.04597

    简介: 经典的U型结构，采用编码器-解码器和跳跃连接，广泛应用于医学图像分割等像素级任务。
    """

    def __init__(self, in_channels=1, out_channels=1, features=[64, 128, 256, 512]):
        super().__init__()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        # 下采样部分
        for feature in features:
            self.downs.append(self._block(in_channels, feature))
            in_channels = feature
        # 上采样部分
        for feature in reversed(features):
            self.ups.append(
                nn.ConvTranspose2d(feature * 2, feature, kernel_size=2, stride=2)
            )
            self.ups.append(self._block(feature * 2, feature))
        self.bottleneck = self._block(features[-1], features[-1] * 2)
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        skip_connections = []
        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = F.max_pool2d(x, 2)
        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]
        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip_connection = skip_connections[idx // 2]
            if x.shape != skip_connection.shape:
                x = F.interpolate(x, size=skip_connection.shape[2:])
            x = torch.cat((skip_connection, x), dim=1)
            x = self.ups[idx + 1](x)
        return self.final_conv(x)

    @staticmethod
    def _block(in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


class UNetPlusPlus(nn.Module):
    """
    UNet++: A Nested U-Net Architecture for Medical Image Segmentation

    出处: UNet++: A Nested U-Net Architecture for Medical Image Segmentation, Zongwei Zhou et al., DLMIA 2018, arXiv:1807.10165
    论文链接: https://arxiv.org/abs/1807.10165

    简介: 在UNet基础上引入密集跳跃连接和深层监督，提升分割精度，广泛应用于医学图像分割等任务。
    """

    def __init__(self, in_channels=1, out_channels=1, features=[64, 128, 256, 512]):
        super().__init__()
        self.depth = len(features)
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.conv_blocks = nn.ModuleDict()
        # 下采样部分
        prev_channels = in_channels
        for d, feature in enumerate(features):
            self.downs.append(self._conv_block(prev_channels, feature))
            prev_channels = feature
        # 嵌套跳跃连接部分
        for i in range(self.depth):
            for j in range(1, self.depth - i):
                self.conv_blocks[f"conv{i}_{j}"] = self._conv_block(
                    features[i] * (j + 1), features[i]
                )
        # 上采样部分
        for feature in reversed(features):
            self.ups.append(
                nn.ConvTranspose2d(feature * 2, feature, kernel_size=2, stride=2)
            )
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        # 存储每层每阶段的特征
        xs = [[None] * self.depth for _ in range(self.depth)]
        # 下采样主干
        for i in range(self.depth):
            if i == 0:
                xs[i][0] = self.downs[i](x)
            else:
                xs[i][0] = self.downs[i](nn.functional.max_pool2d(xs[i - 1][0], 2))
        # 嵌套跳跃连接
        for j in range(1, self.depth):
            for i in range(self.depth - j):
                upsampled = nn.functional.interpolate(
                    xs[i + 1][j - 1],
                    size=xs[i][0].shape[2:],
                    mode="bilinear",
                    align_corners=True,
                )
                concat = torch.cat([xs[i][k] for k in range(j)] + [upsampled], dim=1)
                xs[i][j] = self.conv_blocks[f"conv{i}_{j}"](concat)
        # 上采样解码
        x = xs[0][self.depth - 1]
        for i, up in enumerate(self.ups):
            if i < self.depth - 1:
                x = up(x)
        x = self.final_conv(x)
        return x

    @staticmethod
    def _conv_block(in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )


class DeepLabV3PlusBlock(nn.Module):
    """
    DeepLabV3+ Block（DeepLabV3+分割结构）

    出处: Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation (DeepLabV3+), Liang-Chieh Chen et al., ECCV 2018, arXiv:1802.02611
    论文链接: https://arxiv.org/abs/1802.02611

    简介: 结合空洞空间金字塔池化（ASPP）和编码器-解码器结构，提升分割精度，广泛应用于语义分割任务。
    """

    def __init__(
        self, in_channels, num_classes, aspp_out_channels=256, atrous_rates=(12, 24, 36)
    ):
        super().__init__()
        self.aspp = ASPP(in_channels, aspp_out_channels, atrous_rates)
        self.decoder = nn.Sequential(
            nn.Conv2d(aspp_out_channels, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, num_classes, 1),
        )

    def forward(self, x):
        x = self.aspp(x)
        x = self.decoder(x)
        return x


class ASPP(nn.Module):
    """
    Atrous Spatial Pyramid Pooling (ASPP)

    出处: Rethinking Atrous Convolution for Semantic Image Segmentation (DeepLabV3), Liang-Chieh Chen et al., arXiv:1706.05587
    论文链接: https://arxiv.org/abs/1706.05587

    简介: 通过多尺度空洞卷积并行提取特征，实现多尺度上下文信息融合。
    """

    def __init__(self, in_channels, out_channels, atrous_rates):
        super().__init__()
        modules = [
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        ]
        for rate in atrous_rates:
            modules.extend(
                [
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
                ]
            )
        self.convs = nn.ModuleList(modules)
        self.project = nn.Sequential(
            nn.Conv2d(
                len(atrous_rates) * out_channels + out_channels,
                out_channels,
                1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        res = []
        res.append(self.convs[0](x))
        for i in range(1, len(self.convs), 3):
            res.append(self.convs[i + 2](self.convs[i + 1](self.convs[i](x))))
        x = torch.cat(res, dim=1)
        x = self.project(x)
        return x


class FPNBlock(nn.Module):
    """
    Feature Pyramid Network Block（特征金字塔网络，FPN）

    出处: Feature Pyramid Networks for Object Detection, Tsung-Yi Lin et al., CVPR 2017, arXiv:1612.03144
    论文链接: https://arxiv.org/abs/1612.03144

    简介: 通过自顶向下和横向连接融合多尺度特征，提升目标检测和分割的多尺度表达能力。
    """

    def __init__(self, in_channels_list, out_channels):
        super().__init__()
        # 横向1x1卷积统一通道数
        self.lateral_convs = nn.ModuleList(
            [
                nn.Conv2d(in_channels, out_channels, 1)
                for in_channels in in_channels_list
            ]
        )
        # 自顶向下3x3卷积平滑
        self.smooth_convs = nn.ModuleList(
            [
                nn.Conv2d(out_channels, out_channels, 3, padding=1)
                for _ in in_channels_list
            ]
        )

    def forward(self, inputs):
        # inputs: list of feature maps (C_i, H_i, W_i), from high to low resolution
        laterals = [l_conv(x) for l_conv, x in zip(self.lateral_convs, inputs)]
        for i in range(len(laterals) - 1, 0, -1):
            upsample = nn.functional.interpolate(
                laterals[i], size=laterals[i - 1].shape[2:], mode="nearest"
            )
            laterals[i - 1] += upsample
        outs = [self.smooth_convs[i](laterals[i]) for i in range(len(laterals))]
        return outs
