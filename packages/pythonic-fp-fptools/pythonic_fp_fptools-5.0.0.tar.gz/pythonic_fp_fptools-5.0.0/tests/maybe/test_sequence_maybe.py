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

from pythonic_fp.containers.functional_tuple import FTuple
from pythonic_fp.fptools.maybe import MayBe
from pythonic_fp.containers.queues.de import DEQueue as DQ, de_queue as dq


class Test_MB_sequence:
    """Test MayBe sequence class function"""

    def test_no_empties(self) -> None:
        """Test without empty MayBe values"""
        list_mb_int = list(map(MayBe, range(1, 2501)))
        tuple_mb_int = tuple(map(MayBe, range(1, 2501)))
        ftuple_mb_int = FTuple(map(MayBe, range(1, 2501)))
        dqueue_mb_int = DQ(map(MayBe, range(1, 2501)))

        mb_list_int = MayBe.sequence(list_mb_int)
        mb_tuple_int = MayBe.sequence(tuple_mb_int)
        mb_ftuple_int = MayBe.sequence(ftuple_mb_int)
        mb_dqueue_int = MayBe.sequence(dqueue_mb_int)

        assert mb_list_int == MayBe(list(range(1, 2501)))
        assert mb_tuple_int == MayBe(tuple(range(1, 2501)))
        assert mb_ftuple_int == MayBe(FTuple(range(1, 2501)))
        assert mb_dqueue_int == MayBe(DQ(range(1, 2501)))

    def test_with_empties(self) -> None:
        """Test with empty MayBe values"""
        list_of_mb_int = [MayBe[int](), MayBe(2), MayBe(3), MayBe(4)]
        tuple_of_mb_int = MayBe(1), MayBe[int](), MayBe(3), MayBe(4)
        ftuple_of_mb_int = FTuple([MayBe(1), MayBe(2), MayBe[int](), MayBe(4)])
        dqueue_of_mb_int = dq(MayBe(1), MayBe(2), MayBe(3), MayBe[int]())

        mb_list_int = MayBe.sequence(list_of_mb_int)
        mb_tuple_int = MayBe.sequence(tuple_of_mb_int)
        mb_ftuple_int = MayBe.sequence(ftuple_of_mb_int)
        mb_dqueue_int = MayBe.sequence(dqueue_of_mb_int)

        assert mb_list_int == MayBe()
        assert mb_tuple_int == MayBe()
        assert mb_ftuple_int == MayBe()
        assert mb_dqueue_int == MayBe()
