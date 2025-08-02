# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""AQT Quantizr API."""

# TODO(wppark): Remove this file. This is a temporary module before the
# official release of AQT quant / dequant API.

import functools
from typing import Sequence

from aqt.jax.v2 import aqt_quantizer
from aqt.jax.v2 import aqt_tensor
from aqt.jax.v2 import calibration
from aqt.jax.v2.numerics import fp8_numerics

import jax
import jax.numpy as jnp

QTensor = aqt_tensor.QTensor


def quant(
    x: jax.Array,
    n_bits: int | fp8_numerics.FP8Dtype,
    calibration_axes: Sequence[int] | None = None,
    use_dummy_static_bound: bool = False,
) -> QTensor:
  """Apply channel-wise quantization to x.

  x is quantized channel-wisely on the calibration axes.

  Args:
    x: input tensor
    n_bits: the precision for quantization.
    calibration_axes: the calibration axes. If None, calibration is done on the
      entire tensor.
    use_dummy_static_bound: If true, a static bound of 1.0 is used.
  Returns:
    A quantized QTensor
  """
  # jax.lax.stop_gradient is not supported in pallas, thus disable
  # scale_stop_grad in the quantizer.
  # VPU ops only support float32. jax implicitly converts tensor into float32.
  # However, pallas requires explicit casting. Therefore, we need to enforce
  # the scale factor and dequant dtype to be float32.
  quantizer = aqt_quantizer.quantizer_make(
      n_bits, scale_stop_grad=False, scale_dtype=jnp.float32
  )
  if calibration_axes is None:
    quantizer.calib_shared_axes = "per_tensor"
  if use_dummy_static_bound:
    quantizer.calibration = functools.partial(
        calibration.ConstantCalibration, bound=1.0
    )
  qx, _ = quantizer.quant(x, calibration_axes=calibration_axes)
  qx.dequant_dtype = jnp.float32
  return qx
