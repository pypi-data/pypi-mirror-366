import os
from model.utils import up_conv_seq_len

import sys
sys.path.append('..')

from tensorclouds.nn.denoiser import TwoTrackDenoiser

from model.autoencoder import Autoencoder
from model.ophiuchus import Ophiuchus

import numpy as np
import e3nn_jax as e3nn

from tensorclouds.loss.losses import (
    LossPipe,
    TensorCloudMatchingLoss
)

from tensorclouds.transport.diffusion import TensorCloudDiffuser
from tensorclouds.nn.denoiser import Denoiser
from tensorclouds.train.trainer import Trainer

from moleculib.protein.transform import (
    ProteinCrop,
    ProteinPad,
)

import pickle

from moleculib.abstract.dataset import PreProcessedDataset

def build_dataset(config):
    autoencoder_model = config.base_autoencoder
    registry_path = os.environ.get("OPHIUCHUS_REGISTRY_PATH")
    data_path = os.path.join(registry_path, autoencoder_model, "encoded_dataset.pyd")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Could not find encoded dataset at {data_path}")
    print('Loading dataset from:', data_path)
    with open(data_path, "rb") as file:
        dataset = {'train': pickle.load(file)}

    transform = [
        ProteinCrop(crop_size=config.sequence_length),
        ProteinPad(pad_size=config.sequence_length, random_position=False),
    ]

    return PreProcessedDataset(splits=dataset, transform=transform)


def build_diffuser(config, dataset=None):
    if dataset == None:
        dataset = build_dataset(config)
    sample = dataset.splits['train'][0]
    data_irreps = sample.irreps
    layers = [config.dim * e3nn.Irreps(config.irreps) for l in range(config.depth)] + [ data_irreps ]
    network = TwoTrackDenoiser(
        feature_net = Denoiser(
            layers = layers,
            k = config.k,
            k_seq = config.k_seq,
            radial_cut = config.radial_cut,
            timesteps = config.timesteps,
            time_range = (0.0, config.timesteps),
            full_square = False,
            pos_encoding = False,
        ),
        coord_net = Denoiser(
            layers = layers,
            k = config.k,
            k_seq = config.k_seq,
            radial_cut = config.radial_cut,
            timesteps = config.timesteps,
            time_range = (0.0, config.timesteps),
            full_square = False,
            pos_encoding = False,        
        )
    )

    diffuser = TensorCloudDiffuser(
        network=network,
        irreps=data_irreps,
        var_features=config.var_features,
        var_coords=config.var_coords,
        timesteps=config.timesteps,
        leading_shape=(config.sequence_length,)
    )

    return diffuser


def truncate_sequence_length(config):        
    sequence_length = 1
    spanning_lengths = [sequence_length]
    print("Config Layers:", config.layers)
    tree_depth = len(config.layers)
    for _ in range(max(10, tree_depth - 1)):
        sequence_length = up_conv_seq_len(
            sequence_length, config.kernel_size, config.stride, "valid"
        )
        spanning_lengths.append(sequence_length)
    print("This Convolutional Configuration Spans Lengths:", spanning_lengths)
    proposal_sequence_length = config.sequence_length
    closest = np.argmin(
        np.abs(np.array(spanning_lengths) - proposal_sequence_length)
    )
    sequence_length = spanning_lengths[closest]
    return sequence_length

from omegaconf import OmegaConf

def build_pipeline(
    config,
    run=None,
):
    loss_list = LossPipe([
        TensorCloudMatchingLoss(),
    ])

    registry_path = os.environ.get("OPHIUCHUS_REGISTRY_PATH")
    ae_config = os.path.join(registry_path, config.base_autoencoder, "config.yml")
    autoencoder_config = OmegaConf.load(ae_config)
    sequence_length = truncate_sequence_length(autoencoder_config)
    config.sequence_length = sequence_length
    
    dataset = build_dataset(config)
    model = build_diffuser(config, dataset)
 
    trainer = Trainer(
        learning_rate=config.learning_rate,

        model=model,
        dataset=dataset,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        losses=loss_list,
        
        seed=config.seed,

        num_epochs=config.num_epochs,
        save_every=config.save_every,

        # evaluate_every=config.evaluate_every,
        validate_every=10000,

        single_datum=config.single_datum,
        single_batch=config.single_batch,
        train_only=config.train_only,

        # plot_pipe=plot_pipe,
        plot_every=2000,
        run=run,
    )

    return trainer
