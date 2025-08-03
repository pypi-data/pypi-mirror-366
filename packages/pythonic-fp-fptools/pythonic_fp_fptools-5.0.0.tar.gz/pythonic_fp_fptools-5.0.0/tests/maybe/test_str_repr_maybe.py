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
from pythonic_fp.fptools.either import Either as Either, LEFT, RIGHT


def add_lt_42(x: int, y: int) -> MayBe[int]:
    sum_xy = x + y
    if sum_xy < 42:
        return MayBe(sum_xy)
    else:
        return MayBe()

def add_gt_42(x: int, y: int) -> Either[int, str]:
    sum_xy = x + y
    if sum_xy > 42:
        return Either(sum_xy)
    else:
        return Either('too small', RIGHT)

class Test_str:
    def test_MayBe_str(self) -> None:
        n1: MayBe[int] = MayBe()
        o1 = MayBe(42)
        assert str(n1) == 'MayBe()'
        assert str(o1) == 'MayBe(42)'
        mb1 = add_lt_42(3, 7)
        mb2 = add_lt_42(15, 30)
        assert str(mb1) == 'MayBe(10)'
        assert str(mb2) == 'MayBe()'
        nt1: MayBe[int] = MayBe()
        assert str(nt1) == str(mb2) =='MayBe()'

    def test_either_str(self) -> None:
        assert str(Either[int, str](10, LEFT)) == '< 10 | >'
        assert str(add_gt_42(10, -4)) == '< | too small >'
        assert str(add_gt_42(10, 40)) == "< 50 | >"
        assert str(Either('Foofoo rules', RIGHT)) == "< | Foofoo rules >"
        assert str(Either[int, str](42, LEFT)) == "< 42 | >"
        assert str(Either[str, int]('foofoo', LEFT)) == "< foofoo | >"

class Test_repr:
    def test_mb_repr(self) -> None:
        mb1: MayBe[object] = MayBe()
        mb2: MayBe[object] = MayBe()
        mb3: MayBe[object] = MayBe(42)
        assert mb1 == mb2 == MayBe()
        assert repr(mb2) == 'MayBe()'
        mb4 = eval(repr(mb3))
        assert mb4 == mb3

        def lt5orNothing(x: int) -> MayBe[int]:
            if x < 5:
                return MayBe(x)
            else:
                return MayBe()

        mb5 = lt5orNothing(3)
        mb6 = lt5orNothing(9)
        mb7 = lt5orNothing(18)

        assert mb4 != mb5
        assert mb6 == mb7

        assert repr(mb5) ==  'MayBe(3)'
        assert repr(mb6) == repr(mb7) ==  'MayBe()'

        mb_str = MayBe('foo')
        mb_str_2 = eval(repr(mb_str))
        assert mb_str_2 == mb_str
        assert repr(mb_str_2) == repr(mb_str) =="MayBe('foo')"
        if mb_str:
            assert True
        else:
            assert False

        mb_str0 = MayBe('')
        mb_str0_2 = eval(repr(mb_str0))
        assert mb_str0_2 == mb_str0
        assert repr(mb_str0_2) == repr(mb_str0) =="MayBe('')"
        if mb_str0:
            assert True
        else:
            assert False

        mb_none = MayBe(None)
        mb_none_2 = eval(repr(mb_none))
        assert mb_none_2 == mb_none
        assert repr(mb_none_2) == repr(mb_none_2) =="MayBe(None)"
        if mb_none:
            assert True
        else:
            assert False

        mb_never: MayBe[str] = MayBe()
        mb_never_2 = eval(repr(mb_never))
        assert mb_never_2 == mb_never
        assert repr(mb_never_2) == repr(mb_never) =="MayBe()"
        if mb_never:
            assert False
        else:
            assert True

        mbmb_str = MayBe(MayBe('foo'))
        mbmb_str_2 = eval(repr(mbmb_str))
        assert mbmb_str_2 == mbmb_str
        assert repr(mbmb_str_2) == repr(mbmb_str) =="MayBe(MayBe('foo'))"
        if mbmb_str:
            assert True
        else:
            assert False

        mbmb_str0 = MayBe(MayBe(''))
        mbmb_str0_2 = eval(repr(mbmb_str0))
        assert mbmb_str0_2 == mbmb_str0
        assert repr(mbmb_str0_2) == repr(mbmb_str0) =="MayBe(MayBe(''))"
        if mbmb_str0:
            assert True
        else:
            assert False

        mbmb_none = MayBe(MayBe(None))
        mbmb_none_2 = eval(repr(mbmb_none))
        assert mbmb_none_2 == mbmb_none
        assert repr(mbmb_none_2) == repr(mbmb_none_2) =="MayBe(MayBe(None))"
        if mbmb_none:
            assert True
        else:
            assert False

        mbmb_never: MayBe[MayBe[str]] = MayBe(MayBe())
        mbmb_never_2 = eval(repr(mbmb_never))
        assert mbmb_never_2 == mbmb_never
        assert repr(mbmb_never_2) == repr(mbmb_never) =="MayBe(MayBe())"
        if mbmb_never:
            assert True
        else:
            assert False

    def test_either_repr(self) -> None:
        e1: Either[int, str] = Either('Nobody home!', RIGHT)
        e2: Either[int, str] = Either('Somebody not home!', RIGHT)
        e3: Either[int, str] = Either(5, LEFT)
        assert e1 != e2
        e5 = eval(repr(e2))
        assert e2 != Either('Nobody home!', RIGHT)
        assert e2 == Either('Somebody not home!', RIGHT)
        assert e5 == e2
        assert e5 != e3
        assert e5 is not e2
        assert e5 is not e3

        def lt5_or_nothing(x: int) -> MayBe[int]:
            if x < 5:
                return MayBe(x)
            else:
                return MayBe()

        def lt5_or_str(x: int) -> Either[int, str]:
            if x < 5:
                return Either(x, LEFT)
            else:
                return Either(f'was to be {x}', RIGHT)

        e6 = lt5_or_nothing(2)
        e7 = lt5_or_str(2)
        e8 = lt5_or_str(3)
        e9 = lt5_or_nothing(7)
        e10 = Either[int, str](10).bind(lt5_or_str)

        assert e6 != e7
        assert e7 != e8
        assert e9 != e10
        assert e8 == eval(repr(e7)).map(lambda x: x+1)

        assert repr(e6) ==  "MayBe(2)"
        assert repr(e7) ==  "Either(2, LEFT)"
        assert repr(e8) ==  "Either(3, LEFT)"
        assert repr(e9) == "MayBe()"
        assert repr(e10) ==  "Either('was to be 10', RIGHT)"
