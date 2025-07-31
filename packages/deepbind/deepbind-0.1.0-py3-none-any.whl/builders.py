import jax
from data.md_cath import mdCATHDataset
import os

from moleculib.loss.chemistry import ClashLoss
from nn.deepjump import DeepJump
import optax
import wandb

from learnax.trainer import Trainer


from learnax.loss import LossFunction, LossPipe
from data.af2fs import AF2FSDB
from data.md_cath import mdCATHDataset
from data.hybrid import HybridDataset

from moleculib.protein.transform import ProteinCrop, ProteinPad, DescribeChemistry
from moleculib.loss.structure import VectorMapLoss

from data.misato import MISATO
from data.atlas import ATLASDataset
import numpy as np

from functools import partial
import jax.numpy as jnp
import einops as ein
from jax.tree_util import tree_map
from learnax.utils import tree_stack

import biotite
from tensorclouds.loss.matching import TensorCloudMatchingLoss


def build_model(cfg):
    return DeepJump(
        irreps=cfg.model.irreps,
        depth=cfg.model.depth,
        cond_depth=cfg.model.cond_depth,
        header_depth=cfg.model.header_depth,
        k_seq=cfg.model.k_seq,
        radial_cut=cfg.model.radial_cut,
        leading_shape=(cfg.model.leading_shape,),
        var_features=cfg.model.var_features,
        var_coords=cfg.model.var_coords,
        timesteps=cfg.model.timesteps,
    )


def build_dataset(cfg):
    transforms = [
        # DescribeChemistry(),
        ProteinCrop(cfg.data.crop_size),
        ProteinPad(cfg.data.crop_size),
    ]

    if cfg.data.dataset == "mdCATH":
        return mdCATHDataset(
            base_path="/mnt/timebucket/molmach_db/mdCATH/",
            transform=transforms,
            temperatures=cfg.data.temperatures,
            # max_seq_len=cfg.data.crop_size,
            taus=cfg.data.deltas,
            size_multiplier=4,
        ), None

    elif cfg.data.dataset == "misato":
        return (
            MISATO(
                max_num_chains=cfg.data.max_num_chains,
                max_seq_len=cfg.data.crop_size,
                max_lig_len=cfg.data.lig_crop_size,
                filter_unk=True,
                transform=transforms,
            ),
            None,
        )

    elif cfg.data.dataset == "atlas":
        return ATLASDataset.split(
            base_path="/mnt/timebucket/molmach_db/atlas",
            transform=transforms,
        )


from moleculib.protein.datum import ProteinDatum
from moleculib.loss.chemistry import BondLoss, AngleLoss

from biotite.structure import lddt


def lddt(
    prediction: ProteinDatum,
    ground: ProteinDatum,
    cutoff=15,
    eps=1e-6,
    bins=[0.5, 1.0, 2.0, 4.0],
):
    ground = ground[1]

    ca_ground = ground.atom_coord[..., 1, :]
    ca_pred = prediction.atom_coord[..., 1, :]
    ca_mask = ground.atom_mask[..., 1]

    dist_map = lambda x: jnp.sqrt(
        jnp.sum((x[..., None, :] - x[..., None, :, :]) ** 2, axis=-1) + eps
    )
    dist_mask = jnp.logical_and(ca_mask[:, None], ca_mask[None, :])

    gnd_dist = dist_map(ca_ground)
    pred_dist = dist_map(ca_pred)

    lddt_mask = (gnd_dist < cutoff).astype(jnp.float32) * dist_mask
    lddt_mask = lddt_mask * (1.0 - jnp.eye(gnd_dist.shape[1]))

    dist = jnp.abs(pred_dist - gnd_dist)

    score = jnp.zeros_like(dist)
    for bin in bins:
        score += (dist < bin).astype(jnp.float32)
    score = score / len(bins)

    res_norm = 1.0 / (1e-10 + jnp.sum(lddt_mask, axis=-1))
    res_score = res_norm * (1e-10 + jnp.sum(lddt_mask * score, axis=-1))

    norm = 1.0 / (1e-10 + jnp.sum(lddt_mask, axis=(-1, -2)))
    score = norm * (1e-10 + jnp.sum(lddt_mask * score, axis=(-1, -2)))

    return score, res_score


class pLDDTHeader(LossFunction):

    def __call__(self, model_output: ProteinDatum, ground: ProteinDatum):
        score, res_score = lddt(prediction=model_output, ground=ground)
        # detach res_score gradient
        res_score = jax.lax.stop_gradient(res_score)

        mask = ground[1].atom_mask[..., 1]
        if hasattr(model_output, "resolution"):
            pred_res_score = model_output.resolution
        else:
            raise ValueError("Model output does not have a resolution attribute.")
        loss_ = jnp.square(res_score - pred_res_score[..., 0]) * mask
        unclipped_loss = jnp.sum(loss_) / jnp.sum(mask)
        loss = jnp.clip(unclipped_loss, 0.0, 5.0)

        return model_output, loss, {"lddt": score, "uncertainty_header_loss": loss, 'unclipped_uncertainty_header_loss': unclipped_loss}


