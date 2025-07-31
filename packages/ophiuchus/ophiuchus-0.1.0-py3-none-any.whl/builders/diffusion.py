import os
from model.graphics import PlotSamples
from model.base.utils import EmbeddingsDataset, TensorCloud, multiscale_irreps, dotdict
from hydra_zen import builds, make_config
import sys
import jax

from model.ophiuchus import Ophiuchus
from moleculib.assembly.dataset import ChromaDataset
from moleculib.abstract.metrics import MetricsPipe
from moleculib.assembly.metrics import ApplyMetricsToProtein
from moleculib.protein.metrics import StandardBondDeviation, CountClashes
from moleculib.protein.metrics import StandardAngleDeviation, StandardDihedralDeviation
from moleculib.protein.datum import ProteinDatum
from model.base.protein import protein_to_tensor_cloud

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from model.base.denoiser import BasicNet
from model.base.diffusion import TensorCloudDiffuser
from model.base.autoencoder import Autoencoder
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
    batch_size=20,
    num_workers=20,
    sequence_length=64,
    # max_sequence_length=64,
    num_chains=1,

    # ======== Architecture
    coord_net_irreps='64x0e+64x1e',
    coord_net_layers=6,

    feature_net_irreps='64x0e+64x1e',
    feature_net_layers=4,

    # ======== Diffusion
    timesteps = 200,
    r3_rescale = 7.0,

    # ======== Training
    learning_rate=7e-3,
    num_epochs=10000,
    save_every=3000,
    sample_every=2000,
    evaluate_every=10,
    single_datum=False,
    single_batch=False,
    train_only=True,
)


class ToExtendedTensorCloud():
    def transform(self, datum: AssemblyDatum):
        with jax.default_device(jax.devices("cpu")[0]):
            datum = TensorCloud.concatenate(datum.protein_data)
        return datum


class ToTensorCloud():
    def transform(self, datum: ProteinDatum):
        with jax.default_device(jax.devices("cpu")[0]):
            datum = protein_to_tensor_cloud(datum)
        return datum
    

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

    PROTEIN_IRREPS = '23x0e + 14x1e'

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
        TensorCloudDiffuser,
        feature_net=FeatureNetCfg,
        coord_net=CoordNetCfg,
        irreps=PROTEIN_IRREPS,
        timesteps=hparams.timesteps,
        leading_shape = (hparams.num_chains * hparams.sequence_length, ),
        rescale=hparams.r3_rescale,
        zen_partial=True,
    )

    OphiuchusCfg = builds(
        Ophiuchus,
        diffuser=DiffusionCfg,
        autoencoder=None,
        zen_partial=True,
    )

    protein_transform = [
        builds(ProteinCrop, crop_size=hparams.sequence_length),
        builds(ProteinPad, pad_size=hparams.sequence_length, random_position=False),
        builds(ToTensorCloud),
    ]

    transform = [ 
        builds(FilterProteinChains, num_chains=hparams.num_chains), 
        builds(ComplexPad, num_chains=hparams.num_chains),
        builds(ApplyToProteins, protein_transform=protein_transform),
        builds(ToExtendedTensorCloud)
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

    SamplerCfg = builds(
        Ophiuchus, 
        autoencoder=None,
        diffuser=DiffusionCfg,
        zen_partial=True
    )

    plot_pipe = builds(
        PlotPipe,
        plot_list=[ builds(PlotSamples)  ],
    )

    sample_metrics = builds(
        MetricsPipe,
        metrics_list=[ 
            builds(ApplyMetricsToProtein,
                [
                    builds(StandardBondDeviation),
                    builds(StandardAngleDeviation),
                    builds(StandardDihedralDeviation),
                    builds(CountClashes),
                ]
            ),
        ],
    )

    TrainerCfg = builds(
        Trainer,
        learning_rate=hparams.learning_rate,
        model=OphiuchusCfg, 
        dataset=DatasetCfg,
        batch_size=hparams.batch_size,
        num_workers=hparams.num_workers,
        losses=LossCfg,
        seed=hparams.seed,
        num_epochs=hparams.num_epochs,
        save_every=hparams.save_every,
        evaluate_every=hparams.evaluate_every,
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
