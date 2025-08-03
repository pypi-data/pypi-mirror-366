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

from pythonic_fp.singletons.sbool import SBool as SBool, Truth, Lie, TRUTH, LIE

class Testbool:
    """Test class pythonic_fp.fptools.bool"""
    def test_equality(self) -> None:
        assert TRUTH == TRUTH
        assert LIE == LIE
        assert TRUTH != LIE  # type: ignore # Non-overlapping identity check
        assert TRUTH is TRUTH
        assert LIE is LIE
        assert TRUTH is not LIE  # type: ignore # Non-overlapping identity check

        sky_is_blue: SBool = TRUTH
        koalas_eat_meat: SBool = LIE
        water_is_wet: SBool = Truth()
        ice_is_hot: SBool = Lie()

        assert sky_is_blue == water_is_wet
        assert koalas_eat_meat == ice_is_hot
        assert sky_is_blue != koalas_eat_meat
        assert water_is_wet != ice_is_hot

        assert sky_is_blue is water_is_wet
        assert koalas_eat_meat is ice_is_hot

        if sky_is_blue:
            assert True
        else:
            assert False

        if koalas_eat_meat:
            assert False
        else:
            assert True

        assert sky_is_blue == 1
        assert sky_is_blue != 0
        assert sky_is_blue != 5
        assert koalas_eat_meat == 0
        assert koalas_eat_meat != 1
        assert koalas_eat_meat != 5

        foo: SBool = TRUTH
        assert foo == TRUTH
        foo = LIE
        assert foo == LIE


class Test_issubclass:
    assert issubclass(Truth, SBool)
    assert issubclass(Lie, SBool)
    assert issubclass(Truth, int)
    assert issubclass(Lie, int)
    assert issubclass(SBool, int)
    assert issubclass(bool, int)
    assert not issubclass(bool, SBool)
    assert not issubclass(SBool, bool)


class Test_isinstance:
    a_bool = False
    my_int = 0
    myLie = Lie()

    assert isinstance(a_bool, int)
    assert isinstance(a_bool, bool)
    assert isinstance(my_int, int)
    assert isinstance(myLie, int)
    assert isinstance(myLie, SBool)
    assert isinstance(myLie, Lie)
    assert not isinstance(myLie, Truth)
    assert not isinstance(myLie, bool)
    assert isinstance(not myLie, bool)

    a_bool = True
    my_int = 1
    myTruth = Truth()

    assert isinstance(a_bool, int)
    assert isinstance(a_bool, bool)
    assert isinstance(my_int, int)
    assert isinstance(myTruth, int)
    assert isinstance(myTruth, SBool)
    assert isinstance(myTruth, Truth)
    assert not isinstance(myTruth, Lie)
    assert not isinstance(myTruth, bool)
    assert isinstance(not myTruth, bool)

class Test_not:
    foo: int = 42
    assert isinstance(foo, int)
    assert not isinstance(foo, bool)
    assert isinstance(not foo, int)
    assert isinstance(not foo, bool)
    assert not isinstance(not foo, SBool)

    bar: bool = True
    assert isinstance(bar, int)
    assert isinstance(bar, bool)
    assert isinstance(not bar, int)
    assert isinstance(not bar, bool)
    assert not isinstance(not bar, SBool)

    baz: SBool = TRUTH
    assert isinstance(baz, int)
    assert not isinstance(baz, bool)
    assert isinstance(not baz, int)
    assert isinstance(not baz, bool)
    assert not isinstance(not baz, SBool)

    quuz: SBool = LIE
    assert isinstance(quuz, int)
    assert not isinstance(quuz, bool)
    assert isinstance(not quuz, int)
    assert isinstance(not quuz, bool)
    assert not isinstance(not quuz, SBool)

    putz: SBool = Truth()
    assert isinstance(putz, int)
    assert not isinstance(putz, bool)
    assert isinstance(not putz, int)
    assert isinstance(not putz, bool)
    assert not isinstance(not putz, SBool)

    lutz: SBool = Lie()
    assert isinstance(lutz, int)
    assert not isinstance(lutz, bool)
    assert isinstance(not lutz, int)
    assert isinstance(not lutz, bool)
    assert not isinstance(not lutz, SBool)

class TestTruthsAndLies:
    fooT: SBool = Truth('foo')
    fudT: SBool = Truth('foo')
    fooL: SBool = Lie('foo')
    fudL: SBool = Lie('foo')

    booT: SBool = Truth('boo')
    budT: SBool = Truth('boo')
    booL: SBool = Lie('boo')
    boobooL: SBool = Lie('boo')

    assert fooT == fooT
    assert fudT == fudT
    assert fooT == fudT
    assert fooL == fooL
    assert fooL == fudL
    assert booT == fooT
    assert booT == fudT
    assert booL == fooL
    assert booL == fudL

    assert fooT != fooL
    assert booT != fudL

    assert fooT is fooT
    assert fudT is fudT
    assert fooT is fudT
    assert fooL is fooL
    assert fooL is fudL
    assert booT is not fooT
    assert booT is not fudT
    assert booL is not fooL
    assert booL is not fudL

    assert fooT is not fooL
    assert booT is not fudL

class TestSuperClassType:
    mooT: SBool = Truth('my_truth')
    yooT: SBool = Truth('your_truth')
    mooL: SBool = Lie('my_lie')
    yooL: SBool = Lie('your_lie')

    mooT == yooT
    mooL == yooL
    mooT != yooL

    mooT is not yooT
    mooL is not yooL
    mooT is not yooL
