from collections import defaultdict
import os
import e3nn_jax as e3nn
from tqdm import tqdm
import numpy as np 
import sys
sys.path.append('../')

from model.utils import up_conv_seq_len
import jax

from absl import app
import os
from absl import flags
from tensorclouds.tensorcloud import TensorCloud 
from torch.utils.data import DataLoader
from copy import deepcopy 

# from moleculib.assembly.datum import AssemblyDatum
# from moleculib.assembly.dataset import ChromaDataset
from moleculib.protein.dataset import FrameDiffDataset


from moleculib.protein.transform import (
    ProteinCrop,
    TokenizeSequenceBoundaries,
    ProteinPad,
    MaybeMirror,
    BackboneOnly,
    DescribeChemistry
)


FLAGS = flags.FLAGS
flags.DEFINE_string("model", None, "id of autoencoder model to use")
flags.mark_flag_as_required('model')

flags.DEFINE_integer("checkpoint", 5000, "Checkpoint to use for encoding proteins")

flags.DEFINE_integer("batch_size", 16, "Batch size for encoding proteins")
flags.DEFINE_integer("device", 0, "GPU device to use")
flags.DEFINE_integer("seq_len", 128, "Dataset to use for encoding")

flags.DEFINE_enum("dataset", "FrameDiff", ["FrameDiff"], "Dataset to use for encoding")


def truncate_sequence_length(cfg, candidate):
        # max_chain_len =  1457    
    sequence_length = 1
    # tree_depth = len(hparams.layers)
    spanning_lengths = []

    for _ in range(8):
        sequence_length = up_conv_seq_len(
            sequence_length, cfg.kernel_size, cfg.stride, "valid"
        )
        spanning_lengths.append(sequence_length)
    
    print("This Convolutional Configuration Spans Lengths:", spanning_lengths)
    winner = min(spanning_lengths, key=lambda x: abs(x - candidate))

    return winner

from omegaconf import OmegaConf
import pickle


def main(argv):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
    os.environ["CUDA_VISIBLE_DEVICES"] = f'{FLAGS.device}'

    os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
    os.environ["XLA_PYTHON_CLIENT_ALLOCATOR"] = "platform"

    # registry = Registry('ophiuchus')
    # platform = registry.get_platform(FLAGS.model, read_only=True)
    registry_path = os.environ['OPHIUCHUS_REGISTRY_PATH']


    cfg = OmegaConf.load(f"{registry_path}/{FLAGS.model}/config.yml")
    seq_len = truncate_sequence_length(cfg, FLAGS.seq_len)

    # cfg = platform.cfg
    transform = [
        MaybeMirror(hand='right'),
        ProteinCrop(crop_size=seq_len),
        # TokenizeSequenceBoundaries(),
        ProteinPad(pad_size=seq_len, random_position=False),
        BackboneOnly(filter=cfg.backbone_only),
        # DescribeChemistry(),
    ]

    dataset = FrameDiffDataset(
        base_path=os.path.join(cfg.data_path, "PREPROCESSED"),
        transform=transform,
    )

    params_path = os.path.join(registry_path, FLAGS.model, f'checkpoints/state_{FLAGS.checkpoint}.pyd')
    with open(params_path, 'rb') as file:
        checkpoint = pickle.load(file)
        params = checkpoint.params

    from builders.autoencoder import build_autoencoder
    model = build_autoencoder(cfg)
    
    key = jax.random.PRNGKey(0)
    
    @jax.jit
    def autoencode(batch):
        return jax.vmap(lambda x: model.apply({'params':  params}, x, rngs={'params': key}))(batch)        

    def tree_stack(trees):
        return jax.tree_util.tree_map(lambda *v: np.stack(v) if type(v[0]) != str else None, *trees)

    def tree_unstack(tree):
        leaves, treedef = jax.tree_util.tree_flatten(tree)
        return [treedef.unflatten(leaf) for leaf in zip(*leaves, strict=True)]

    loader = DataLoader(dataset.splits['train'], batch_size=FLAGS.batch_size, num_workers=0, collate_fn=tree_stack)
    batch = next(iter(loader))
    autoencode(batch) # compile the function

    encoded_dataset = []

    for batch in tqdm(loader):
        output = autoencode(batch)
        latents = jax.device_get(tree_unstack(output.encoder_internals[-1]))
        for latent in latents:
            encoded_dataset.append(latent)
                
    dataset_path = os.path.join(registry_path, FLAGS.model, f'encoded_dataset.pyd')
    with open(dataset_path, 'wb') as file:
        pickle.dump(encoded_dataset, file)


if __name__ == "__main__":
    app.run(main)