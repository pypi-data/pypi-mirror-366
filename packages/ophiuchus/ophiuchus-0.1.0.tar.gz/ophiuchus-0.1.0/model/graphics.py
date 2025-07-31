import os
from model.base.utils import ModelOutput, TensorCloud, inner_split
from moleculib.protein.datum import ProteinDatum
from moleculib.graphics.py3Dmol import plot_py3dmol_grid

from tempfile import gettempdir
from model.base.protein import tensor_cloud_to_protein
import wandb 
import time

from moleculib.assembly.transform import UnstackProteins

class PlotReconstruction:

    def __init__(
            self, 
            num_samples=7, 
            window_size=(250, 250), 
            sphere=False,
            ribbon=False,
        ):
        self.num_samples = num_samples
        self.window_size = window_size
        self.sphere = sphere
        self.ribbon = ribbon
        self.unstack = UnstackProteins()

    def __call__(self, run, outputs, batch, _):
        pairs = []
        
        num_samples = min(self.num_samples, len(outputs))
        list_ = enumerate(list(zip(outputs, batch))[:num_samples])
        for _, (output, ground) in list_:
            output_data = self.unstack.transform(output.datum)
            ground_data = self.unstack.transform(ground)
            pairs.append([output_data, ground_data])

        # transpose pairs grid 
        pairs = list(zip(*pairs))
        v = plot_py3dmol_grid(pairs, window_size=self.window_size)
        html = v._make_html()

        html_path = os.path.join(gettempdir(), f'{run.name}.html')
        with open(html_path, 'w') as f: f.write(html)
        run.log({'reconstruction': wandb.Html(open(html_path))})

        time.sleep(1)
        os.remove(html_path)


class PlotSamples:

    def __init__(self, num_samples=7, window_size=(250, 250)):
        self.num_samples = num_samples
        self.window_size = window_size

    def __call__(self, run, outputs, _, __):
        # transform 9 outputs in 3x3 grid:
        outputs = [outputs[i:i+3] for i in range(0, len(outputs), 3)]
        v = plot_py3dmol_grid(outputs, window_size=self.window_size)
        html = v._make_html()

        html_path = os.path.join(gettempdir(), f'{run.name}.html')
        with open(html_path, 'w') as f: f.write(html)
        run.log({'samples': wandb.Html(open(html_path))})

        time.sleep(1)
        os.remove(html_path)
