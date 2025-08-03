# Copyright 2023-2025 Geoffrey R. Scheller
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

"""Pythonic FP - Collection of singleton classes"""

from __future__ import annotations

__all__ = ['Sentinel']

from typing import final


@final
class Sentinel:
    """Singleton classes representing sentinel values.

    - intended for library code, not to be exported/shared between modules

      - otherwise some of its intended typing guarantees may be lost

    - useful substitute for ``None`` as a hidden sentinel value

      - allows ``None`` to be stored in data structures
      - allows end users to choose to use ``None`` or ``()`` as sentinel values
      - always equals itself (unlike ``NoValue``)

    **Usage:**

    - import Sentinel and then either

      - define ``_my_sentinel: Final[Sentinel] = Sentinel('my_sentinel')``
      - or use ``Sentinel('my_sentinel')`` directly

    - compare using either

      - ``is`` and ``is not`` or ``==`` and ``!=``
      - the ``Sentinel()`` value always equals itself
      - and never equals anything else, especially other sentinel values

    """

    __slots__ = ('_sentinel_name',)
    _instances: dict[str, Sentinel] = {}

    def __new__(cls, sentinel_name: str) -> Sentinel:
        if sentinel_name not in cls._instances:
            cls._instances[sentinel_name] = super(Sentinel, cls).__new__(cls)
        return cls._instances[sentinel_name]

    def __init__(self, sentinel_name: str) -> None:
        self._sentinel_name = sentinel_name

    def __repr__(self) -> str:
        return "Sentinel('" + self._sentinel_name + "')"
