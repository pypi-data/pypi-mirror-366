# Copyright 2024-2025 Geoffrey R. Scheller
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

from pythonic_fp.fptools.state import State

class Test_simple:
    def test_simple_counter(self) -> None:
        sc = State(lambda s: (s+1, s+1))

        ss, aa = sc.run(0)
        assert (ss, aa) == (1, 1)

        ss, aa = sc.run(42)
        assert (ss, aa) == (43, 43)

        sc1 = sc.bind(lambda a: sc)
        ss, aa = sc1.run(0)
        assert (ss, aa) == (2, 2)

        sc2 = sc.bind(lambda a: sc)
        ss, aa = sc2.run(40)
        assert (ss, aa) == (42, 42)

        start = State.put(0)
        sc3 = start.bind(lambda a: sc)
        ss, aa = sc3.run(40)
        assert (ss, aa) == (1, 1)

        sc4 = sc.bind(lambda a: sc).bind(lambda a: sc)
        ss, aa = sc4.run(0)
        assert (ss, aa) == (3, 3)
        ss, aa = sc4.run(0)
        assert (ss, aa) == (3, 3)

        sc4 = sc4.bind(lambda a: sc1)
        ss, aa = sc4.run(5)
        assert ss == 10
        assert aa == 10

        s1, a1 = sc.run(5)
        s2, a2 = sc.run(s1)
        assert (s1, a1) == (6, 6)
        assert (s2, a2) == (7, 7)

    def test_mod3_count(self) -> None:
        m3: State[int, int] = State(lambda s: ((s+1)%3, s))

        s, a = m3.run(1)
        assert a == 1
        s, a = m3.run(s)
        assert a == 2
        s, a = m3.run(s)
        assert a == 0
        s, a = m3.run(s)
        assert a == 1
        s, a = m3.run(s)
        assert a == 2

    def test_countdown(self) -> None:
        def cntdn(a: int) -> State[int, int]:
            if a == 0:
                return State(lambda a: (6, 6))
            else:
                return State(lambda a: (a-1, a-1))

        start: State[int, int] = State.unit(100)
        assert 100 == start.eval(42)
        countdown: State[int, int] = start.bind(cntdn)
        assert countdown.eval(5) == 4
        assert countdown.eval(100) == 99
        countdown = countdown.bind(cntdn).bind(cntdn)
        assert countdown.eval(5) == 2
        assert countdown.eval(100) == 97
        countdown = countdown.bind(cntdn)
        assert countdown.eval(5) == 1
        countdown = countdown.bind(cntdn)
        assert countdown.eval(5) == 0
        countdown = countdown.bind(cntdn)
        assert countdown.eval(5) == 6
        assert countdown.eval(6) == 0
        assert countdown.eval(4) == 5

    def test_modify(self) -> None:
        def square(n1: int) -> int:
            return n1*n1

        count: State[int, int] = State(lambda s: (s, s+1))

        def cnt(a: int) -> State[int, int]:
            return State(lambda s: (s, s+1))

        def sqr_st(a: tuple[()]) -> State[int, tuple[()]]:
            return State.modify(square)

        do_it = count.bind(cnt).bind(cnt).bind(sqr_st).bind(cnt).bind(sqr_st).bind(cnt)
        a, s = do_it.run(0)
        assert (a, s) == (100, 101)

    def test_get(self) -> None:
        get_sa: State[object, object] = State.get()
        t = get_sa.run('foo')
        assert (t[0], t[1]) == ('foo', 'foo')

    def test_put(self) -> None:
        put_sa: State[object, tuple[()]] = State.put('bar')
        t = put_sa.run('foo')
        assert (t[0], t[1]) == ((), 'bar')

    def test_map(self) -> None:
        sa0: State[int, int] = State(lambda s: (1, s))
        sa1 = sa0.map(lambda n: n*4)
        n, s = sa0.run(21)
        assert (n, s) == (1, 21)
        n, s = sa1.run(21)
        assert (n, s) == (4, 21)
        sa2: State[int, int] = sa1.get().map(lambda n: 2*n)
        n, s = sa2.run(21)
        assert (n, s) == (42, 21)

    def test_map2(self) -> None:
        sa20: State[int, int] = State(lambda s: (20, s))
        sa11: State[int, int] = State(lambda s: (11, s))
        sa42 = sa20.map2(sa11, lambda x, y: x+2*y)
        n, s = sa42.run(0)
        assert (n, s) == (42, 0)

    def test_sequence(self) -> None:
        sa1 = State(lambda s: (str(s), s+1))
        sa2 = State(lambda s: (str(s), s+2))
        sa3 = State(lambda s: (str(s), s+3))
        sa4 = State(lambda s: (str(s), s+4))
        sas = [sa1, sa2, sa3, sa4]
        sal = State.sequence(sas)
        ll, ss = sal.run(0)
        assert ss == 10
        assert ll == ["0", "1", "3", "6"]

        sa1 = State(lambda s: (str(1), s))
        sa2 = State(lambda s: (str(2), s))
        sa3 = State(lambda s: (str(3), s))
        sa4 = State(lambda s: (str(4), s))
        sas = [sa1, sa2, sa3, sa4]
        sal = State.sequence(sas)
        ll, ss = sal.run(0)
        assert ss == 0
        assert ll == ["1", "2", "3", "4"]
