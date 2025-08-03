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

from typing import Final
from pythonic_fp.containers.functional_tuple import FTuple
from pythonic_fp.fptools.either import Either, LEFT, RIGHT
from pythonic_fp.containers.queues.fifo import FIFOQueue


class TestEitherSequence:
    """Test Either sequence class function"""

    def test_no_rights(self) -> None:
        """Test with omly left values"""
        list_of_either_int_str: list[Either[int, str]] = list(
            map(lambda x: Either(x, LEFT), range(1, 2501))
        )
        tuple_of_either_int_str: tuple[Either[int, str], ...] = tuple(
            map(lambda x: Either(x, LEFT), range(1, 2501))
        )
        ftuple_of_either_int_str: FTuple[Either[int, str]] = FTuple(
            map(lambda x: Either(x, LEFT), range(1, 2501))
        )
        fifo_of_either_int_str: FIFOQueue[Either[int, str]] = FIFOQueue(
            map(lambda x: Either(x, LEFT), range(1, 2501))
        )

        either_listInt_str = Either.sequence(list_of_either_int_str)
        either_tupleInt_str = Either.sequence(tuple_of_either_int_str)
        either_ftuple_int_str = Either.sequence(ftuple_of_either_int_str)
        either_fifo_int_str = Either.sequence(fifo_of_either_int_str)


        assert either_listInt_str == Either(list(range(1, 2501)), LEFT)
        assert either_tupleInt_str == Either(tuple(range(1, 2501)), LEFT)
        assert either_ftuple_int_str == Either(FTuple(range(1, 2501)), LEFT)
        assert either_fifo_int_str == Either(FIFOQueue(range(1, 2501)), LEFT)

    def test_with_a_right(self) -> None:
        """Test with a single right value, use multiple data structures"""
        list_of_either_int_str: list[Either[int, str]] = [
            Either('1', RIGHT), Either(2, LEFT), Either(3, LEFT), Either(4, LEFT)
        ]
        tuple_of_either_int_str: tuple[Either[int, str], ...] = (
            Either(1, LEFT), Either('2', RIGHT), Either(3, LEFT), Either(4, LEFT)
        )
        ftuple_of_either_int_str = FTuple(
            (Either(1, LEFT), Either(2, LEFT), Either('3', RIGHT), Either(4, LEFT),)
        )
        fifo_of_either_int_str = FIFOQueue(
            (Either(1, LEFT), Either(2, LEFT), Either(3, LEFT), Either('4', RIGHT),)
        )

        either_list_int = Either.sequence(list_of_either_int_str)
        either_tuple_int = Either.sequence(tuple_of_either_int_str)
        either_ftuple_int = Either.sequence(ftuple_of_either_int_str)
        either_fifo_int: Either[FIFOQueue[int], str] = Either.sequence(fifo_of_either_int_str)

        assert either_list_int == Either('1', RIGHT)
        assert either_tuple_int == Either('2', RIGHT)
        assert either_ftuple_int == Either('3', RIGHT)
        assert either_fifo_int == Either('4', RIGHT)

    def test_with_multiple_rights(self) -> None:
        """Test with a multiple right value"""

        type Letter = Either[str, int]
        type Letters = Either[list[str], int]

        ALPHABET: Final[str] = ' abcdefghijklmnopqrstuvwxyz'

        def alphabet_position(char_str: str) -> int:
            """Letter position in ALPHABET"""
            char = ' '
            if len(char_str):
                char = char_str[0]
            if 0 < (pos := ord(char) - 96) < 27:
                return pos
            return 0

        def letter_left(letter: str) -> Letter:
            pos = alphabet_position(letter)
            return Either(ALPHABET[pos], LEFT)

        def letter_right(letter: str) -> Letter:
            pos = alphabet_position(letter)
            return Either(pos, RIGHT)

        letter_set_0 = list[str]()
        letter_set_1 = ['a', 'w', 's', 's', 'b', 'm', 'j']
#       letter_set_2 = ['w', 'x', 'y', 'z', ' ']
#       letter_set_3 = ['waldo', 'x', 'y', 'zebra', '']

        data0 = list(map(letter_left, letter_set_0))
        data1 = list(map(letter_left, letter_set_1))
        data2 = list(data1)
        data2[5] = data2[5].bind(letter_right)

        sequenced_data0 = Either.sequence(data0)
        sequenced_data1 = Either.sequence(data1)
        sequenced_data2: Letters = Either.sequence(data2)

        result0: Letters = Either([], LEFT)
        result1: Letters = Either(letter_set_1, LEFT)
        result2: Letters = Either(13, RIGHT)

        assert sequenced_data0 == result0
        assert sequenced_data1 == result1
        assert sequenced_data2 == result2
