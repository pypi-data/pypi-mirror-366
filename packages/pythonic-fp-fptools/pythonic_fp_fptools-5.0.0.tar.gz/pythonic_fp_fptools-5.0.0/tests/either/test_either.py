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

from typing import Never
from pythonic_fp.fptools.maybe import MayBe
from pythonic_fp.fptools.either import Either, LEFT, RIGHT


# -- Simple contrived tests ----------------------------------------------------


def gt42(x: int) -> bool | Never:
    """contrived function that fails for 42, returns a bool"""
    if x > 42:
        return True
    if x < 42:
        return False
    raise ValueError('x = 42')


def lt42bool(x: int) -> Either[bool, str] | Never:
    """contrived function that fails for 42, returns an Either"""
    if x < 42:
        return Either(True, LEFT)
    if x > 42:
        return Either(f'{x}', RIGHT)
    raise ValueError('42 failed')


def fail_int(x: int) -> int | Never:
    """contrived function that fails for all but 1 unusual argument"""
    if x != -666:
        raise ValueError
    return x


def fail_str(s: str) -> str | Never:
    if s != '-666':
        raise ValueError
    return s


class TestSimole:
    """Simple tests"""

    def test_equal(self) -> None:
        """some non-systematic tests"""
        xor41 = Either[int, str](40 + 1, LEFT)
        xor42: Either[int, str] = Either(40 + 2, LEFT)
        xor43: Either[int, str] = Either(40 + 3, LEFT)
        xor_no42: Either[int, str] = Either('no 42', RIGHT)
        xor_fortytwo: Either[str, int] = Either('forty-two', LEFT)
        xor_str_42: Either[str, int] = Either(21 * 2, RIGHT)
        xor_42tuple: Either[int, tuple[int, ...]] = Either(42, LEFT)
        xor42_tuple: Either[int, tuple[int, ...]] = Either((2, 3), side=RIGHT)

        assert xor42 == xor42
        assert xor_no42 == xor_no42
        assert xor_fortytwo == xor_fortytwo
        assert xor_str_42 == xor_str_42
        assert xor_42tuple == xor_42tuple
        assert xor42_tuple == xor42_tuple

        assert xor41 != xor43
        assert xor42 != xor_fortytwo
        assert xor42 != xor_str_42
        assert xor42 == xor_42tuple
        assert xor_42tuple != xor42_tuple

    def test_identity(self) -> None:
        """identity tests"""
        e1: Either[int, str] = Either(42, LEFT)
        e2: Either[int, str] = Either(42, LEFT)
        e3: Either[int, str] = Either('The secret is unknown', RIGHT)
        e4: Either[int, str] = Either('not 42', RIGHT)
        e5: Either[int, str] = Either('also not 42', RIGHT)
        e6 = e3
        assert e1 is e1
        assert e1 is not e2
        assert e1 is not e3
        assert e1 is not e4
        assert e1 is not e5
        assert e1 is not e6
        assert e2 is e2
        assert e2 is not e3
        assert e2 is not e4
        assert e2 is not e5
        assert e2 is not e6
        assert e3 is e3
        assert e3 is not e4
        assert e3 is not e5
        assert e3 is e6
        assert e4 is e4
        assert e4 is not e5
        assert e4 is not e6
        assert e5 is e5
        assert e5 is not e6
        assert e6 is e6

    def test_equality(self) -> None:
        """equality tests"""
        e1: Either[int, str] = Either(42, LEFT)
        e2: Either[int, str] = Either(42, LEFT)
        e3: Either[int, str] = Either('not 42', RIGHT)
        e4: Either[int, str] = Either('not 42', RIGHT)
        e5: Either[int, str] = Either('also not 42', RIGHT)
        e6 = e3
        assert e1 == e1
        assert e1 == e2
        assert e1 != e3
        assert e1 != e4
        assert e1 != e5
        assert e1 != e6
        assert e2 == e2
        assert e2 != e3
        assert e2 != e4
        assert e2 != e5
        assert e2 != e6
        assert e3 == e3
        assert e3 == e4
        assert e3 != e5
        assert e3 == e6
        assert e4 == e4
        assert e4 != e5
        assert e4 == e6
        assert e5 == e5
        assert e5 != e6
        assert e6 == e6

    def test_MB_Either(self) -> None:
        """Proving a nothing can be stored in a something"""
        mb_42 = MayBe(42)
        mb_not: MayBe[int] = MayBe()

        left_mb_42: Either[MayBe[int], str] = Either(mb_42, LEFT)
        left_mb_not: Either[MayBe[int], str] = Either(mb_not, LEFT)
        assert left_mb_42 == Either(MayBe(42), LEFT)
        assert left_mb_not == Either(MayBe(), LEFT)

        phNot1: MayBe[Either[MayBe[int], str]] = MayBe(Either(MayBe[int](), LEFT))
        phNot2 = MayBe(Either[int, str]('', RIGHT))
        assert phNot1 != phNot2

        none_to_the_left_1: Either[None, None] = Either(None, LEFT)
        none_to_the_left_2: Either[None, None] = Either(None, LEFT)
        none_to_the_right_1: Either[None, None] = Either(None, RIGHT)
        none_to_the_right_2: Either[None, None] = Either(None, RIGHT)

        assert none_to_the_left_1 == none_to_the_left_1
        assert none_to_the_left_2 == none_to_the_left_2
        assert none_to_the_left_1 == none_to_the_left_2
        assert none_to_the_right_1 == none_to_the_right_1
        assert none_to_the_right_2 == none_to_the_right_2
        assert none_to_the_right_1 == none_to_the_right_2
        assert none_to_the_left_1 != none_to_the_right_1
        assert none_to_the_left_2 != none_to_the_right_2


