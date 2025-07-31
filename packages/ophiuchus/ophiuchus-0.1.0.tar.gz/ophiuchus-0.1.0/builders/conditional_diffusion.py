import os
from model.graphics import PlotSamples
from model.base.utils import TensorCloud, dotdict
from hydra_zen import builds, make_config
import sys

from model.ophiuchus import Ophiuchus
from moleculib.assembly.dataset import ChromaDataset
from moleculib.abstract.metrics import MetricsPipe
from moleculib.protein.transform import BackboneOnly
from moleculib.assembly.metrics import ApplyMetricsToProtein
from moleculib.protein.metrics import (
    StandardBondDeviation, CountClashes, AlignedRootMeanSquareDeviation, StandardAngleDeviation, StandardDihedralDeviation
)
from model.base.protein import protein_to_tensor_cloud, tensor_cloud_to_protein

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from model.base.denoiser import BasicNet
from model.diffusion.tensorcloud_diffusion import TensorCloudDiffuser
from tensorclouds.tensorclouds.loss.losses import LossPipe, LatentDiffusionLoss

from kheiron.pipeline import Registry, Trainer
from kheiron.plot.plot_pipe import PlotPipe
import e3nn_jax as e3nn

from moleculib.protein.transform import (
    ProteinCrop, ProteinPad
)

from moleculib.assembly.transform import (
    FilterProteinChains, ApplyToProteins, ComplexPad
)

from moleculib.assembly.datum import AssemblyDatum


DEFAULTS = dotdict(
    # =======================================================
    # ================ ⚕ Ophiuchus Config ⚕ =================
    # =======================================================
    seed=42,

    # ======== Env
    preallocate=True,
    device=0,
    debug_nans=False,
    disable_jit=False,

    # ======== Data
    batch_size=30,
    num_workers=30,
    sequence_length=64,
    # max_sequence_length=64,
    num_chains=1,

    # ======== Architecture
    coord_net_irreps='128x0e+128x1e',
    coord_net_layers=4,

    feature_net_irreps='64x0e+64x1e',
    feature_net_layers=4,

    # ======== Diffusion
    timesteps = 50,
    r3_rescale = 8.0,
    diffusion_start=0.05, # where 1.0 is full noising

    # ======== Training
    learning_rate=1e-2,
    num_epochs=10000,
    save_every=3000,
    sample_every=2000,
    validate_every=10,
    
    single_datum=False,
    single_batch=True,

    train_only=True,
)



import haiku as hk
import jax.numpy as jnp


class SequenceConditionedProteinDiffuser(hk.Module):

    def __init__(self, **kwargs):
        super().__init__()
        self.sequence_emb = hk.Embed(vocab_size=23, embed_dim=64)
        self.diffuser = TensorCloudDiffuser(irreps='14x1e', **kwargs)

    def sample(self, datum: AssemblyDatum):
        sequence = jnp.concatenate([datum.protein_data[i].residue_token for i in range(len(datum.protein_data))], axis=0)
        sequence_emb = self.sequence_emb(sequence)

        tensorclouds = [protein_to_tensor_cloud(datum.protein_data[i]) for i in range(len(datum.protein_data))]
        tensorclouds = TensorCloud.concatenate(tensorclouds)
        tensorclouds_vectors = tensorclouds.replace(
            irreps_array=tensorclouds.irreps_array.filter('1e')
        )

        out_tensorcloud, _ = self.diffuser.sample(cond=sequence_emb, x0=tensorclouds_vectors)
        out_tensorclouds = out_tensorcloud.split([len(datum.protein_data[i].residue_token) for i in range(len(datum.protein_data))])
        out_proteins = [tensor_cloud_to_protein(out_tensorclouds[i], datum.protein_data[i]) for i in range(len(datum.protein_data))]
        assembly = AssemblyDatum(protein_data=out_proteins)
        return assembly

    def __call__(self, datum: AssemblyDatum, is_training=False):
        tensorclouds = [protein_to_tensor_cloud(datum.protein_data[i]) for i in range(len(datum.protein_data))]
        tensorclouds = TensorCloud.concatenate(tensorclouds)
        tensorclouds_vectors = tensorclouds.replace(
            irreps_array=tensorclouds.irreps_array.filter('1e')
        )
        sequence = jnp.concatenate([datum.protein_data[i].residue_token for i in range(len(datum.protein_data))], axis=0)
        tensorclouds_scalars = self.sequence_emb(sequence)
        return self.diffuser(x0=tensorclouds_vectors, cond=tensorclouds_scalars)


