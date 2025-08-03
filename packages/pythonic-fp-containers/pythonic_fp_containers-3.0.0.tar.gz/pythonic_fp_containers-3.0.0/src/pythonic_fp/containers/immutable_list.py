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

"""Pythonic FP - Immutable guaranteed hashable lists

- hashable if elements are hashable
- declared covariant in its generic datatype
  - hashability should be enforced by LSP tooling
  - hashability will be enforced at runtime
  - IList addition supported via concatenation
  - IList integer multiplication supported

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Hashable
from typing import cast, Never, overload, TypeVar
from pythonic_fp.iterables.folding import accumulate
from pythonic_fp.iterables.merging import blend, concat, MergeEnum

__all__ = ['IList']

D = TypeVar('D', covariant=True)
T = TypeVar('T')

class IList[D](Hashable):
    """Immutable List like data structure.

    - its method type parameters are also covariant
    - hashability will be enforced by LSP tooling
    - supports both indexing and slicing
    - addition concatenates results, resulting type a Union type
    - both left and right int multiplication supported

    """
    __slots__ = ('_ds', '_len', '_hash')
    __match_args__ = ('_ds', '_len')

    L = TypeVar('L')
    R = TypeVar('R')
    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) > 1:
            msg = f'IList expects at most 1 iterable argument, got {size}'
            raise ValueError(msg)
        else:
            self._ds: tuple[D, ...] = tuple(dss[0]) if size == 1 else tuple()
            self._len = len(self._ds)
            try:
                self._hash = hash((self._len, 42) + self._ds)
            except TypeError as exc:
                msg = f'IList: {exc}'
                raise TypeError(msg)

    def __hash__(self) -> int:
        return self._hash

    def __iter__(self) -> Iterator[D]:
        return iter(self._ds)

    def __reversed__(self) -> Iterator[D]:
        return reversed(self._ds)

    def __bool__(self) -> bool:
        return bool(self._ds)

    def __len__(self) -> int:
        return len(self._ds)

    def __repr__(self) -> str:
        return 'immutable_list(' + ', '.join(map(repr, self)) + ')'

    def __str__(self) -> str:
        return '((' + ', '.join(map(repr, self)) + '))'

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, IList):
            return NotImplemented  # magic object
        if self._len != other._len:
            return False
        if self._ds is other._ds:
            return True
        return self._ds == other._ds

    @overload
    def __getitem__(self, idx: int, /) -> D: ...
    @overload
    def __getitem__(self, idx: slice, /) -> IList[D]: ...

    def __getitem__(self, idx: slice | int, /) -> IList[D] | D:
        if isinstance(idx, slice):
            return IList(self._ds[idx])
        return self._ds[idx]

    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """Fold Left

        - fold left with an optional starting value
        - first argument of function ``f`` is for the accumulated value
        
        "raises ValueError: when empty and a start value not given

        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))  # L_co = D_co in this case
        else:
            if default is None:
                msg0 = 'IList: foldl method requires '
                msg1 = 'either start or default to be defined for '
                msg2 = 'an empty IList'
                raise ValueError(msg0 + msg1 + msg2)
            acc = default
        for v in it:
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
        - second argument of function ``f`` is for the accumulated value

        "raises ValueError: when empty and a start value not given

        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))
        else:
            if default is None:
                msg0 = 'IList: foldr method requires '
                msg1 = 'either start or default to be defined for '
                msg2 = 'an empty IList'
                raise ValueError(msg0 + msg1 + msg2)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def __add__(self, other: IList[D], /) -> IList[D]:
        if not isinstance(other, IList):
            msg = 'IList being added to something not a IList'
            raise ValueError(msg)

        return IList(concat(self, other))

    def __mul__(self, num: int, /) -> IList[D]:
        return IList(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> IList[D]:
        return IList(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> IList[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an IList with
        an optional starting value.

        """
        if s is None:
            return IList(accumulate(self, f))
        return IList(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> IList[U]:
        return IList(map(f, self))

    def bind[U](
            self,
            f: Callable[[D], IList[U]],
            merge_enum: MergeEnum = MergeEnum.Concat,
            yield_partials: bool = False,
        ) -> IList[U] | Never:
        """Bind function `f` to the `IList`.

        :param ds: values to instantiate IList
        :return: resulting IList
        :raises ValueError: if given unknown merge_type

        """
        return IList(
            blend(
                *map(f, self),
                merge_enum=merge_enum,
                yield_partials=yield_partials
            )
        )
