import sys

sys.path.append("../")


from absl import app
from omegaconf import OmegaConf

import numpy as np

import wandb
import os

import wandb

from absl.flags import FLAGS
from absl import flags

flags.DEFINE_string("restore", None, "wandb hash to restore")
flags.DEFINE_string("iter", None, "#iteration in restarting cycles")
flags.DEFINE_string("device", None, "CUDA device to run on")

from learnax.registry import Registry

import pprint


def main(argv):
    print(
        """\n
    _________                 ________
    ___  __ \_______________________  /___  ________ ___________
    __  / / /  _ \  _ \__  __ \__  / /_  / / /_  __ `__ \__  __
    _  /_/ //  __/  __/_  /_/ / /_/ / / /_/ /_  / / / / /_  /_/ /
    /_____/ \___/\___/_  .___/\____/  \__,_/ /_/ /_/ /_/_  .___/
                       /_/                               /_/
    \n"""
    )

    project = "deepjump"
    entity = "molecular-machines"
    restore = FLAGS.restore

    if restore != None:
        config_path = (
            f'{os.environ.get("TRAINAX_REGISTRY_PATH")}/{project}/{restore}/config.yml'
        )
        assert os.path.exists(config_path), f"Config file not found at {config_path}"
        cfg = OmegaConf.load(config_path)
    else:
        cfg = OmegaConf.load(f"./train_config.yml")
    pprint.pp(OmegaConf.to_container(cfg))

    if restore != None:
        run = Registry(project).restore_run(restore)
    else:
        run = Registry(project).new_run(cfg)

    device = FLAGS.device
    os.environ["CUDA_VISIBLE_DEVICES"] = str(device)
    os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "true"
    os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = ".99"


    from builders import build_pipeline
    trainer = build_pipeline(cfg, run=run, restore=restore)

    import jax
    jax.config.update("jax_debug_nans", False)
    trainer.train()


if __name__ == "__main__":
    app.run(main)
