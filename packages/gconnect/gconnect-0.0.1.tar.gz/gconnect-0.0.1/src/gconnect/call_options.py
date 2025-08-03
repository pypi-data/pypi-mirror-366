# Copyright 2025 Gaudiy Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""Call options configuration models."""

import asyncio

from pydantic import BaseModel, ConfigDict, Field


class CallOptions(BaseModel):
    """Options for configuring a call.

    Attributes:
        timeout (float | None): Timeout for the call in seconds. If None, no timeout is applied.
        abort_event (asyncio.Event | None): Event to abort the call. If set, the call can be cancelled by setting this event.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    timeout: float | None = Field(default=None)
    """Timeout for the call in seconds."""

    abort_event: asyncio.Event | None = Field(default=None)
    """Event to abort the call."""
