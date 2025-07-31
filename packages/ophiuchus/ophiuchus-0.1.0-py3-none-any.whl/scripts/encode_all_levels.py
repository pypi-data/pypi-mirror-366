from collections import defaultdict
from functools import reduce
import os
from tqdm import tqdm
import numpy as np 
import sys

from moleculib.graphics.py3Dmol import plot_py3dmol_grid
from moleculib.protein.datum import ProteinDatum

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import jax
import haiku as hk
from model.base.utils import down_conv_seq_len

from kheiron.pipeline.registry import Registry

from absl import app
import os
from absl import flags

from moleculib.assembly.dataset import ChromaDataset

from moleculib.protein.transform import (
    ProteinCrop,
    TokenizeSequenceBoundaries,
    ProteinPad,
    MaybeMirror,
    BackboneOnly,
    DescribeChemistry
)

from sklearn.manifold import TSNE


FLAGS = flags.FLAGS
flags.DEFINE_string("model", None, "Name of autoencoder model to use")
flags.mark_flag_as_required('model')

flags.DEFINE_string("path", None, "Path to save embeddings")
flags.DEFINE_bool("snapshot", True, "Whether to html embed snapshots of the protein fragments")

flags.DEFINE_integer("device", 0, "GPU device to use")
flags.DEFINE_enum("dataset", "Chroma", ["Chroma"], "Dataset to use for encoding")


def main(argv):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID" 
    os.environ["CUDA_VISIBLE_DEVICES"] = f'{FLAGS.device}'

    os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
    os.environ["XLA_PYTHON_CLIENT_ALLOCATOR"] = "platform"

    path = FLAGS.path
    if path is None:
        path = f'{FLAGS.model}-embeddings'

    if not os.path.exists(path):
        os.makedirs(path)

    registry = Registry('ophiuchus')
    platform = registry.get_platform(FLAGS.model, read_only=True)
    cfg = platform.cfg

    stride = cfg['trainer']['model']['autoencoder']['stride']
    kernel_size = cfg['trainer']['model']['autoencoder']['kernel_size']
    depth = len(cfg['trainer']['model']['autoencoder']['layers'])
    max_chain_len =  485

    from model.base.sequence_convolution import moving_window

    chain_len = max_chain_len

    # we initialize the slices as [i:i+1] for each i in the chain    
    slices = np.stack([np.arange(0, chain_len), np.arange(1, chain_len + 1)],axis=-1)
    
    slices_per_level = {0: slices}
    # we then reduce as we would in convolutions, but we keep track of the sizes instead
    for i in range(depth - 1):
        windows = moving_window(np.arange(slices.shape[0]), kernel_size, stride)
        slices_ = slices[windows]
        slices = np.stack([slices_[:, :, 0].min(axis=-1), slices_[:, :, 1].max(axis=-1)],axis=-1)
        slices_per_level[i + 1] = slices

    protein_transform = [
        ProteinCrop(crop_size=max_chain_len),
        TokenizeSequenceBoundaries(),
        MaybeMirror(hand='left'),
        ProteinPad(pad_size=max_chain_len, random_position=False),
        BackboneOnly(filter=True),
        DescribeChemistry(),
    ]

    transform = lambda datum: reduce(lambda x, f: f.transform(x), protein_transform, datum)

    dataset = ChromaDataset(
        base_path=cfg['trainer']['dataset']['base_path'],
        reduced=True
    )

    rng_seq = hk.PRNGSequence(42)
    premodel = platform.instantiate_model()
    forward_ = hk.transform(lambda *a, **ka: premodel()(*a, **ka))

    @jax.jit
    def _autoencoder(params, rng, datum):
        return forward_.apply(params, rng, datum)

    base_params = platform.get_params(-1)
    def autoencoder(batch):
        return _autoencoder(base_params, next(rng_seq), batch)

    START_LEVEL = 3

    encoded_dataset = defaultdict(dict)
    sliced_dataset = defaultdict(lambda: defaultdict(list))

    for key, split in dataset.splits.items():
        pbar = tqdm(split)
        pbar.set_description(f'Encoding {key}')

        for idx, assembly in enumerate(pbar):
            
            for protein_index in range(len(assembly.protein_data)):
                # seq_len = datum.protein_data[0].residue_token.shape[0] 
    
                datum = assembly.protein_data[protein_index]
                
                datum_input = transform(datum)
                datum_input.idcode = None
                output = autoencoder(datum_input)

                for level in range(START_LEVEL, len(output.encoder_internals)):
                    tc = output.encoder_internals[level]
                    mask = tc.mask_coord[0]
                    tc = np.array(tc.irreps_array.filter('0e').array)[0][mask]
                    encoded_dataset[datum.idcode][level] = tc

                    slices = slices_per_level[level]
                    for i, (start, end) in enumerate(slices):
                        if start <= len(datum):
                            sliced_dataset[datum.idcode][level].append(datum[start:end])
            if idx > 5:
                break

    import time
    print('plotting proteins into html')
    for key, protein in tqdm(list(sliced_dataset.items())):
        for level, slices in list(protein.items()):
            for i, slice_ in enumerate(slices):
                path = f'{FLAGS.model}-embeddings/images/{key}/{level}'
                
                v = plot_py3dmol_grid([[slice_]], window_size=(300, 300))
                html = v._make_html()

                if not os.path.exists(path):
                    os.makedirs(path)
                html_path = os.path.join(path, f'{i}.html')
                with open(html_path, 'w') as f: f.write(html)
                time.sleep(0.1)

    encoded_dataset_tsne = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    for level in range(START_LEVEL, len(output.encoder_internals)):
        level_data = []
        for key, value in list(encoded_dataset.items()):
            level_data.append(value[level])
        level_data = np.concatenate(level_data)
        
        
        # TODO(): Add a flag to choose between PCA and TSNE
        # TODO(): tsne doesnt scale, need to fit to a smaller subset of the data
        # and then the full data must be transformed with the fitted tsne
        print(f'computing position tsne for level {level}: {level_data.shape}')
        position = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=3).fit_transform(level_data)
        print(f'computing color tsne for level {level}: {level_data.shape}')
        colors = TSNE(n_components=3, learning_rate='auto', init='random', perplexity=3).fit_transform(level_data)
        
        colors = (colors - colors.min())
        colors = (colors * 255 / colors.max()).astype(np.int32)
        colors = [f'rgb({r}, {g}, {b})' for r, g, b in colors]

        cumsum = 0        
        for _, key in enumerate(list(encoded_dataset.keys())):
            len_ = len(encoded_dataset[key][level])
            encoded_dataset_tsne[key][level]['pos'] = position[cumsum:cumsum+len_].tolist()
            encoded_dataset_tsne[key][level]['colors'] = colors[cumsum:cumsum+len_]
            cumsum += len_

    import pickle
    with open(f'{path}/encoded_dataset.pkl', 'wb') as f:
        pickle.dump(encoded_dataset, f)

    import json
    with open(f'{path}/encoded_dataset_tsne.json', 'w') as f:
        json.dump(encoded_dataset_tsne, f)
    


if __name__ == "__main__":
    app.run(main)