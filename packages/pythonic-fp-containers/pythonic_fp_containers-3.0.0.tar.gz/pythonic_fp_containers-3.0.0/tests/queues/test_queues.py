# Copyright 2023-2024 Geoffrey R. Scheller
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
from typing import Optional
from pythonic_fp.circulararray.auto import ca
from pythonic_fp.circulararray.fixed import caf
from pythonic_fp.containers.queues.de import DEQueue as DE
from pythonic_fp.containers.queues.de import de_queue as de
from pythonic_fp.containers.queues.fifo import FIFOQueue as FQ
from pythonic_fp.containers.queues.fifo import fifo_queue as fq
from pythonic_fp.containers.queues.lifo import LIFOQueue as LQ
from pythonic_fp.containers.queues.lifo import lifo_queue as lq
from pythonic_fp.fptools.maybe import MayBe

class TestQueueTypes:
    def test_mutate_map(self) -> None:
        de1: DE[int] = DE()
        de1.pushl(1,2,3)
        de1.pushr(1,2,3)
        de2 = de1.map(lambda x: x-1)
        assert de2.popl() == de2.popr() == MayBe(2)

        def add_one_if_int(x: int|str) -> int|str:
            if type(x) is int:
                return x+1
            else:
                return x

        fq1: FQ[int] = FQ()
        fq1.push(1,2,3)
        fq1.push(4,5,6)
        fq2 = fq1.map(lambda x: x+1)
        not_none = fq2.pop()
        assert not_none != MayBe()
        assert not_none == MayBe(2)
        assert fq2.peak_last_in() == MayBe(7) != MayBe()
        assert fq2.peak_next_out() == MayBe(3)

        lq1: LQ[MayBe[int]] = LQ()  # not really a canonical way to use MB
        lq1.push(MayBe(1), MayBe(2), MayBe(3))
        lq1.push(MayBe(4), MayBe(), MayBe(5))
        lq2 = lq1.map(lambda mb: mb.bind(lambda n: MayBe(2*n)))
        last = lq2.pop()
        assert last.get(MayBe(42)) == MayBe(10)
        pop_out = lq2.pop()
        assert pop_out == MayBe(MayBe())
        assert pop_out.get(MayBe(42)) == MayBe()
        assert lq2.peak() == MayBe(MayBe(8))
        assert lq2.peak().get(MayBe(3)) == MayBe(8)
        assert lq2.peak().get(MayBe(3)).get(42) == 8

    def test_push_then_pop(self) -> None:
        de1 = DE[int]()
        pushed_1 = 42
        de1.pushl(pushed_1)
        popped_1 = de1.popl()
        assert MayBe(pushed_1) == popped_1
        assert len(de1) == 0
        pushed_1 = 0
        de1.pushl(pushed_1)
        popped_1 = de1.popr()
        assert pushed_1 == popped_1.get(-1) == 0
        assert not de1
        pushed_1 = 0
        de1.pushr(pushed_1)
        popped_2 = de1.popl().get(1000)
        assert popped_2 != 1000
        assert pushed_1 == popped_2
        assert len(de1) == 0

        de2: DE[str] = DE()
        pushed_3 = ''
        de2.pushr(pushed_3)
        popped_3 = de2.popr().get('hello world')
        assert pushed_3 == popped_3
        assert len(de2) == 0
        de2.pushr('first')
        de2.pushr('second')
        de2.pushr('last')
        assert de2.popl() == MayBe('first')
        assert de2.popr() == MayBe('last')
        assert de2
        de2.popl()
        assert len(de2) == 0

        fq1: FQ[MayBe[int|str]] = FQ()
        fq1.push(MayBe(42))
        fq1.push(MayBe('bar'))
        assert fq1.pop().get() == MayBe(42)
        assert fq1.pop().get(MayBe('foo')).get(13) == 'bar'
        assert fq1.pop().get(MayBe('foo')).get() == 'foo'
        assert len(fq1) == 0
        fq1.push(MayBe(0))
        assert fq1.pop() == MayBe(MayBe(0))
        assert not fq1
        assert fq1.pop() == MayBe()
        assert len(fq1) == 0
        val: MayBe[int|str] = MayBe('Bob' + 'by')
        fq1.push(val)
        assert fq1
        assert val.get('Robert') == fq1.pop().get(MayBe('Bob')).get('Billy Bob') == 'Bobby'
        assert len(fq1) == 0
        assert fq1.pop().get(MayBe('Robert')) == MayBe('Robert')
        fq1.push(MayBe('first'))
        fq1.push(MayBe(2))
        fq1.push(MayBe('last'))
        fq1.map(lambda x: x.get('improbable'))
        popped = fq1.pop()
        if popped == 'impossible' or popped == 'improbable':
            assert False
        else:
            assert popped.get().get('impossible') == 'first'
        assert fq1.pop().get(MayBe()).get(-1) == 2
        assert fq1
        fq1.pop()
        assert len(fq1) == 0
        assert not fq1

        lq10: LQ[int|float|str] = LQ()
        lq10.push(42)
        lq10.push('bar')
        assert lq10.pop().get(100) == 'bar'
        assert lq10.pop().get('foo') == 42
        assert lq10.pop().get(24.0) == 24.0
        assert len(lq10) == 0
        lq10.push(0)
        assert lq10.pop() == MayBe(0)
        assert not lq10
        assert lq10.pop() == MayBe()
        assert len(lq10) == 0

        val1: int|float|complex = 1.0 + 2.0j
        val2: int|float|complex = 2
        val3: int|float|complex = 3.0
        fq11: FQ[int|float|complex] = FQ()
        lq11: LQ[int|float|complex] = LQ()
        lq11.push(val1)
        lq11.push(val2)
        lq11.push(val3)
        fq11.push(val1)
        fq11.push(val2)
        fq11.push(val3)
        assert lq11.pop().get() * lq11.pop().get() == 6.0
        assert fq11.pop().get() * fq11.pop().get() == 2.0 + 4.0j


        def is42(ii: int) -> Optional[int]:
            return None if ii == 42 else ii

        fq2: FQ[object] = FQ()
        fq3: FQ[object] = FQ()
        fq2.push(None)
        fq3.push(None)
        assert fq2 == fq3
        assert len(fq2) == 1

        barNone: tuple[int|None, ...] = (None, 1, 2, 3, None)
        bar42 = (42, 1, 2, 3, 42)
        fq4: FQ[object] = FQ(barNone)
        fq5: FQ[object] = FQ(map(is42, bar42))
        assert fq4 == fq5

        lqu1: LQ[Optional[int]] = LQ()
        lqu2: LQ[Optional[int]] = LQ()
        lqu1.push(None, 1, 2, None)
        lqu2.push(None, 1, 2, None)
        assert lqu1 == lqu2
        assert len(lqu1) == 4

        barNone = (None, 1, 2, None, 3)
        bar42 = (42, 1, 2, 42, 3)
        lqu3: LQ[Optional[int]] = LQ(barNone)
        lqu4: LQ[Optional[int]] = LQ(map(is42, bar42))
        assert lqu3 == lqu4


    def test_pushing_None(self) -> None:
        de1: DE[Optional[int]] = DE()
        de2: DE[Optional[int]] = DE()
        de1.pushr(None)
        de2.pushl(None)
        assert de1 == de2

        def is42(ii: int) -> Optional[int]:
            return None if ii == 42 else ii

        barNone = (1, 2, None, 3, None, 4)
        bar42 = (1, 2, 42, 3, 42, 4)
        de3 = DE[Optional[int]](barNone)
        de4 = DE[Optional[int]](map(is42, bar42))
        assert de3 == de4

    def test_bool_len_peak(self) -> None:
        de: DE[int] = DE()
        assert not de
        de.pushl(2,1)
        de.pushr(3)
        assert de
        assert len(de) == 3
        assert de.popl() == MayBe(1)
        assert len(de) == 2
        assert de
        assert de.peakl() == MayBe(2)
        assert de.peakr() == MayBe(3)
        assert de.popr() == MayBe(3)
        assert len(de) == 1
        assert de
        assert de.popl() == MayBe(2)
        assert len(de) == 0
        assert not de
        assert len(de) == 0
        assert not de
        de.pushr(42)
        assert len(de) == 1
        assert de
        assert de.peakl() == MayBe(42)
        assert de.peakr() == MayBe(42)
        assert de.popr() == MayBe(42)
        assert not de
        assert de.peakl() == MayBe()
        assert de.peakr() == MayBe()

        fq: FQ[int] = FQ()
        assert not fq
        fq.push(1,2,3)
        assert fq
        assert fq.peak_next_out() == MayBe(1)
        assert fq.peak_last_in() == MayBe(3)
        assert len(fq) == 3
        assert fq.pop() == MayBe(1)
        assert len(fq) == 2
        assert fq
        assert fq.pop() == MayBe(2)
        assert len(fq) == 1
        assert fq
        assert fq.pop() == MayBe(3)
        assert len(fq) == 0
        assert not fq
        assert fq.pop().get(-42) == -42
        assert len(fq) == 0
        assert not fq
        fq.push(42)
        assert fq
        assert fq.peak_next_out() == MayBe(42)
        assert fq.peak_last_in() == MayBe(42)
        assert len(fq) == 1
        assert fq
        assert fq.pop() == MayBe(42)
        assert not fq
        assert fq.peak_next_out().get(-42) == -42
        assert fq.peak_last_in().get(-42) == -42

        lq: LQ[int] = LQ()
        assert not lq
        lq.push(1,2,3)
        assert lq
        assert lq.peak() == MayBe(3)
        assert len(lq) == 3
        assert lq.pop() == MayBe(3)
        assert len(lq) == 2
        assert lq
        assert lq.pop() == MayBe(2)
        assert len(lq) == 1
        assert lq
        assert lq.pop() == MayBe(1)
        assert len(lq) == 0
        assert not lq
        assert lq.pop() == MayBe()
        assert len(lq) == 0
        assert not lq
        lq.push(42)
        assert lq
        assert lq.peak() == MayBe(42)
        assert len(lq) == 1
        assert lq
        lq.push(0)
        assert lq.peak() == MayBe(0)
        popped = lq.pop()
        assert popped.get(-1) == 0
        assert lq.peak() == MayBe(42)
        popped2 = lq.pop().get(-1)
        assert popped2 == 42
        assert not lq
        assert lq.peak() == MayBe()
        assert lq.pop() == MayBe()

    def test_iterators(self) -> None:
        data_d = caf(1, 2, 3, 4, 5)
        data_mb = data_d.map(lambda d: MayBe(d))
        de: DE[MayBe[int]] = DE(data_mb)
        ii = 0
        for item in de:
            assert data_mb[ii] == item
            ii += 1
        assert ii == 5

        de0: DE[bool] = DE()
        for _ in de0:
            assert False

        data_bool_mb: tuple[bool, ...] = ()
        de1: DE[bool] = DE(data_bool_mb)
        for _ in de1:
            assert False
        de1.pushr(True)
        de1.pushl(True)
        de1.pushr(True)
        de1.pushl(False)
        assert not de1.popl().get(True)
        while de1:
            assert de1.popl().get(False)
        assert de1.popr() == MayBe()

        def wrapMB(x: int) -> MayBe[int]:
            return MayBe(x)

        data_ca = ca(1, 2, 3, 4, 0, 6, 7, 8, 9)
        fq: FQ[MayBe[int]] = FQ(data_ca.map(wrapMB))
        assert data_ca[0] == 1
        assert data_ca[-1] == 9
        ii = 0
        for item in fq:
            assert data_ca[ii] == item.get()
            ii += 1
        assert ii == 9

        fq0: FQ[MayBe[int]] = FQ()
        for _ in fq0:
            assert False

        fq00: FQ[int] = FQ(())
        for _ in fq00:
            assert False
        assert not fq00

        data_list: list[int] = list(range(1,1001))
        lq: LQ[int] = LQ(data_list)
        ii = len(data_list) - 1
        for item_int in lq:
            assert data_list[ii] == item_int
            ii -= 1
        assert ii == -1

        lq0: LQ[int] = LQ()
        for _ in lq0:
            assert False
        assert not lq0
        assert lq0.pop() == MayBe()

        lq00: LQ[int] = LQ(*())
        for _ in lq00:
            assert False
        assert not lq00
        assert lq00.pop() == MayBe()

    def test_equality(self) -> None:
        de1: DE[object] = de(1, 2, 3, 'Forty-Two', (7, 11, 'foobar'))
        de2: DE[object] = de(2, 3, 'Forty-Two')
        de2.pushl(1)
        de2.pushr((7, 11, 'foobar'))
        assert de1 == de2

        tup = de2.popr().get(tuple(range(42)))
        assert de1 != de2

        de2.pushr((42, 'foofoo'))
        assert de1 != de2

        de1.popr()
        de1.pushr((42, 'foofoo'))
        de1.pushr(tup)
        de2.pushr(tup)
        assert de1 == de2

        holdA = de1.popl().get(0)
        holdB = de1.popl().get(0)
        holdC = de1.popr().get(0)
        de1.pushl(holdB)
        de1.pushr(holdC)
        de1.pushl(holdA)
        de1.pushl(200)
        de2.pushl(200)
        assert de1 == de2

        tup1 = 7, 11, 'foobar'
        tup2 = 42, 'foofoo'

        fq1 = fq(1, 2, 3, 'Forty-Two', tup1)
        fq2 = fq(2, 3, 'Forty-Two')
        fq2.push((7, 11, 'foobar'))
        popped = fq1.pop()
        assert popped == MayBe(1)
        assert fq1 == fq2

        fq2.push(tup2)
        assert fq1 != fq2

        fq1.push(fq1.pop(), fq1.pop(), fq1.pop())
        fq2.push(fq2.pop(), fq2.pop(), fq2.pop())
        fq2.pop()
        assert MayBe(tup2) == fq2.peak_next_out()
        assert fq1 != fq2
        assert fq1.pop() != fq2.pop()
        assert fq1 == fq2
        fq1.pop()
        assert fq1 != fq2
        fq2.pop()
        assert fq1 == fq2

        l1 = ['foofoo', 7, 11]
        l2 = ['foofoo', 42]

        lq1: LQ[object] = lq(3, 'Forty-Two', l1, 1)
        lq2: LQ[object] = lq(3, 'Forty-Two', 2)
        assert lq1.pop() == MayBe(1)
        peak = lq1.peak().get([1,2,3,4,5])
        assert peak == l1
        assert type(peak) is list
        assert peak.pop() == 11
        assert peak.pop() == 7
        peak.append(42)
        assert lq2.pop() == MayBe(2)
        lq2.push(l2)
        assert lq1 == lq2

        lq2.push(42)
        assert lq1 != lq2

        lq3: LQ[str] = LQ(map(lambda i: str(i), range(43)))
        lq4: LQ[int] = lq(*range(-1, 39), 41, 40, 39)

        lq3.push(lq3.pop().get(), lq3.pop().get(), lq3.pop().get())
        lq5 = lq4.map(lambda i: str(i+1))
        assert lq3 == lq5

    def test_map(self) -> None:
        def f1(ii: int) -> int:
            return ii*ii - 1

        def f2(ii: int) -> str:
            return str(ii)

        de0: DE[int] = de()
        de1 = de(5, 2, 3, 1, 42)
        de2 = de1.copy()
        assert de2 == de1
        assert de2 is not de1
        de0m = de0.map(f1)
        de1m = de2.map(f1)
        assert de1 == de(5, 2, 3, 1, 42)
        assert de0m == de()
        assert de1m == de(24, 3, 8, 0, 1763)
        assert de0m.map(f2) == DE()
        assert de1m.map(f2) == de('24', '3', '8', '0', '1763')

        fq0: FQ[int] = fq()
        fq1: FQ[int] = fq(5, 42, 3, 1, 2)
        q0m = fq0.map(f1)
        q1m = fq1.map(f1)
        assert q0m == fq()
        assert q1m == fq(24, 1763, 8, 0, 3)

        fq0.push(8, 9, 10)
        assert fq0.pop().get(-1) == 8
        assert fq0.pop() == MayBe(9)
        fq2 = fq0.map(f1)
        assert fq2 == fq(99)
        assert fq2 == fq(99)

        fq2.push(100)
        fq3 = fq2.map(f2)
        assert fq3 == FQ(['99', '100'])

        lq0: LQ[int] = LQ()
        lq1 = lq(5, 42, 3, 1, 2)
        lq0m = lq0.map(f1)
        lq1m = lq1.map(f1)
        assert lq0m == LQ()
        assert lq1m == lq(24, 1763, 8, 0, 3)

        lq0.push(8, 9, 10)
        assert lq0.pop() == MayBe(10)
        assert lq0.pop() == MayBe(9)
        lq2 = lq0.map(f1)
        assert lq2 == lq(63)

        lq2.push(42)
        lq3 = lq2.map(f2)
        assert lq3 == lq('63', '42')

    def test_folding(self) -> None:
        def f1(ii: int, jj: int) -> int:
            return ii + jj

        def f2l(ss: str, ii: int) -> str:
            return ss + str(ii)

        def f2r(ii: int, ss: str) -> str:
            return ss + str(ii)

        data = [1, 2, 3, 4, 5]
        de0: DE[int] = DE()
        fq0: FQ[int] = FQ()
        lq0: LQ[int] = LQ()
        
        de1: DE[int] = DE()
        fq1: FQ[int] = FQ()
        lq1: LQ[int] = LQ()

        de1.pushr(*data[1:])
        de1.pushl(data[0])
        fq1.push(*data)
        lq1.push(*data)

        assert de1.foldl(f1).get(42) == 15
        assert de1.foldr(f1).get(42) == 15
        assert fq1.fold(f1).get(42) == 15
        assert lq1.fold(f1).get(42) == 15

        assert de1.foldl(f1, 10).get(-1) == 25
        assert de1.foldr(f1, 10).get(-1) == 25
        assert fq1.fold(f1, 10).get(-1) == 25
        assert lq1.fold(f1, 10).get(-1) == 25

        assert de1.foldl(f2l, '0').get('-1') == '012345'
        assert de1.foldr(f2r, '6').get('-1') == '654321' 
        assert fq1.fold(f2l, '0').get('-1') == '012345'
        assert lq1.fold(f2l, '6').get('-1') == '654321'

        assert de0.foldl(f1).get(42) == 42
        assert de0.foldr(f1).get(42) == 42
        assert fq0.fold(f1).get(42) == 42
        assert lq0.fold(f1).get(42) == 42

        assert de0.foldl(f1, 10).get(-1) == 10
        assert de0.foldr(f1, 10).get(-1) == 10
        assert fq0.fold(f1, 10).get(-1) == 10
        assert lq0.fold(f1, 10).get(-1) == 10

        assert de0.foldl(f2l, '0').get() == '0'
        assert de0.foldr(f2r, '6').get() == '6' 
        assert fq0.fold(f2l, '0').get() == '0'
        assert lq0.fold(f2l, '6').get() == '6'

        cnt_up = fq1.fold(f2l, '0').map(lambda ss: ss + '6789')
        assert cnt_up == MayBe('0123456789')
