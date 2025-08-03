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

from __future__ import annotations

from pythonic_fp.circulararray.auto import ca
from pythonic_fp.singletons.nada import Nada

nada = Nada()

def add2(x: int|Nada) -> int|Nada:
    return x + 2

def make_non_negative(x: int|Nada) -> int|Nada:
    if x >= 0:
        return x
    if x < 0:
        return 0
    return nada

def not_nada(x: object) -> bool:
    if x is nada:
        return False
    else:
        return True

class TestBuiltinContainers:
    def test_mixed_list(self) -> None:
        foo: list[int|Nada] = [23, -5, nada, nada, -1, 40]

        bar: list[int|Nada] = list(map(add2, foo))
        assert bar == [25, -3, nada, nada, 1, 42]

        baz: list[int|Nada] = []
        for x in foo:
            baz.append(make_non_negative(x))
        assert baz == [23, 0, nada, nada, 0, 40]

        fuz = list(filter(not_nada, foo))
        assert fuz == [23, -5, -1, 40]

        zud1 = list(filter(None, foo))
        zud2 = list(filter(None, baz))
        assert zud1 == [23, -5, -1, 40]
        assert zud2 == [23, 40]

    def test_mixed_tuples(self) -> None:
        tup0: tuple[tuple[int|Nada, ...]|Nada, ...] = \
            (0, 1, 2, 3), \
            (-1, 10, nada, 30, 40, nada, 60), \
            tuple(range(40, 81)) + (nada, nada), \
            nada, \
            (99, nada)*5

        tup1: tuple[int|Nada, ...] = ()

        for idx in range(len(tup0)):
            tup1 += tup0[idx][2],
        assert tup1 == (2, nada, 42, nada, 99)

    def test_dicts(self) -> None:
        dict1 = {None:'0', ():'1', nada:'2', 42:'42'}
        assert dict1[None] == str(0)
        assert dict1[()] == str(1)
        assert dict1[nada] == str(2)
        assert dict1[Nada()] == str(2) # PyPI version < 0.1.2
        assert dict1[42] == str(42)

        foo = Nada()
        bar = Nada()
        dict2 = {1: 42, 2: foo, 3: bar}
        assert dict2[1] == 42
        assert dict2[2] is Nada()
        assert dict2[3] is Nada()
        assert dict2[2] is dict2[3]
        assert foo is bar
        assert dict2[2] is foo
        assert dict2[2] is dict2[3]
        assert dict2[2] is dict2[2]

    def test_comparibility(self) -> None:
        cir1 = 42, ca(42, nada)
        cir2 = 42, ca(42, nada)
        assert cir1 == cir2  # CAs now compare with identity before equality
        assert cir1 is not cir2

        tup1 = 42, [42]
        tup2 = 42, [42]
        assert tup1 == tup2  # lists must compare identity before equality
        assert tup1 is not tup2

        tup3 = 42, [42, nada]
        tup4 = 42, [42, nada]
        assert tup3 == tup4
        assert tup3 is not tup4  # because both contain mutable objects
        assert tup3[1].pop(-1) is nada
        assert tup4[1].pop(-1) is nada
        tup3[1].append(100)
        tup4[1].append(200)
        assert tup3 != tup4
        tup4[1][1] -= 100     # type: ignore # to test, I have to lie somewhere
        assert tup3 == tup4
        tup4[1][0] += 1       # type: ignore
        assert tup3 != tup4
        tup3[1][0] += 1       # type: ignore
        assert tup3 == tup4