# -- Test map and map_right ----------------------------------------------------------


def add2ifLT5(x: int) -> int | Never:
    """Contrived function to fail if given 5"""
    if x < 5:
        return x + 2
    elif x > 5:
        return x
    else:
        raise ValueError


def add_1_if_gt_5(x: int) -> int:
    """Contrived function to fail if given 5"""
    if x == 5:
        raise ValueError
    if x > 5:
        return x + 1
    return x


def chk_str_starts_map(s: str) -> str | Never:
    """Contrived function to fail if str given does not start 'map'"""
    if s[0:3] == 'map':
        return f'{s}'
    else:
        raise ValueError


class TestMapExcept:
    """Test map_except"""

    def test_xor_map_except_1(self) -> None:
        """Test 1 map_except"""
        s2 = Either[int, str](2, LEFT)
        s5 = Either[int, str](5, LEFT)
        s10 = Either[int, str](10, LEFT)
        s_foo_m = Either[int, str]('foo', RIGHT)

        assert s2.get_left() == MayBe(2)
        assert s5.get_left() == MayBe(5)
        assert s10.get_left() == MayBe(10)
        assert s_foo_m.get_left() == MayBe()
        assert s2.get_right() == MayBe()
        assert s5.get_right() == MayBe()
        assert s10.get_right() == MayBe()
        assert s_foo_m.get_right() == MayBe('foo')

        s2 = s2.map_except(add2ifLT5, 'map_except failed 2')
        s5 = s5.map_except(add2ifLT5, 'map_except failed 5')
        s10 = s10.map_except(add2ifLT5, 'map_except failed 10')
        s_foo_m = s_foo_m.map_except(add2ifLT5, 'map_except failed foo')
        s_foo_cr = s_foo_m.map_right(lambda s: f'Foo{s} rules!')

        assert s2.get_left() == MayBe(4)
        assert s5.get_left() == MayBe()
        assert s10.get_left() == MayBe(10)
        assert s_foo_m.get_left() == MayBe()
        assert s2.get_right() == MayBe()
        assert s5.get_right() == MayBe('map_except failed 5')
        assert s10.get_right() == MayBe()
        assert s_foo_m.get_right() == MayBe('foo')
        assert s_foo_cr.get_right() == MayBe('Foofoo rules!')

        try:
            s2g = s2.get()
            assert s2g == 4
            s10g = s10.get()
            assert s10g == 10
        except AssertionError:
            assert False
        except ValueError:
            assert False
        else:
            assert True

        try:
            assert s5.get() > 0
        except AssertionError:
            assert False
        except ValueError:
            assert True
        else:
            assert False

        try:
            assert s2.get() == 2
        except AssertionError:
            assert True
        except ValueError:
            assert False
        else:
            assert False

    def test_xor_maps(self) -> None:
        """Test 2 map_except"""

        s2 = Either[int, str](2, LEFT)
        s5 = Either[int, str](5, LEFT)
        s10 = Either[int, str](10, LEFT)
        s_bar = Either[int, str]('bar', RIGHT)

        s2g = s2.get()
        s10g = s10.get()
        s2gl = s2.get_left()
        s5gl = s5.get_left()
        s10gl = s10.get_left()
        s_bar_gl = s_bar.get_left()
        s2gr = s2.get_right()
        s5gr = s5.get_right()
        s10gr = s10.get_right()
        s_bar_gr = s_bar.get_right()

        assert s2g == 2
        assert s10g == 10
        assert s2gl == MayBe(2)
        assert s5gl == MayBe(5)
        assert s10gl == MayBe(10)
        assert s_bar_gl == MayBe()
        assert s2gr == MayBe()
        assert s5gr == MayBe()
        assert s10gr == MayBe()
        assert s_bar_gr == MayBe('bar')

        s2 = s2.map_except(add_1_if_gt_5, 'map_except failed 2')
        s5 = s5.map_except(add_1_if_gt_5, 'map_except failed 5')
        s10 = s10.map_except(add_1_if_gt_5, 'map_except failed 10')
        s_bar = s_bar.map_except(add_1_if_gt_5, 'map_except failed bar')

        s2g = s2.get()
        s10g = s10.get()
        s2gl = s2.get_left()
        s5gl = s5.get_left()
        s10gl = s10.get_left()
        s_bar_gl = s_bar.get_left()
        s2gr = s2.get_right()
        s5gr = s5.get_right()
        s10gr = s10.get_right()
        s_bar_gr = s_bar.get_right()

        assert s2g == 2
        assert s10g == 11
        assert s2gl == MayBe(2)
        assert s5gl == MayBe()
        assert s10gl == MayBe(11)
        assert s_bar_gl == MayBe()
        assert s2gr == MayBe()
        assert s5gr == MayBe('map_except failed 5')
        assert s10gr == MayBe()
        assert s_bar_gr == MayBe('bar')

        try:
            s2g = s2.get()
            s10g = s10.get()
            assert s2g == 2
            assert s10g == 11
        except AssertionError:
            assert False
        except ValueError:
            assert False

        try:
            s5g = s5.get()
            assert s5g > 0
        except AssertionError:
            assert False
        except ValueError:
            assert True

        try:
            s2g = s2.get()
            assert s2g != 2
        except AssertionError:
            assert True
        except ValueError:
            assert False

        try:
            s_bar_g = s_bar.get()
            assert s_bar_g != 2
        except AssertionError:
            assert False
        except ValueError:
            assert True


