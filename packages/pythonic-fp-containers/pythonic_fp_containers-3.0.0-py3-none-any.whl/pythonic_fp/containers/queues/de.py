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

"""Stateful Double-Ended (DE) Queue data structure.

- O(1) pops each end
- O(1) amortized pushes each end
- O(1) length determination
- will automatically increase storage capacity when needed
- in a Boolean context, true if not empty, false if empty
- neither indexable nor sliceable by design

"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar
from pythonic_fp.circulararray.auto import CA
from pythonic_fp.fptools.maybe import MayBe

__all__ = ['DEQueue', 'de_queue']

D = TypeVar('D')


class DEQueue[D]:

    __slots__ = ('_ca',)

    def __init__(self, *dss: Iterable[D]) -> None:
        """Initial data in FIFO order, newest to oldest, as if
        pushed on from the right side.

        :param dss: takes up to one iterable
        :raises ValueError: if more than 1 iterable is given

        """
        if (size := len(dss)) > 1:
            msg = f'DEQueue expects at most 1 argument, got {size}'
            raise ValueError(msg)
        self._ca = CA(dss[0]) if size == 1 else CA()

    def __bool__(self) -> bool:
        return len(self._ca) > 0

    def __len__(self) -> int:
        return len(self._ca)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DEQueue):
            return False
        return self._ca == other._ca

    def __iter__(self) -> Iterator[D]:
        return iter(list(self._ca))

    def __reversed__(self) -> Iterator[D]:
        return reversed(list(self._ca))

    def __repr__(self) -> str:
        if len(self) == 0:
            return 'DEQueue()'
        return 'DEQueue(' + ', '.join(map(repr, self._ca)) + ')'

    def __str__(self) -> str:
        return '>< ' + ' | '.join(map(str, self)) + ' ><'

    def copy(self) -> DEQueue[D]:
        """Shallow copy.

        :return: shallow copy of the DEQueue

        """
        return DEQueue(self._ca)

    def pushl(self, *ds: D) -> None:
        """Push data onto left side of DEQueue.

        :param ds: items to be pushed onto DEQueue from the left

        """
        self._ca.pushl(*ds)

    def pushr(self, *ds: D) -> None:
        """Push data onto right side of DEQueue.

        :param ds: items to be pushed onto DEQueue from the right

        """
        self._ca.pushr(*ds)

    def popl(self) -> MayBe[D]:
        """Pop next data item from left side DEQueue, if it exists.

        :return: MayBe of popped item if queue was not empty, empty MayBe otherwise

        """
        if self._ca:
            return MayBe(self._ca.popl())
        return MayBe()

    def popr(self) -> MayBe[D]:
        """Pop next item off right side DEQueue.

        :return: MayBe of popped item if queue was not empty, empty MayBe otherwise

        """
        if self._ca:
            return MayBe(self._ca.popr())
        return MayBe()

    def peakl(self) -> MayBe[D]:
        """Peak at data on left side of DEQueue.

        :return: MayBe of leftmost data if queue not empty, empty MayBe otherwise

        """
        if self._ca:
            return MayBe(self._ca[0])
        return MayBe()

    def peakr(self) -> MayBe[D]:
        """Peak at right side of DEQueue. Does not consume item.

        :return: MayBe of rightmost data if queue not empty, empty MayBe otherwise

        """
        if self._ca:
            return MayBe(self._ca[-1])
        return MayBe()

    def foldl[L](self, f: Callable[[L, D], L], start: L | None = None) -> MayBe[L]:
        """Reduces DEQueue left to right.

        :param f: reducing function, first argument is for accumulator
        :param start: optional starting value
        :return: MayBe of reduced value with f, empty MayBe if queue empty and no starting value given

        """
        if start is None:
            if not self._ca:
                return MayBe()
        return MayBe(self._ca.foldl(f, start))

    def foldr[R](self, f: Callable[[D, R], R], start: R | None = None) -> MayBe[R]:
        """Reduces DEQueue right to left.

        :param f: reducing function, second argument is for accumulator
        :param start: optional starting value
        :return: MayBe of reduced value with f, empty MayBe if queue empty and no starting value given

        """
        if start is None:
            if not self._ca:
                return MayBe()
        return MayBe(self._ca.foldr(f, start))

    def map[U](self, f: Callable[[D], U]) -> DEQueue[U]:
        """Map f over the DEQueue left to right, retain original order.

        :return: new DEQueue instance

        """
        return DEQueue(map(f, self._ca))


def de_queue[D](*ds: D) -> DEQueue[D]:
    """DEQueue factory function."""
    return DEQueue(ds)
