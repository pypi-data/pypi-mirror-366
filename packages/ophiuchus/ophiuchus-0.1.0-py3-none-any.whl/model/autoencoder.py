from typing import List
from flax import linen as nn

from .decoder import Decoder
from .encoder import Encoder

from tensorclouds.tensorcloud import TensorCloud
import e3nn_jax as e3nn


class Autoencoder(nn.Module):

    irreps: e3nn.Irreps
    layers: List[int]
    rescale: float
    stride: int
    kernel_size: int

    def setup(
        self,
    ):
        self.encoder = Encoder(
            self.irreps,
            self.layers,
            self.rescale,
            self.stride,
            self.kernel_size,
        )
        self.decoder = Decoder(
            self.irreps,
            self.layers,
            self.rescale,
            self.stride,
            self.kernel_size,
            skip_connections=False
        )

    @nn.compact
    def __call__(
        self,
        input: TensorCloud = None,
        bottleneck: TensorCloud = None,
    ):
        if input is not None:
            encoder_internals = self.encoder(input)
            skip = encoder_internals[-1]
        else:
            skip = bottleneck
            encoder_internals = None
        tc, decoder_internals = self.decoder(
            skips=skip,
            is_training=True,
        )
        return tc, encoder_internals, encoder_internals, decoder_internals
