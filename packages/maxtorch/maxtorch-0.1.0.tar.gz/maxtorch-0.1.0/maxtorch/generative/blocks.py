import torch
import torch.nn as nn


class PixelShuffleBlock(nn.Module):
    """
    PixelShuffle Block (Sub-pixel Convolution, ESPCN)

    Reference: Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network (ESPCN), Wenzhe Shi et al., CVPR 2016, arXiv:1609.05158
    https://arxiv.org/abs/1609.05158

    Summary: Efficient upsampling using pixel shuffle, widely used in super-resolution and generative models.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        upscale_factor (int): Upsampling factor.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H * upscale_factor, W * upscale_factor)
    """

    def __init__(self, in_channels, out_channels, upscale_factor):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels * (upscale_factor**2), 3, padding=1
        )
        self.pixel_shuffle = nn.PixelShuffle(upscale_factor)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.pixel_shuffle(x)
        x = self.relu(x)
        return x


class GANDiscriminatorBlock(nn.Module):
    """
    GAN Discriminator Block

    Reference: Generative Adversarial Nets, Ian Goodfellow et al., NeurIPS 2014, arXiv:1406.2661
    https://arxiv.org/abs/1406.2661

    Summary: Typical convolutional discriminator block, widely used in DCGAN, WGAN, and other GANs.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        kernel_size (int, optional): Convolution kernel size. Default: 4.
        stride (int, optional): Convolution stride. Default: 2.
        padding (int, optional): Convolution padding. Default: 1.
        use_bn (bool, optional): Whether to use BatchNorm. Default: True.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self, in_channels, out_channels, kernel_size=4, stride=2, padding=1, use_bn=True
    ):
        super().__init__()
        layers = [
            nn.Conv2d(
                in_channels, out_channels, kernel_size, stride, padding, bias=not use_bn
            )
        ]
        if use_bn:
            layers.append(nn.BatchNorm2d(out_channels))
        layers.append(nn.LeakyReLU(0.2, inplace=True))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class GANGeneratorBlock(nn.Module):
    """
    GAN Generator Block

    Reference: Generative Adversarial Nets, Ian Goodfellow et al., NeurIPS 2014, arXiv:1406.2661
    https://arxiv.org/abs/1406.2661

    Summary: Typical transposed convolution generator block, widely used in DCGAN, WGAN, and other GANs.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        kernel_size (int, optional): Transposed convolution kernel size. Default: 4.
        stride (int, optional): Transposed convolution stride. Default: 2.
        padding (int, optional): Transposed convolution padding. Default: 1.
        use_bn (bool, optional): Whether to use BatchNorm. Default: True.

    Input:
        x (Tensor): Shape (B, in_channels, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self, in_channels, out_channels, kernel_size=4, stride=2, padding=1, use_bn=True
    ):
        super().__init__()
        layers = [
            nn.ConvTranspose2d(
                in_channels, out_channels, kernel_size, stride, padding, bias=not use_bn
            )
        ]
        if use_bn:
            layers.append(nn.BatchNorm2d(out_channels))
        layers.append(nn.ReLU(inplace=True))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class VAEEncoderBlock(nn.Module):
    """
    VAE Encoder Block

    Reference: Auto-Encoding Variational Bayes, Diederik P. Kingma, Max Welling, ICLR 2014, arXiv:1312.6114
    https://arxiv.org/abs/1312.6114

    Summary: Neural network outputs mean and log-variance for probabilistic modeling of latent variables. Core structure of VAE.

    Args:
        in_features (int): Input feature dimension.
        hidden_dim (int): Hidden layer dimension.
        latent_dim (int): Latent variable dimension.

    Input:
        x (Tensor): Shape (B, in_features)
    Output:
        mu (Tensor): Mean of latent variable, shape (B, latent_dim)
        logvar (Tensor): Log-variance of latent variable, shape (B, latent_dim)
    """

    def __init__(self, in_features, hidden_dim, latent_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(in_features, hidden_dim), nn.ReLU(inplace=True)
        )
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)

    def forward(self, x):
        h = self.fc(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar


class VAEDecoderBlock(nn.Module):
    """
    VAE Decoder Block

    Reference: Auto-Encoding Variational Bayes, Diederik P. Kingma, Max Welling, ICLR 2014, arXiv:1312.6114
    https://arxiv.org/abs/1312.6114

    Summary: Neural network maps latent variable back to data space. Core structure of VAE.

    Args:
        latent_dim (int): Latent variable dimension.
        hidden_dim (int): Hidden layer dimension.
        out_features (int): Output feature dimension.

    Input:
        z (Tensor): Latent variable, shape (B, latent_dim)
    Output:
        x_recon (Tensor): Reconstructed data, shape (B, out_features)
    """

    def __init__(self, latent_dim, hidden_dim, out_features):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, out_features),
        )

    def forward(self, z):
        x_recon = self.fc(z)
        return x_recon


