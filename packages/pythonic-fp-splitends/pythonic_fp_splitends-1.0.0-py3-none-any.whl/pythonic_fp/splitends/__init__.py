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

"""Mutable stack objects that can safely share data.

Python package Implementing a singularly linked LIFO queue
called a ``SplitEnd``. These data structures can safely share
data nodes between themselves.

- each ``SplitEnd`` is a very simple stateful (mutable) LIFO stack
- data can be "extended" to or "snipped" off of the end (tip)
- the "root" value of a ``SplitEnd`` is fixed and cannot be "snipped"
- different mutable split ends can safely share the same "tail"
- each ``SplitEnd`` sees itself as a singularly linked list
- bush-like datastructures can be formed using multiple ``SplitEnds``
- the ``SplitEnd`` copy method and ``len`` are O(1)
- in boolean context returns true if the ``SplitEnd`` is not just a "root"

"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2023-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