from typing import Any


class FilterStringsOut():

    def transform(self, datum: Any):
        attrs = vars(datum)
        for key in list(attrs.keys()):
            if isinstance(attrs[key], str):
                attrs[key] = None
        return type(datum)(**attrs)



def build_pipeline(
    hparams=dotdict(DEFAULTS),
):
    EnvCfg = make_config(
        device=hparams.device,
        preallocate=hparams.preallocate,
        debug_nans=hparams.debug_nans,
        disable_jit=hparams.disable_jit,
        data_path=os.environ.get("OPHIUCHUS_DATA_PATH"),
    )
    
    PROTEIN_IRREPS='14x1e'

    coord_net_irreps = e3nn.Irreps(hparams.coord_net_irreps)
    layers = [str(coord_net_irreps)] * (hparams.coord_net_layers - 1) + [PROTEIN_IRREPS] 
    CoordNetCfg = builds(
        BasicNet,
        layers=layers,
        zen_partial=True,
    )

    feature_net_irreps = e3nn.Irreps(hparams.feature_net_irreps)
    layers = [str(feature_net_irreps)] * (hparams.feature_net_layers - 1) + [PROTEIN_IRREPS] 
    FeatureNetCfg = builds(
        BasicNet,
        layers=layers,
        zen_partial=True,
    )

    DiffusionCfg = builds(
        SequenceConditionedProteinDiffuser,
        feature_net=FeatureNetCfg,
        coord_net=CoordNetCfg,
        timesteps=hparams.timesteps,
        leading_shape = (hparams.num_chains * hparams.sequence_length, ),
        rescale=hparams.r3_rescale,
        start_at=hparams.diffusion_start,
        zen_partial=True,
    )

    protein_transform = [
        builds(ProteinCrop, crop_size=hparams.sequence_length),
        builds(ProteinPad, pad_size=hparams.sequence_length, random_position=False),
        builds(BackboneOnly, filter=False),
        builds(FilterStringsOut)
    ]

    transform = [ 
        builds(FilterProteinChains, num_chains=hparams.num_chains), 
        builds(ComplexPad, num_chains=hparams.num_chains),
        builds(ApplyToProteins, protein_transform=protein_transform),
    ]
    
    DatasetCfg = builds(
        ChromaDataset,
        base_path=os.path.join(EnvCfg.data_path, "PREPROCESSED"),
        transform=transform,
        reduced=hparams.single_datum or hparams.single_batch
    )

    loss_list = [
        builds(
            LatentDiffusionLoss,
            weight=1.0
        )
    ]

    LossCfg = builds(LossPipe, loss_list=loss_list)

    SamplerCfg = DiffusionCfg

    plot_pipe = builds(
        PlotPipe,
        plot_list=[ builds(PlotSamples)  ],
    )

    sample_metrics = builds(
        MetricsPipe,
        metrics_list=[ 
            # builds(ApplyMetricsToProtein,
                # [
                    # builds(AlignedRootMeanSquareDeviation)
                # ]
            # ),
        ],
    )

    TrainerCfg = builds(
        Trainer,
        learning_rate=hparams.learning_rate,
        model=DiffusionCfg, 
        dataset=DatasetCfg,
        batch_size=hparams.batch_size,
        num_workers=hparams.num_workers,
        losses=LossCfg,
        seed=hparams.seed,
        num_epochs=hparams.num_epochs,
        save_every=hparams.save_every,
        validate_every=hparams.validate_every,
        sample_batch_size=None,
        sample_metrics=sample_metrics,
        zen_partial=True,
        sample_model=SamplerCfg,
        sample_every=hparams.sample_every,
        sample_plot=plot_pipe,
        single_batch=hparams.single_batch,
        single_datum=hparams.single_datum,
        train_only=hparams.train_only
    )

    TrainCfg = make_config(
        trainer=TrainerCfg,
        env=EnvCfg,
    )
    return TrainCfg
