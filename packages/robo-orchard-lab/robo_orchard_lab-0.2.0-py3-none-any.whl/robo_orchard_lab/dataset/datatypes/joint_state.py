# Project RoboOrchard
#
# Copyright (c) 2024-2025 Horizon Robotics. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

import datasets as hg_datasets
from robo_orchard_core.datatypes.joint_state import (
    BatchJointsState as _BatchJointsState,
)

from robo_orchard_lab.dataset.datatypes.hg_features import (
    RODictDataFeature,
    ToDataFeatureMixin,
    TypedDictFeatureDecode,
    check_fields_consistency,
    hg_dataset_feature,
)
from robo_orchard_lab.dataset.datatypes.hg_features.tensor import (
    TypedTensorFeature,
)

__all__ = [
    "BatchJointsStateFeature",
    "BatchJointsState",
]


class BatchJointsState(_BatchJointsState, ToDataFeatureMixin):
    """Batch joint states of robot.

    This class extends the base BatchJointsState and provides methods
    to encode and decode joint states for dataset storage.
    """

    @classmethod
    def dataset_feature(
        cls, dtype: Literal["float32", "float64"] = "float32"
    ) -> BatchJointsStateFeature:
        ret = BatchJointsStateFeature(dtype=dtype)
        check_fields_consistency(cls, ret.pa_type)
        return ret


@hg_dataset_feature
@dataclass
class BatchJointsStateFeature(RODictDataFeature, TypedDictFeatureDecode):
    dtype: Literal["float32", "float64"] = "float32"
    decode: bool = True

    _decode_type: type = BatchJointsState

    def __post_init__(self):
        _typed_tensor_feature = TypedTensorFeature(
            dtype=self.dtype, as_torch_tensor=True
        )
        self._dict = {
            "position": _typed_tensor_feature,
            "velocity": _typed_tensor_feature,
            "effort": _typed_tensor_feature,
            "names": hg_datasets.features.features.Sequence(
                hg_datasets.features.features.Value("string")
            ),
            "timestamps": hg_datasets.features.features.Sequence(
                hg_datasets.features.features.Value("int64")
            ),
        }
