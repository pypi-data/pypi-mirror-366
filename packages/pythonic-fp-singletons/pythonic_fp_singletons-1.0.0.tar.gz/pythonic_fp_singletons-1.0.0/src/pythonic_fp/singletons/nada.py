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

__all__ = ['Nada']

from collections.abc import Callable, Iterator
from typing import Any, Final, final
from .sentinel import Sentinel


@final
class Nada:
    """Singleton class representing & propagating failure.

    - singleton ``_nada: nada = Nada()`` represents a non-existent value
    - returns itself for arbitrary method calls
    - returns itself if called as a Callable with arbitrary arguments
    - interpreted as an empty container by standard Python functions
    - warning: non-standard equality semantics

      - comparison compares true only when 2 non-missing values compare true
      - thus ``a == b`` means two non-missing values compare as equal

    **Usage:**

    - import ``Nada`` and then

      - either use ``Nada()`` directly
      - or define ``_nada: Final[Nada] = Nada()`` don't export it

    - start propagating failure by setting a propagating value to Nada()

      - works best when working with expression
      - failure may fail to propagate

        - for a function/method with just side effects
        - engineer Nada() to fail to trigger side effects

    - test for failure by comparing a result to ``Nada()`` itself using

      - ``is`` and ``is not``

    - propagate failure through a calculation using

      - ``==`` and ``!=``
      - the ``Nada()`` value never equals itself
      - and never equals anything else

    """

    __slots__ = ()
    _instance: Nada | None = None
    _hash: int = 0

    SENTINEL: Final[Sentinel] = Sentinel('Nada')

    def __new__(cls) -> Nada:
        if cls._instance is None:
            cls._instance = super(Nada, cls).__new__(cls)
            cls._hash = hash((cls._instance, (cls._instance,)))
        return cls._instance

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self) -> str:
        return 'Nada()'

    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __add__(self, right: Any) -> Nada:
        return Nada()

    def __radd__(self, left: Any) -> Nada:
        return Nada()

    def __mul__(self, right: Any) -> Nada:
        return Nada()

    def __rmul__(self, left: Any) -> Nada:
        return Nada()

    def __eq__(self, right: Any) -> bool:
        return False

    def __ne__(self, right: Any) -> bool:
        return True

    def __ge__(self, right: Any) -> bool:
        return False

    def __gt__(self, right: Any) -> bool:
        return False

    def __le__(self, right: Any) -> bool:
        return False

    def __lt__(self, right: Any) -> bool:
        return False

    def __getitem__(self, index: int | slice) -> Any:
        return Nada()

    def __setitem__(self, index: int | slice, item: Any) -> None:
        return

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return Nada()

    def __getattr__(self, name: str) -> Callable[..., Any]:
        def method(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            return Nada()

        return method

    def nada_get(self, alt: Any = SENTINEL) -> Any:
        """Get an alternate value, defaults to ``Nada()``."""
        if alt == Sentinel('Nada'):
            return Nada()
        return alt