def build_loss(cfg):
    return LossPipe(
        [VectorMapLoss()],
        # [TensorCloudMatchingLoss()], #BondLoss(), AngleLoss(), ClashLoss()],
        transform=lambda x: ProteinDatum.from_tensor_cloud(x),
    )


def build_pipeline(cfg, run, restore: bool = False):
    train_ds, val_ds = build_dataset(cfg)

    cfg.model.leading_shape = cfg.data.crop_size

    model = build_model(cfg)
    losses = build_loss(cfg)

    jax.config.update("jax_disable_jit", cfg.env.disable_jit)
    jax.config.update("jax_debug_nans", cfg.env.debug_nans)

    learning_rate = optax.linear_schedule(
        init_value=cfg.train.lr_start,
        end_value=cfg.train.lr_end,
        transition_steps=cfg.train.lr_steps,
        transition_begin=1,
    )

    trainer = Trainer(
        model=model,
        learning_rate=learning_rate,
        losses=losses,
        seed=cfg.train.seed,
        train_dataset=train_ds,
        num_epochs=cfg.train.num_epochs,
        batch_size=cfg.train.batch_size,
        num_workers=cfg.train.num_workers,
        save_every=cfg.train.save_every,
        run=run,
        save_model=None,
        single_datum=cfg.train.single_datum,
        registry="deepjump",
        val_datasets=val_ds,
        val_every=cfg.train.val_every,
        load_checkpoint=restore,
    )

    return trainer


def build_simulation_loader(
    mode, dataset, protein, batch_size, num_steps, seq_len=None
):
    from utils import build_alpha_helix, build_beta_strand
    from moleculib.protein.datum import ProteinDatum

    if mode == "crystal":

        init_datum = ProteinDatum.from_atom_array(dataset.get_crystal(protein))
        if seq_len != None:
            init_datum = ProteinPad(seq_len)(init_datum)
        init_data = [init_datum] * batch_size
        loader = [init_data] * num_steps

    elif mode == "alpha" or mode == "beta":

        aa = dataset.atom_arrays[protein]
        _, seq = biotite.structure.get_residues(aa)
        seq = "".join(
            [
                biotite.sequence.ProteinSequence.convert_letter_3to1(seq_).upper()
                for seq_ in seq
            ]
        )

        builder = build_alpha_helix if mode == "alpha" else build_beta_strand
        chain = ProteinDatum.from_atom_array(builder(seq))

        if seq_len != None:
            chain = ProteinPad(seq_len)(chain)

        init_data = [chain] * batch_size
        loader = [init_data] * num_steps

    elif mode == "default":
        from torch.utils.data import DataLoader

        if seq_len != None:
            dataset.transform = [ProteinPad(seq_len)]
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            collate_fn=lambda x: [x_[0] for x_ in x],
            num_workers=0,
        )

    return loader


def build_simulation_model(
    weights,
    temp,
    config,
    init_data,
    timesteps=None,
    delta=1,
):
    # config.model.leading_shape = dataset.pad.pad_size
    config.model.leading_shape = len(init_data[0])
    batch_size = len(init_data)

    if temp != 0:
        temp = config.data.temperatures.index(temp) + 1

    model = build_model(config)
    params = {"params": weights}

    @partial(jax.pmap, in_axes=(0, 0))
    def _sample_pmap(keys, prots):
        return jax.vmap(
            lambda k, p: model.apply(
                params,
                p,
                temp=jnp.array([temp]),
                delta=jnp.array([delta]),
                rngs={"params": k},
                method="sample",
                num_steps=timesteps,
            )
        )(keys, prots)

    device_count = jax.device_count()

    def _sample(key, batch):
        batch = tree_map(
            lambda v: (
                ein.rearrange(
                    v,
                    "(p q) ... -> p q ...",
                    p=device_count,
                    q=batch_size // device_count,
                )
                if not (v is None)
                else v
            ),
            batch,
        )
        keys = ein.rearrange(
            jax.random.split(key, batch_size),
            "(p q) ... -> p q ...",
            p=device_count,
            q=batch_size // device_count,
        )

        out = _sample_pmap(keys, batch)
        out = tree_map(lambda v: ein.rearrange(v, "p q ... -> (p q) ..."), out)
        return out

    # init_key = jax.random.PRNGKey(42)
    # print(f"Compiling Sampling...")
    # _sample(init_key, tree_stack(init_data))

    return _sample


from metrics import TICAMetric, CrystalRMSD, Gyradius, FNC, RMSF
from learnax.metrics import MetricPipe


def build_metrics(cfg, dataset, protein):
    metrics = []

    crystal = dataset.get_crystal(protein)
    # crystal = crystal[(crystal.element != 'H')]
    # crystal = crystal[:-1] # drop the last oxygen

    crystal = crystal[(crystal.atom_name == "CA")]

    if "tica" in cfg.evaluate:
        reference = dataset.get_metrics(protein)
        tica_model = reference["tica_model"]
        msm = reference["clusters"]
        metrics.append(TICAMetric(reference_tica=tica_model, reference_msm=msm))

    metrics.extend(
        [
            CrystalRMSD(crystal=crystal),
            Gyradius(),
            FNC(crystal=crystal),
            RMSF(crystal=crystal),
        ]
    )

    return MetricPipe(metrics)

