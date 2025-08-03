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

"""Pythonic FP - Functional Tuple"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import cast, Never, overload, TypeVar
from pythonic_fp.iterables.folding import accumulate
from pythonic_fp.iterables.merging import blend, concat, MergeEnum

__all__ = ['FTuple']

D = TypeVar('D', covariant=True)

class FTuple[D](tuple[D, ...]):
    """Functional Tuple suitable for inheritance

    - Supports both indexing and slicing
    - FTuple addition and int multiplication supported

      - addition concatenates results, resulting in a Union type
      - both left and right int multiplication supported
      - homogeneous in its data type
      - supports being further inherited from
      - unslotted

    - Since these tuples are homogeneous, their covariance may be quirky

    """
    def __reversed__(self) -> Iterator[D]:
        for ii in range(len(self) - 1, -1, -1):
            yield (self[ii])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + ', '.join(map(repr, self)) + ')'

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if (length := len(self)) != len(other):
            return False
        if self is other:
            return True
        for ii in range(length):
            if self[ii] != other[ii]:
                return False
        return True

    @overload    # type:ignore
    def __getitem__(self, x: int) -> D: ...
    @overload
    def __getitem__(self, x: slice) -> tuple[D, ...]: ...

    def __getitem__(self, idx: int | slice, /) -> tuple[D, ...] | D:
        def newtup(tup: tuple[D, ...]) -> tuple[D, ...]:
            return tup[0:-1] + tup[-1:]

        if isinstance(idx, slice):
            return self.__class__(newtup(super().__getitem__(idx)))
        else:
            return super().__getitem__(idx)

    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """Fold Left

        - fold left with an optional starting value
        - first argument of function f is for the accumulated value

        :raises ValueError: when FTuple empty and a start value not given

        """
        it_self = iter(self)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it_self))
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty FTuple'
                raise ValueError('FTuple.foldl - ' + msg)
            acc = default
        for v in it_self:
            acc = f(acc, v)
        return acc

    def foldr[R](
        self,
        f: Callable[[D, R], R],
        /,
        start: R | None = None,
        default: R | None = None,
    ) -> R | None:
        """Fold Right

        - fold right with an optional starting value
        - second argument of function f is for the accumulated value

        :raises ValueError: when FTuple empty and a start value not given

        """
        it_self = reversed(self)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it_self))
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty FTuple'
                raise ValueError('FTuple.foldR - ' + msg)
            acc = default
        for v in it_self:
            acc = f(v, acc)
        return acc

    def copy(self) -> FTuple[D]:
        """Return a shallow copy of ``FTuple`` in O(1) time & space complexity."""
        return self.__class__(self)

    def __add__(self, other: object, /) -> tuple[D, ...]:
        if not isinstance(other, FTuple):
            msg = 'FTuple being added to something not an FTuple'
            raise ValueError(msg)
        return self.__class__(concat(self, other))

    def __mul__(self, num: int, /) -> tuple[D, ...]:
        return self.__class__(super().__mul__(num))

    def __rmul__(self, num: int, /) -> tuple[D]:
        return self.__class__(super().__rmul__(num))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> FTuple[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an ``FTuple`` with an optional
        starting value.

        """
        if s is None:
            return FTuple(accumulate(self, f))
        return FTuple(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> FTuple[U]:
        return FTuple(map(f, self))

    def bind[U](
            self, f: Callable[[D], FTuple[U]],
            merge_enum: MergeEnum = MergeEnum.Concat,
            yield_partials: bool = False,
        ) -> FTuple[U] | Never:
        """Bind function ``f`` to the ``FTuple``.

        :param ds: values to instantiate FTuple
        :return: resulting FTuple
        :raises ValueError: if given unknown merge_type

        """
        return FTuple(
            blend(
                *map(f, self),
                merge_enum=merge_enum,
                yield_partials=yield_partials
            )
        )