# -- Test map and map_right ----------------------------------------------------------


def lessThan2(x: int) -> Either[int, str]:
    if x < 2:
        return Either(x, LEFT)
    else:
        return Either(f'{x} >= 2', RIGHT)


def lessThan5(x: int) -> Either[int, str]:
    if x < 5:
        return Either(x, LEFT)
    else:
        return Either(f'{x} >= 5', RIGHT)


class TestBind:
    """Test map and map_right together"""

    def test_xor_bind(self) -> None:
        left1 = Either[int, str](1, LEFT)
        left4 = Either[int, str](4, LEFT)
        left7 = Either[int, str](7, LEFT)
        right: Either[int, str] = Either('Nobody home.', RIGHT)

        nobody = right.bind(lessThan2)
        assert nobody == Either('Nobody home.', RIGHT)

        lt2 = left1.bind(lessThan2)
        lt5 = left1.bind(lessThan5)
        assert lt2 == Either(1, LEFT)
        assert lt5 == Either(1, LEFT)

        lt2 = left4.bind(lessThan2)
        lt5 = left4.bind(lessThan5)
        assert lt2 == Either('4 >= 2', RIGHT)
        assert lt5 == Either(4, LEFT)

        lt2 = left7.bind(lessThan2)
        lt5 = left7.bind(lessThan5)
        assert lt2 == Either('7 >= 2', RIGHT)
        assert lt5 == Either('7 >= 5', RIGHT)

        nobody = right.bind(lessThan5)
        assert nobody == Either('Nobody home.', RIGHT)

        lt2 = left1.bind(lessThan2)
        lt5 = left1.bind(lessThan5)
        assert lt2 == Either(1, LEFT)
        assert lt5 == Either(1, LEFT)

        lt2 = left4.bind(lessThan2)
        lt5 = left4.bind(lessThan5)
        assert lt2 == Either('4 >= 2', RIGHT)
        assert lt2 != Either('42 >= 2', RIGHT)
        assert lt5 == Either(4, LEFT)
        assert lt5 != Either('5 >= 5', RIGHT)

        lt2 = left7.bind(lessThan2).map_right(lambda _: 'greater than 1')
        lt5 = left7.bind(lessThan5).map_right(lambda s: s + ', greater than 4')
        assert lt2 == Either('greater than 1', RIGHT)
        assert lt5 == Either('7 >= 5, greater than 4', RIGHT)