class UNet1D(nn.Module):
    """
    1D U-Net (UNet1D)

    Reference: Adapted from U-Net: Convolutional Networks for Biomedical Image Segmentation, Olaf Ronneberger et al., MICCAI 2015, arXiv:1505.04597
    https://arxiv.org/abs/1505.04597

    Summary: U-shaped encoder-decoder architecture for 1D signals, widely used in audio processing and diffusion models.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        features (list of int, optional): Number of channels at each encoder/decoder stage. Default: [64, 128, 256, 512].

    Input:
        x (Tensor): Shape (B, in_channels, L)
    Output:
        out (Tensor): Shape (B, out_channels, L)
    """

    def __init__(self, in_channels=1, out_channels=1, features=[64, 128, 256, 512]):
        super().__init__()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        # Encoder
        for feature in features:
            self.downs.append(self._block(in_channels, feature))
            in_channels = feature
        # Decoder
        for feature in reversed(features):
            self.ups.append(
                nn.ConvTranspose1d(feature * 2, feature, kernel_size=2, stride=2)
            )
            self.ups.append(self._block(feature * 2, feature))
        self.bottleneck = self._block(features[-1], features[-1] * 2)
        self.final_conv = nn.Conv1d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        skip_connections = []
        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = nn.functional.max_pool1d(x, 2)
        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]
        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip_connection = skip_connections[idx // 2]
            if x.shape[-1] != skip_connection.shape[-1]:
                x = nn.functional.interpolate(x, size=skip_connection.shape[-1])
            x = torch.cat((skip_connection, x), dim=1)
            x = self.ups[idx + 1](x)
        return self.final_conv(x)

    @staticmethod
    def _block(in_channels, out_channels):
        return nn.Sequential(
            nn.Conv1d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm1d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv1d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm1d(out_channels),
            nn.ReLU(inplace=True),
        )


class UNet3D(nn.Module):
    """
    3D U-Net (UNet3D)

    Reference: 3D U-Net: Learning Dense Volumetric Segmentation from Sparse Annotation, Özgün Çiçek et al., MICCAI 2016, arXiv:1606.06650
    https://arxiv.org/abs/1606.06650

    Summary: U-shaped encoder-decoder architecture for 3D volumetric data, widely used in medical image segmentation and diffusion models.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        features (list of int, optional): Number of channels at each encoder/decoder stage. Default: [32, 64, 128, 256].

    Input:
        x (Tensor): Shape (B, in_channels, D, H, W)
    Output:
        out (Tensor): Shape (B, out_channels, D, H, W)
    """

    def __init__(self, in_channels=1, out_channels=1, features=[32, 64, 128, 256]):
        super().__init__()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        # Encoder
        for feature in features:
            self.downs.append(self._block(in_channels, feature))
            in_channels = feature
        # Decoder
        for feature in reversed(features):
            self.ups.append(
                nn.ConvTranspose3d(feature * 2, feature, kernel_size=2, stride=2)
            )
            self.ups.append(self._block(feature * 2, feature))
        self.bottleneck = self._block(features[-1], features[-1] * 2)
        self.final_conv = nn.Conv3d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        skip_connections = []
        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = nn.functional.max_pool3d(x, 2)
        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]
        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip_connection = skip_connections[idx // 2]
            if x.shape[-3:] != skip_connection.shape[-3:]:
                x = nn.functional.interpolate(
                    x,
                    size=skip_connection.shape[-3:],
                    mode="trilinear",
                    align_corners=True,
                )
            x = torch.cat((skip_connection, x), dim=1)
            x = self.ups[idx + 1](x)
        return self.final_conv(x)

    @staticmethod
    def _block(in_channels, out_channels):
        return nn.Sequential(
            nn.Conv3d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
        )


class DiffusionBlock(nn.Module):
    """
    Diffusion Block (Denoising Diffusion Probabilistic Models)

    Reference: Denoising Diffusion Probabilistic Models, Jonathan Ho et al., NeurIPS 2020, arXiv:2006.11239
    https://arxiv.org/abs/2006.11239

    Summary: Core block for diffusion models, typically used to predict noise or denoised data at each timestep, often implemented as a residual block with time embedding.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        time_emb_dim (int): Dimension of time embedding.
        hidden_dim (int, optional): Hidden layer dimension. Default: None (uses in_channels).

    Input:
        x (Tensor): Input data, shape (B, in_channels, ...)
        t_emb (Tensor): Time embedding, shape (B, time_emb_dim)
    Output:
        out (Tensor): Output data, shape (B, out_channels, ...)
    """

    def __init__(self, in_channels, out_channels, time_emb_dim, hidden_dim=None):
        super().__init__()
        hidden_dim = hidden_dim or in_channels
        self.conv1 = nn.Conv2d(in_channels, hidden_dim, 3, padding=1)
        self.time_mlp = nn.Sequential(
            nn.Linear(time_emb_dim, hidden_dim), nn.ReLU(inplace=True)
        )
        self.conv2 = nn.Conv2d(hidden_dim, out_channels, 3, padding=1)
        self.act = nn.ReLU(inplace=True)
        self.res_conv = (
            nn.Conv2d(in_channels, out_channels, 1)
            if in_channels != out_channels
            else nn.Identity()
        )

    def forward(self, x, t_emb):
        h = self.conv1(x)
        # Add time embedding (broadcast to spatial dims)
        t = self.time_mlp(t_emb).unsqueeze(-1).unsqueeze(-1)
        h = h + t
        h = self.act(h)
        h = self.conv2(h)
        return h + self.res_conv(x)


class StyleGANBlock(nn.Module):
    """
    StyleGAN2 Block (Generator/Discriminator Block)

    Reference: Analyzing and Improving the Image Quality of StyleGAN, Tero Karras et al., CVPR 2020, arXiv:1912.04958
    https://arxiv.org/abs/1912.04958

    Summary: Core block for StyleGAN2, featuring modulated convolution, noise injection, and demodulation for high-fidelity image synthesis.

    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        style_dim (int): Dimension of style vector.
        upsample (bool, optional): If True, applies upsampling. Default: False.
        demodulate (bool, optional): If True, applies weight demodulation. Default: True.

    Input:
        x (Tensor): Input feature map, shape (B, in_channels, H, W)
        style (Tensor): Style vector, shape (B, style_dim)
        noise (Tensor, optional): Noise tensor, shape (B, 1, H, W). Default: None.
    Output:
        out (Tensor): Output feature map, shape (B, out_channels, H_out, W_out)
    """

    def __init__(
        self, in_channels, out_channels, style_dim, upsample=False, demodulate=True
    ):
        super().__init__()
        self.upsample = (
            nn.Upsample(scale_factor=2, mode="nearest") if upsample else nn.Identity()
        )
        self.conv = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.style_fc = nn.Linear(style_dim, in_channels)
        self.demodulate = demodulate
        self.bias = nn.Parameter(torch.zeros(1, out_channels, 1, 1))

    def forward(self, x, style, noise=None):
        B, C, H, W = x.shape
        x = self.upsample(x)
        style = self.style_fc(style).view(B, C, 1, 1)
        weight = self.conv.weight.unsqueeze(0)  # (1, out_c, in_c, k, k)
        weight = weight * (style + 1)
        if self.demodulate:
            d = torch.rsqrt((weight**2).sum([2, 3, 4]) + 1e-8)
            weight = weight * d.view(B, -1, 1, 1, 1)
        x = nn.functional.conv2d(
            x, weight.view(-1, C, 3, 3), bias=None, padding=1, groups=B
        )
        x = x + self.bias
        if noise is not None:
            x = x + noise
        x = nn.functional.leaky_relu(x, 0.2)
        return x
