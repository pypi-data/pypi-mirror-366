from typing import Dict
from moleculib.protein.metrics import (
    CountClashes,
    StandardBondDeviation,
    StandardAngleDeviation,
    StandardDihedralDeviation,
)

from .base.utils import ModelOutput
import jax, jax.numpy as jnp


class SequenceProfile:
    def __call__(
        self,
        model_output: ModelOutput,
    ):
        (res_logits, sos_logits, eos_logits) = model_output.logits
        eos_idx = eos_logits.argmax(-1)
        sos_idx = sos_logits.argmax(-1)
        res_pred = res_logits.argmax(-1)
        sequence_length = eos_idx - sos_idx
        eos_mask = jnp.cumsum(
            jax.nn.one_hot(eos_idx + 1, eos_logits.shape[-1]), axis=-1
        )
        sos_mask = jnp.cumsum(jax.nn.one_hot(sos_idx, sos_logits.shape[-1]), axis=-1)
        pad_mask = res_pred == 0
        mid_mask = sos_mask - eos_mask
        pad_mid = pad_mask * mid_mask

        metrics = dict(
            valid_length=(sequence_length > 0).astype(res_logits.dtype).mean(),
            mean_length=sequence_length.mean(),
            mid_pad_mean=(pad_mid.sum(-1) / sequence_length).mean(),
        )
        return metrics


class CountClashesWrap:
    def __init__(self):
        self.f = CountClashes()

    def __call__(self, model_output: ModelOutput) -> Dict:
        return self.f(model_output.datum)


class StandardChemicalDeviation:
    def __init__(self):
        self.fb = StandardBondDeviation()
        self.fa = StandardAngleDeviation()
        self.fd = StandardDihedralDeviation()
        self.cc = CountClashes()

    def __call__(self, datum) -> Dict:
        metrics = self.fb(datum)
        metrics.update(self.fa(datum))
        metrics.update(self.fd(datum))
        metrics.update(self.cc(datum))
        return metrics