class TestEitherUsecases:
    """Non-systematic tests for ease of use"""

    def test_usecase(self) -> None:
        "Get Smart logic"

        def lt42(x: int) -> Either[int, str] | Never:
            """contrived function that fails for 42, returns an Either"""
            if x < 42:
                return Either(x, LEFT)
            if x > 42:
                return Either(f'Agent {x}', RIGHT)
            raise ValueError('42 failed')

        xor_99 = Either[int, str](99, LEFT)
        xor_86 = Either[int, str]('Max', RIGHT)
        xor_49 = Either[int, str](49, LEFT)
        xor_42 = Either[int, str](42, LEFT)
        xor_21 = Either[int, str](21, LEFT)
        xor_12 = Either[int, str](12, LEFT)
        xor_01 = Either[int, str](1, LEFT)

        assert xor_99.get() == 99
        assert xor_99.get_right() == MayBe()
        try:
            agent = xor_86.get()
            assert agent == 86
        except AssertionError:
            assert False
        except ValueError:
            assert True
        else:
            assert False
        assert xor_86.get_right() == MayBe('Max')

        kaos0: Either[bool, str] = Either(True, LEFT)
        kaos1 = xor_99.map(gt42)
        kaos2 = xor_49.map(gt42)
        assert kaos0 == kaos1 == kaos2

        kaos0 = Either(False, LEFT)
        kaos1 = xor_01.map(gt42)
        kaos2 = xor_86.map(gt42)
        kaos3: Either[bool, str] = Either('Max', RIGHT)
        assert kaos0 == kaos1 != kaos2 == kaos3

        kaos0 = Either(False, LEFT)
        kaos1 = xor_12.map(gt42)
        kaos2 = xor_21.map(gt42)
        assert kaos0 == kaos1 == kaos2

        kaos0 = Either('Kaos Reins!', RIGHT)
        kaos1 = xor_42.map_except(gt42, 'Kaos Reins!' )
        assert kaos0 == kaos1

        # refactored by adding map_right
        chief1 = xor_86.map(lambda n: f'Agent {n}, you are a genius!').map_right(
            lambda s: f'{s}, you idiot!'
        )

        chief2 = xor_86.map_right(lambda s: f'{s}, you idiot!').map(
            lambda n: f'Agent {n}, you are a genius!'
        )

        chief3 = xor_99.map(lambda n: f'Agent {n}, you are a genius!').map_right(
            lambda s: f'{s}, you idiot!'
        )

        chief4 = xor_99.map_right(lambda s: f'{s}, you idiot!').map(
            lambda n: f'Agent {n}, you are a genius!'
        )

        assert chief1 == Either('Max, you idiot!', RIGHT)
        assert chief2 == Either('Max, you idiot!', RIGHT)
        assert chief3 == Either('Agent 99, you are a genius!', LEFT)
        assert chief4 == Either('Agent 99, you are a genius!', LEFT)

        hymie42: Either[str, str] = Either('I am a robot.', RIGHT)
        hymie99 = xor_99.bind(lt42).map(lambda n: f'Hey {n}, got some oil?').map_right(lambda s: f'Hello {s}.')
        hymie21 = xor_21.bind(lt42).map(lambda n: f'Hey {n}, got some oil?').map_right(lambda s: f'Hello {s}.')
        try:
            hymie42 = xor_42.bind(lt42).map(lambda n: f'Hey {n}, got some oil?').map_right(lambda s: f'Hello {s}.')
        except ValueError:
            assert True
        else:
            assert False

        assert hymie99 == Either('Hello Agent 99.', RIGHT)
        assert hymie21 == Either('Hey 21, got some oil?', LEFT)
        assert hymie42 == Either('I am a robot.', RIGHT)
