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

__all__ = ['NoValue']


class NoValue:
    """Singleton class representing a missing value.

    Similar to ``None`` but

    - while ``None`` represents "returned no values"
    - ``NoValue()`` represents the absence of a value

    **Usage:**

    - ``import NoValue`` from ``pythonic-fp.singletons`` and then

      - either use ``NoValue()`` directly
      - or define ``_noValue: Final[NoValue] = NoValue()`` don't export it

    - compare using ``is`` and ``is not``

      - not ``==`` or ``!=``
      - ``None`` means returned no values, so ``None == None`` makes sense
      - if one or both values are missing, then what is there to compare?

    """

    __slots__ = ()
    _instance: NoValue | None = None

    def __new__(cls) -> NoValue:
        if cls._instance is None:
            cls._instance = super(NoValue, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        return

    def __repr__(self) -> str:
        return 'NoValue()'

    def __eq__(self, other: object) -> bool:
        return False
