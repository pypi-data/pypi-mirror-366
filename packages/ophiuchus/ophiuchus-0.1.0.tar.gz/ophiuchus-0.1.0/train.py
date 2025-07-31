import sys

sys.path.append('../')
import random


from absl import app, flags

from omegaconf import OmegaConf

import os
import wandb
import pickle
import numpy as np

import shutil 

FLAGS = flags.FLAGS

flags.DEFINE_string('config', None, "Config file to use")
flags.DEFINE_string('restart', None, 'Flag to indicate restart from a specific checkpoint')
flags.DEFINE_string('tag', 'default', 'Tag for experiment')

def main(argv):
    print("\n «««««««««««««««««««« ⚕ Starting Ophiuchus Training ⚕ »»»»»»»»»»»»»»»»»»»» \n ")

    registry_path = os.environ['OPHIUCHUS_REGISTRY_PATH']
    if not registry_path:
        raise RuntimeError('Please set OPHIUCHUS_REGISTRY_PATH environment variable: run export OPHIUCHUS_REGISTRY_PATH=/yourpath/ophiuchus/')
    
    if not os.path.exists(registry_path):
        os.makedirs(registry_path, exist_ok=True)

    # set cuda_visible_devices
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = '3'

    if FLAGS.restart != None: 
        
        id = FLAGS.restart
        run = wandb.init(
            project="ophiuchus",
            id=id,
            entity='molecular-machines',
            resume='must',
        )

        run_path = registry_path + '/' + id
        cfg = OmegaConf.load(f"{run_path}/config.yml")

    else:
        if FLAGS.config == 'autoencoder': 
            from builders.autoencoder import build_pipeline
            cfg = OmegaConf.load(f'./configs/autoencoder.yml')
        elif FLAGS.config == 'latent_diffusion':
            from builders.latent_diffusion import build_pipeline
            cfg = OmegaConf.load(f'./configs/latent_diffusion.yml')

        run = wandb.init(
            project="ophiuchus",
            dir=os.path.expanduser(registry_path),
            config=OmegaConf.to_container(cfg),
            tags=[FLAGS.tag],
            entity='molecular-machines'
        )

        with open(f"{run.dir}/conf.yml", "w") as f:
            OmegaConf.save(OmegaConf.to_container(cfg), f)

        id = run.id
        run_path = registry_path + '/' + id
        os.makedirs(run_path)

        with open(f"{run_path}/config.yml", "w") as f:
            OmegaConf.save(OmegaConf.to_container(cfg), f)

        def ignore_files(dir, files):
            print(f"Copying {dir}")
            ignore_list = [
                file
                for file in files
                if (
                    file.startswith(".")
                    or file in ("__pycache__",)
                    or file.startswith('wandb')
                    or file.startswith('.')
                    or file.startswith('notebooks')
                )
            ]
            return ignore_list

        # print('copying repo')
        # code_path = run_path + '/code/'
        # shutil.copytree(
        #     os.getcwd(),
        #     str(code_path),
        #     ignore=ignore_files,
        # )
    
    print('...Building Pipeline')
    trainer = build_pipeline(cfg, run)
    
    print('...Training')
    trainer.train()


if __name__ == "__main__":
    app.run(main)
    
