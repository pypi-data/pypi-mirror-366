# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Note: import <name> as <name> is required for names to be exported.
# See PEP 484 & https://github.com/jax-ml/jax/issues/7570
# pylint: disable=g-multiple-import,useless-import-alias,g-importing-member
from neuralgcm.experimental.xreader.iterators import (
    evaluation_iterator as evaluation_iterator,
    training_iterator as training_iterator,
)
from neuralgcm.experimental.xreader.stencils import (
    Stencil as Stencil,
    TimeStencil as TimeStencil,
    valid_origin_points as valid_origin_points,
)
