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
# See the License for the specific language governing permissions anddd
# limitations under the License.

from pythonic_fp.fptools.function import partial, sequenced, swap
from pythonic_fp.iterables.drop_take import take
from pythonic_fp.iterables.folding import maybe_fold_left

class Test_function:
    def test_same_type(self) -> None:
        def multAdd(m1: int, m2: int, a: int) -> int:
            return m1*m2 + a

        ans = 8*5 + 2
        assert ans == multAdd(8, 5, 2)

        p2 = partial(multAdd, 8)
        p1 = partial(multAdd, 8, 5)
        p0 = partial(multAdd, 8, 5, 2)

        assert p2(5, 2) == p1(2) == p0() == ans

        s2 = swap(p2)
        assert s2(341, 5621) == p2(5621, 341)

    def test_different_types(self) -> None:
        def names(num: int, sep: str, names: list[str]) -> str:
            return maybe_fold_left(take(names, num),
                         lambda names, name: names + sep + name,
                         "").get()[len(sep):]

        charactors = ['Moe', 'Larry', 'Curlie', 'Shemp', 'Curlie Joe']
        stooges = names(3, ', ', charactors)
        assert stooges == 'Moe, Larry, Curlie'
        stooges = names(1, ', ', charactors)
        assert stooges == 'Moe'
        stooges = names(0, ', ', charactors)
        assert stooges == ''

        stooges3 = partial(names, 3, ' and ')
        assert stooges3(charactors) == 'Moe and Larry and Curlie'

    def test_sequenced(self) -> None:
        def compute(a: float, b: float, c: float, d: int) -> float:
            return ( (a + b)*c ) ** d

        data: tuple[float, float, float, int] = (3.1, 4.2, 2.7, 5)
        compute_seq = sequenced(compute)

        assert compute(*data) == compute_seq(data)
