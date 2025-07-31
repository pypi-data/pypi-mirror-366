import e3nn_jax as e3nn
from flax import linen as nn
import jax

from tensorclouds.nn.layer_norm import EquivariantLayerNorm
from tensorclouds.nn.residual import Residual
from tensorclouds.nn.self_interaction import SelfInteraction
from .sequence_convolution import SequenceConvolution
from tensorclouds.tensorcloud import TensorCloud


class MixingBlock(nn.Module):
    
    irreps_out: e3nn.Irreps
    kernel_size: int = 3
    residual: bool = True
    weighted_coords: bool = False

    @nn.compact
    def __call__(
        self,
        state: TensorCloud,
    ):
        residual = state
        state = SelfInteraction(
            [self.irreps_out],
            norm_last=True,
            residual=False,
        )(state)
        state = SequenceConvolution(
            self.irreps_out,
            stride=1,
            kernel_size=3,
            mode="same",
            norm=False,
            weighted=self.weighted_coords,
        )(state)
        state = state.replace(
            irreps_array=EquivariantLayerNorm()(state.irreps_array + residual.irreps_array)
        )

        return state
