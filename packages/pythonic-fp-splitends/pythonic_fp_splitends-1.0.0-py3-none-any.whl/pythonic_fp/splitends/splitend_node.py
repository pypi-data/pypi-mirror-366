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

"""Data node class used privately by class SplitEnd.

Node classes used to make bush-like graphs. API made public since it
might prove useful to someone designing other data structures similar
to a ``splitend``.

"""
from __future__ import annotations
from collections.abc import Callable, Hashable, Iterator
from typing import cast, TypeVar
from pythonic_fp.fptools.maybe import MayBe

__all__ = ['SENode']

D = TypeVar('D', bound=Hashable)


class SENode[D]:
    """Data node for class SplitEnd

    - hashable data node for a end-to-root singularly linked list.
    - designed so multiple splitends can safely share the same data

    - two nodes compare as equal if

      - both their previous Nodes are the same
      - their data compare as equal

    - more than one node can point to the same proceeding node

      - forming bush like graphs

    """

    __slots__ = '_data', '_prev'

    def __init__(self, data: D, prev: SENode[D] | None = None) -> None:
        """
        :param data: nodes always contain data of type D
        :param prev: potential link to a previous node

        """
        self._data: D = data
        self._prev: MayBe[SENode[D]] = MayBe(prev) if prev is not None else MayBe()

    def __iter__(self) -> Iterator[D]:
        node = self
        while node:
            yield node._data
            node = node._prev.get()
        yield node._data

    def __bool__(self) -> bool:
        return self._prev != MayBe()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._prev != other._prev:
            return False
        if self._data == other._data:
            return True
        return False

    def peak(self) -> D:
        """Return contained data"""
        return self._data

    def pop2(self) -> tuple[D, SENode[D]]:
        """Return the data at the tip and the tail of the senode."""
        if self._prev:
            return self._data, self._prev.get()
        return self._data, self

    def push(self, data: D) -> SENode[D]:
        """Push data onto the queue and return a new node containing the data."""
        return SENode(data, self)

    def fold[T](
            self,
            f: Callable[[T, D], T],
            init: T | None = None
        ) -> T:
        """Fold data across linked nodes with a function..

        .. code:: python

            def fold[T](
                    self,
                    f: Callable([T, D], T],
                    init: T | None = None
            ) -> T

        :param f: folding function, first argument is for accumulated value
        :param init: optional initial starting value for the fold
        :return: reduced value folding from end to root in natural LIFO order

        """
        if init is None:
            acc: T = cast(T, self._data)
            node = self._prev.get()
        else:
            acc = init
            node = self

        while node:
            acc = f(acc, node._data)
            node = node._prev.get()
        acc = f(acc, node._data)
        return acc
