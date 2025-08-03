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

from pythonic_fp.fptools.maybe import MayBe


def add2(x: int) -> int:
    return x + 2

class TestMayBe:
    def test_identity(self) -> None:
        n1: MayBe[int] = MayBe()
        n2: MayBe[int] = MayBe()
        o1 = MayBe(42)
        o2 = MayBe(40)
        assert o1 is o1
        assert o1 is not o2
        o3 = o2.map(add2)
        assert o3 is not o2
        assert o1 is not o3
        assert n1 is n1
        assert n1 is not n2
        assert o1 is not n1
        assert n2 is not o2

    def test_equality(self) -> None:
        n1: MayBe[int] = MayBe()
        n2: MayBe[int] = MayBe()
        o1 = MayBe(42)
        o2 = MayBe(40)
        assert o1 == o1
        assert o1 != o2
        o3 = o2.map(add2)
        assert o3 != o2
        assert o1 == o3
        assert n1 == n1
        assert n1 == n2
        assert o1 != n1
        assert n2 != o2

    def test_iterate(self) -> None:
        o1 = MayBe(38)
        o2 = o1.map(add2).map(add2)
        n1: MayBe[int] = MayBe()
        l1 = []
        l2 = []
        for v in n1:
            l1.append(v)
        for v in o2:
            l2.append(v)
        assert len(l1) == 0
        assert len(l2) == 1
        assert l2[0] == 42

    def test_get(self) -> None:
        o1 = MayBe(1)
        n1: MayBe[int] = MayBe()
        assert o1.get(42) == 1
        assert n1.get(21) == 21
        assert o1.get() == 1
        try:
            foo = 42
            foo = n1.get()
        except ValueError:
            assert True
        else:
            assert False
        finally:
            assert foo == 42
        assert n1.get(13) == (10 + 3)
        assert n1.get(10 // 7) == 10 // 7

    def test_equal_self(self) -> None:
        mb42 = MayBe(40 + 2)
        mbno: MayBe[int] = MayBe()
        assert mb42 != mbno
        assert mb42 == mb42
        assert mbno == mbno
