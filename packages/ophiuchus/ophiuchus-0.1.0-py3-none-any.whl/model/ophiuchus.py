from functools import partial
import jax
from typing import Optional, Tuple, Union

import flax.linen as nn
from moleculib.protein.datum import ProteinDatum

from .autoencoder import Autoencoder

# from model.generative.diffusion import TensorCloudDiffuser
from tensorclouds.data.protein import protein_to_tensor_cloud, tensor_cloud_to_protein
# from moleculib.protein.datum import ProteinDatum

from .utils import ModelOutput, inner_stack 
from moleculib.assembly.datum import AssemblyDatum

from tensorclouds.tensorcloud import TensorCloud

import e3nn_jax as e3nn
import jax.numpy as jnp


class Ophiuchus(nn.Module):

    autoencoder: Autoencoder
    # diffuser: Optional[Diffuser]

    @nn.compact
    def __call__(
        self,
        datum: Optional[Union[ProteinDatum, AssemblyDatum]] = None,
        is_training: bool = False,
        bottleneck: Optional[TensorCloud] = None,
    ):
        if hasattr(self, 'autoencoder'):
            encoding = protein_to_tensor_cloud(
                datum
            ) if datum is not None else None
            encoding_out, skips, encoder_internals, decoder_internals = self.autoencoder(input=encoding, bottleneck=None)
            proteins_out = tensor_cloud_to_protein(encoding_out, datum if datum else None)
            return ModelOutput(
                datum=proteins_out,
                encoder_internals=encoder_internals,
                decoder_internals=decoder_internals,
                atom_perm_loss=0.0,
                diff_loss=[],
            )
        elif hasattr(self, 'diffuser'):
            return self.diffuser(datum, is_training=is_training)
        else:
            raise ValueError("Neither autoencoder nor diffuser available for inference")
        
    
    def sample(self, conditioners=[]):
        if self.diffuser is None:
            raise ValueError("Diffuser not available for sampling")        

        latent, _ = self.diffuser.sample(conditioners)
        latent = TensorCloud.stack(latent.split(piece_sizes=[len(latent)]))
        if not hasattr(self, 'autoencoder'):
            return AssemblyDatum(protein_data=jax.vmap(tensor_cloud_to_protein)(latent, None))

        return self(bottleneck=latent, is_training=False).datum
