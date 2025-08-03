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
from pythonic_fp.splitends.splitend import SplitEnd as SE
from pythonic_fp.iterables.merging import concat

class Test_SplitEnds:
    def test_mutate_returns_none(self) -> None:
        ps = SE(41)
        assert ps.extend(1,2,3) is None  # type: ignore[func-returns-value]

    def test_wxtend_then_snip(self) -> None:
        s1 = SE(42)
        pushed = 21
        s1.extend(pushed)
        popped = s1.snip()
        assert pushed == popped == 21

    def test_pop_from_one_element_splitend(self) -> None:
        s1 = SE[int](42)
        try:
            assert s1.snip() == 42
            assert s1.snip() == 42
        except ValueError:
            assert False
        else:
            assert len(s1) == 1

    def test_splitend_extend_snip(self) -> None:
        s1 = SE(101)
        s2 = SE(*range(0,2000))

        assert len(s1) == 1
        assert len(s2) == 2000
        s1.extend(42)
        assert s2.snip() == 1999
        assert s2.snip() == 1998
        assert len(s1) == 2
        assert len(s2) == 1998
        assert s1.snip() == 42
        assert s1.snip() == 101     # re-rooted
        s1.extend(12, 13, 14)
        assert len(s1) == 4
        assert s1.snip() == 14
        assert s1.snip() == 13
        assert len(s1) == 2
        assert s1.snip() == 12
        assert len(s1) == 1
        assert s1.snip() == 101
        assert len(s1) == 1
        assert s1.snip() == 101
        assert len(s1) == 1


    def test_SplitEnd_len(self) -> None:
        s1: SE[int|None] = SE(None)
        s2: SE[int|None] = SE(None, 42)

        assert len(s1) == 1
        if s1:
            assert True

        assert len(s1) == 1
        assert s1.snip() is None
        assert len(s1) == 1
        assert s1.snip() is None
        assert len(s1) == 1
        assert len(s2) == 2
        assert s2.snip() == 42
        assert len(s2) == 1
        assert s2.snip() is None
        assert len(s2) == 1
        assert s2.snip() is None
        assert len(s2) == 1

        s2001: SE[int] = SE(*range(1,2001))
        if s2001:
            assert len(s2001) == 2000
        else:
            assert False

        s3 = s2001.copy()
        assert len(s3) == 2000
        assert s3 == s2001
        assert s3.snip() == 2000
        assert s3.snip() == 1999
        assert s3 != s2001
        assert s2001.snip() == 2000
        assert s2001.snip() == 1999
        assert s2001.snip() == 1998
        assert s3 != s2001
        assert s3.snip() == 1998
        assert s3 == s2001
        assert s2001.peak() == 1997
        assert len(s3) == 1997
        assert len(s2001) == 1997

    def test_iteration(self) -> None:
        giantSplitEnd: SE[str] = SE(' Fum', ' Fo', ' Fi', 'Fe')
        giantTalk = giantSplitEnd.snip()
        assert giantTalk == "Fe"
        for giantWord in giantSplitEnd:
            giantTalk += giantWord
        assert len(giantSplitEnd) == 3
        assert giantTalk == 'Fe Fi Fo Fum'

        gSE = giantSplitEnd.copy()
        for ff in gSE:
            assert ff[0] in {' ', 'F'}

    def test_equality(self) -> None:
        s1 = SE(*range(3))
        s2 = s1.copy()
        s2.extend(42)
        assert s1 is not s2
        assert s1 != s2
        assert s2.snip() == 42
        assert s1 == s2
        assert s2 is not s1
        assert s2.peak() == 2

        s3 = SE(*range(1, 10001))
        s4 = s3.copy()
        assert s3 is not s4
        assert s3 == s4

        s3.extend(s4.snip())
        assert s3.snip() == 10000
        assert s3.snip() == 10000
        assert s3 == s4
        assert s3 is not s4

        s5 = SE(1,2,3,4)
        s6 = SE(1,2,3,42)
        assert s5 != s6
        for ii in range(10):
            s5.extend(ii)
            s6.extend(ii)
        assert s5 != s6

        ducks: tuple[str, ...] = ("Huey", "Dewey")
        s7 = SE((), ducks)
        s8 = SE((), ducks)
        s9 = s8.copy()
        s9.extend(("Huey", "Dewey", "Louie"))
        assert s7 == s8
        assert s7 != s9
        assert s7.peak() == s8.peak()
        assert s7.peak() != s9.peak()
        ducks = ducks + ("Louie",)
        s7.extend(ducks)
        assert s7 != s8
        assert s7 == s9
        stouges = ('Moe', 'Larry', 'Curlie')
        s7.extend(stouges)
        assert s7 != s9
        s9.extend(('Moe', 'Larry', 'Curlie'))
        assert s7 == s9
        assert s7 is not s9
        assert s7.peak() == s9.peak()

    def test_storing_Nones(self) -> None:
        s0: SE[int|None] = SE(100)
        s0.extend(None)
        s0.extend(42)
        s0.extend(None)
        s0.extend(42)
        s0.extend(None)
        assert len(s0) == 6
        while s0:
            assert s0
            s0.snip()
        assert not s0

        s1: SE[int|None] = SE(None)
        s1.extend(24)
        s2 = s1.copy()
        s2.extend(42)
        s1.extend(42)
        assert s1 == s2
        assert len(s1) == len(s2) == 3
        s3 = s2.copy()
        s3.extend(None)
        assert s3.peak() is None
        assert s3
        assert len(s3) == 4
        assert s3.snip() is None
        assert s3.snip() == 42
        assert s3.snip() == 24
        assert s3.snip() is None
        assert len(s3) == 1
        s3.extend(42)
        s4 = SE(None, 42)
        assert s3 == s4

    def test_reversing(self) -> None:
        s1 = SE('a', 'b', 'c', 'd')
        s2 = SE('d', 'c', 'b', 'a')
        assert s1 != s2
        assert s2 == SE(*iter(s1))
        s0 = SE('z')
        assert s0 == SE(*iter(s0))
        s3 = SE(*concat(iter(range(1, 100)), iter(range(98, 0, -1))))
        s4 = SE(*s3)
        assert s3 == s4
        assert s3 is not s4

    def test_reversed(self) -> None:
        lf = [1.0, 2.0, 3.0, 4.0]
        lr = [4.0, 3.0, 2.0, 1.0]
        s1: SE[float] = SE(*lr)
        l_s1 = list(s1)
        l_r_s1 = list(reversed(s1))
        assert lf == l_s1
        assert lr == l_r_s1
        s2 = SE(*lf)
        for x in s2:
            assert x == lf.pop()
        assert len(lf) == 0       # test iteration gets all values
        assert len(s2) == 4       # s2 not consumed

    def test_fold(self) -> None:
        def cat_str(s1: str, s2: str) -> str:
            return s1 + s2

        def cat_ord(s1: str, s2: int) -> str:
            return s1 + chr(s2)

        se_str = SE('b', 'c', 'd', 'e')
        se_ord = SE(98, 99, 100, 101)

        assert se_str.fold(cat_str) == 'edcb'
        assert se_str.rev_fold(cat_str) == 'bcde'
        assert se_str.fold(cat_str, 'f') == 'fedcb'
        assert se_str.rev_fold(cat_str, 'a' ) == 'abcde'

        assert se_ord.fold(cat_ord, 'f') == 'fedcb'
        assert se_ord.rev_fold(cat_ord, 'a' ) == 'abcde'
