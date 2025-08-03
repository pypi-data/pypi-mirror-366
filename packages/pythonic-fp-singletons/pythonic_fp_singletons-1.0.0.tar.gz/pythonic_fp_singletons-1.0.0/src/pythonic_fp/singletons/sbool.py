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


"""Class `SBool` - Subclassable Singleton Booleans

Python does not permit bool to be subclassed, but ``int`` can be
subclassed. Under-the-hood a ``bool`` is just an ``int``. The
SBool class inherits from ``int`` and relies on the underlying
truthiness and falsiness of ``1`` and ``0``.

The ``Truth(truth: str)`` and ``Lie(lie: str)`` subclass constructors
produce singletons based on their input parameters. When using type
hints, declare variables of these types as type ``SBool``.

Best practices when used with these subclasses are:

- use `==` or `!=` for pure Boolean comparisons
- use `is` or `not is` if the type of truth matters
- only use ``SBool`` as a type, never as a constructor
- when using Python shortcut logic remember

  - an instance of ``Truth`` is truthy
  - an instance of ``Lie`` is falsy
  - shortcut logic is lazy

    - the last truthy thing evaluated is returned
    - and is not converted to a ``bool``

  - the `not` statement converts a ``SBool`` to an actual ``bool``

"""

from __future__ import annotations

from typing import Final

__all__ = ['SBool', 'Truth', 'Lie', 'TRUTH', 'LIE']


class SBool(int):
    """Subclassable Boolean hierarchy.

    This class's sub-types represent different "flavors" of "truth"
    where each flavor has one unique "truthy" and one unique "falsy"
    instance.

    .. note::
        
        Python does not permit bool to be subclassed, but ``int`` can
        be. Under-the-hood a ``bool`` is just an ``int``. This class
        inherits from ``int`` and relies on the underlying truthiness
        and falsiness of ``1`` and ``0``.

    .. important::

        Only use SBool as a type, never as a constructor.

    """

    def __new__(cls) -> SBool:
        return super(SBool, cls).__new__(cls, 0)

    def __repr__(self) -> str:
        if self:
            return 'SBool(1)'
        return 'SBool(0)'

    def flavor(self) -> str:
        raise NotImplementedError


class Truth(SBool):
    """Truthy singleton SBool subclass.

    .. note::
        When using type hints, declare variables SBool, not Truth.

    """

    _instances: dict[str, Truth] = dict()

    def __new__(cls, flavor: str = 'DEFAULT_TRUTH') -> Truth:
        if flavor not in cls._instances:
            cls._instances[flavor] = super(SBool, cls).__new__(cls, 1)
        return cls._instances[flavor]

    def __init__(self, flavor: str = 'DEFAULT_TRUTH') -> None:
        self._flavor = flavor

    def __repr__(self) -> str:
        return f"Truth('{self._flavor}')"

    def flavor(self) -> str:
        return self._flavor


class Lie(SBool):
    """Falsy singleton SBool subclass.

    .. note::
        When using type hints, declare variables SBool, not Lie.

    """

    _instances: dict[str, Lie] = dict()

    def __new__(cls, flavor: str = '') -> Lie:
        if flavor not in cls._instances:
            cls._instances[flavor] = super(SBool, cls).__new__(cls, 0)
        return cls._instances[flavor]

    def __init__(self, flavor: str = '') -> None:
        self._flavor = flavor

    def __repr__(self) -> str:
        return f"Lie('{self._flavor}')"

    def flavor(self) -> str:
        return self._flavor


TRUTH: Final[Truth] = Truth()
LIE: Final[Lie] = Lie()


def snot(val: SBool) -> SBool:
    """Return the opposite truthiness of the same flavor of truth.

    .. note::

        Trying to use the Python ``not`` operator for this will just
        return a ``bool``. There is no ``__not__`` dunder method
        that will change the behavior of ``not``.

    """
    if val:
        return Lie(val.flavor())
    return Truth(val.flavor())
