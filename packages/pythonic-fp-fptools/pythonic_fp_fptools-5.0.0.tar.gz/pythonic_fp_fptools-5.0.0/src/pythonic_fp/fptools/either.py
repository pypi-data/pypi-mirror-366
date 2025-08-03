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

__all__ = ['Either', 'LEFT', 'RIGHT']

from collections.abc import Callable, Iterator, Sequence
from typing import cast, Never, overload, TypeVar
from pythonic_fp.singletons.sbool import SBool, Truth as Left, Lie as Right
from pythonic_fp.singletons.sentinel import Sentinel as _Sentinel
from .maybe import MayBe

L = TypeVar('L', covariant=True)
R = TypeVar('R', covariant=True)

LEFT = Left('LEFT')
RIGHT = Right('RIGHT')


class Either[L, R]:
    """Either monad, data structure semantically containing either a left
    or a right value, but not both.

    Implements a left biased Either Monad.

    - `Either(value: +L, LEFT)` produces a left `Either`
    - `Either(value: +L, RIGHT)` produces a right `Either`

    In a Boolean context

    - `True` if a left `Either`
    - `False` if a right `Either`

    Two `Either` objects compare as equal when

    - both are left values or both are right values whose values

      - are the same object
      - compare as equal

    Immutable, an `Either` does not change after being created. Therefore
    map & bind return new instances

    .. warning::

        The contained value need not be immutable, therefore
        not hashable if value is mutable.

    .. note::

        ``Either(value: +L, side: Left): Either[+L, +R] -> left: Either[+L, +R]``
        ``Either(value: +R, side: Right): Either[+L, +R] -> right: Either[+L, +R]``

    """
    __slots__ = '_value', '_side'
    __match_args__ = ('_value', '_side')

    U = TypeVar('U', covariant=True)
    V = TypeVar('V', covariant=True)
    T = TypeVar('T')

    @overload
    def __init__(self, value: L, side: Left) -> None: ...
    @overload
    def __init__(self, value: R, side: Right) -> None: ...

    def __init__(self, value: L | R, side: SBool = LEFT) -> None:
        self._value = value
        self._side = side

    def __hash__(self) -> int:
        return hash((_Sentinel('XOR'), self._value, self._side))

    def __bool__(self) -> bool:
        return self._side == LEFT

    def __iter__(self) -> Iterator[L]:
        if self:
            yield cast(L, self._value)

    def __repr__(self) -> str:
        if self:
            return 'Either(' + repr(self._value) + ', LEFT)'
        return 'Either(' + repr(self._value) + ', RIGHT)'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._value) + ' | >'
        return '< | ' + str(self._value) + ' >'

    def __len__(self) -> int:
        """An Either always contains just one value."""
        return 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self and other:
            if (self._value is other._value) or (self._value == other._value):
                return True

        if not self and not other:
            if (self._value is other._value) or (self._value == other._value):
                return True

        return False

    def get(self) -> L | Never:
        """Get value if a left.

        .. warning::

            Unsafe method ``get``. Will raise ``ValueError`` if ``Either``
            is a right. Best practice is to first check the ``Either`` in
            a boolean context.

        :return: its value if a Left
        :rtype: +L
        :raises ValueError: if not a left

        """
        if self._side == RIGHT:
            msg = 'Either: get method called on a right valued Either'
            raise ValueError(msg)
        return cast(L, self._value)

    def get_left(self) -> MayBe[L]:
        """Get value of `Either` if a left. Safer version of `get` method.

        - if `Either` contains a left value, return it wrapped in a MayBe
        - if `Either` contains a right value, return MayBe()

        """
        if self._side == LEFT:
            return MayBe(cast(L, self._value))
        return MayBe()

    def get_right(self) -> MayBe[R]:
        """Get value of `Either` if a right

        - if `Either` contains a right value, return it wrapped in a MayBe
        - if `Either` contains a left value, return MayBe()

        """
        if self._side == RIGHT:
            return MayBe(cast(R, self._value))
        return MayBe()

    def map_right[V](self, f: Callable[[R], V]) -> Either[L, V]:
        """Construct new Either with a different right."""
        if self._side == LEFT:
            return cast(Either[L, V], self)
        return Either[L, V](f(cast(R, self._value)), RIGHT)

    def map[U](self, f: Callable[[L], U]) -> Either[U, R]:
        """Map over if a left value. Return new instance."""
        if self._side == RIGHT:
            return cast(Either[U, R], self)
        return Either(f(cast(L, self._value)), LEFT)

    def bind[U](self, f: Callable[[L], Either[U, R]]) -> Either[U, R]:
        """Flatmap over the left value, propagate right values."""
        if self:
            return f(cast(L, self._value))
        return cast(Either[U, R], self)

    def map_except[U](self, f: Callable[[L], U], fallback_right: R) -> Either[U, R]:
        """Map over if a left value - with fallback upon exception.

        - if `Either` is a left then map `f` over its value

          - if `f` successful return a left `Either[+U, +R]`
          - if `f` unsuccessful return right `Either[+U, +R]`

            - swallows many exceptions `f` may throw at run time

        - if `Either` is a right

          - return new `Either(right=self._right): Either[+U, +R]`

        """
        if self._side == RIGHT:
            return cast(Either[U, R], self)

        applied: MayBe[Either[U, R]] = MayBe()
        fall_back: MayBe[Either[U, R]] = MayBe()
        try:
            applied = MayBe(Either(f(cast(L, self._value)), LEFT))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            fall_back = MayBe(cast(Either[U, R], Either(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    def bind_except[U](
        self, f: Callable[[L], Either[U, R]], fallback_right: R
    ) -> Either[U, R]:
        """Flatmap `Either` with function `f` with fallback right

        .. warning::
            Swallows exceptions.

        :param fallback_right: fallback value if exception thrown

        """
        if self._side == RIGHT:
            return cast(Either[U, R], self)

        applied: MayBe[Either[U, R]] = MayBe()
        fall_back: MayBe[Either[U, R]] = MayBe()
        try:
            if self:
                applied = MayBe(f(cast(L, self._value)))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            fall_back = MayBe(cast(Either[U, R], Either(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    @staticmethod
    def sequence[U, V](
        sequence_xor_uv: Sequence[Either[U, V]],
    ) -> Either[Sequence[U], V]:
        """Sequence an indexable of type `Either[~U, ~V]`

        If the iterated `Either` values are all lefts, then return an `Either` of
        an iterable of the left values. Otherwise return a right Either containing
        the first right encountered.

        """
        list_items: list[U] = []

        for xor_uv in sequence_xor_uv:
            if xor_uv:
                list_items.append(xor_uv.get())
            else:
                return Either(xor_uv.get_right().get(), RIGHT)

        sequence_type = cast(Sequence[U], type(sequence_xor_uv))

        return Either(sequence_type(list_items))  # type: ignore # subclass will be callable
