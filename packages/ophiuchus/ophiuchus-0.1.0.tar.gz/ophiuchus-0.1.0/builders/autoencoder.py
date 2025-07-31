import os
from model.utils import up_conv_seq_len
# from model.graphics import PlotReconstruction

import sys
sys.path.append('..')

from model.autoencoder import Autoencoder
from model.ophiuchus import Ophiuchus

import numpy as np
import e3nn_jax as e3nn

from moleculib.protein.dataset import FrameDiffDataset
from tensorclouds.loss.losses import (
    LossPipe,
    VectorMapLoss,
    CrossEntropyLoss,
    BondLoss,
    AngleLoss,
    DihedralLoss,
    ClashLoss,
    AtomPermLoss,
    ApplyLossToProteins,
    BottleneckRegularization
)

from tensorclouds.train.trainer import Trainer

from moleculib.protein.transform import (
    ProteinCrop,
    TokenizeSequenceBoundaries,
    ProteinPad,
    MaybeMirror,
    BackboneOnly,
    DescribeChemistry,
)


def build_autoencoder(config):
    ae = Autoencoder(
        layers=config.layers,
        irreps=e3nn.Irreps(config.irreps),
        rescale=config.rescale,
        stride=config.stride,
        kernel_size=config.kernel_size,
    )
    return Ophiuchus(autoencoder=ae)

def build_pipeline(
    config,
    run=None,
):


    loss_list = LossPipe([
        VectorMapLoss(
            weight=5.0,
            start_step=0,
            max_radius=32.0,
            max_error=0.0,
            norm_only=False,
        ),
        BondLoss(weight=0.1, start_step=0),
        AngleLoss(weight=0.1, start_step=0),
        DihedralLoss(weight=0.1, start_step=0),
        ClashLoss(weight=10.0, start_step=0),
        CrossEntropyLoss(weight=1.0, start_step=0),
    ])
    sequence_length = 1
    spanning_lengths = [sequence_length]
    tree_depth = len(config.layers)
    for _ in range(max(10, tree_depth - 1)):
        sequence_length = up_conv_seq_len(
            sequence_length, config.kernel_size, config.stride, "valid"
        )
        spanning_lengths.append(sequence_length)
    print("This Convolutional Configuration Spans Lengths:", spanning_lengths)


    if config.sequence_length is None:
        sequence_length = spanning_lengths[tree_depth - 1]
    else:
        proposal_sequence_length = config.sequence_length
        closest = np.argmin(
            np.abs(np.array(spanning_lengths) - proposal_sequence_length)
        )
        sequence_length = spanning_lengths[closest]

    print(f"Compressing Sequence Fragments of {sequence_length}")

    sequence_length = config.sequence_length
    transform = [
        MaybeMirror(hand='right'),
        ProteinCrop(crop_size=sequence_length),
        # TokenizeSequenceBoundaries(),
        ProteinPad(pad_size=sequence_length, random_position=False),
        BackboneOnly(filter=config.backbone_only),
        DescribeChemistry(),
    ]

    ds = FrameDiffDataset(
        base_path=os.path.join(config.data_path, "PREPROCESSED"),
        transform=transform,
    )

    model = build_autoencoder(config)

    trainer = Trainer(
        run=run,
        seed=config.seed,

        learning_rate=config.learning_rate,

        model=model,
        train_dataset=ds.splits['train'],
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        losses=loss_list,

        num_epochs=config.num_epochs,
        save_every=config.save_every,

        single_datum=config.single_datum,
        single_batch=config.single_batch,
        train_only=config.train_only,
    )

    return trainer
