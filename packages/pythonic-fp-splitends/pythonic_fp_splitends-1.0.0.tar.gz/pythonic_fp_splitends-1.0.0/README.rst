Pythonic FP - SplitEnds
=======================

PyPI project
`pythonic-fp.splitends <https://pypi.org/project/pythonic-fp.splitends/>`_.

Python package Implementing a singularly linked LIFO queue called
a ``SplitEnd``. These data structures can safely share data nodes
between themselves.

- each ``SplitEnd`` is a very simple stateful (mutable) LIFO stack
- data can be "extended" to or "snipped" off of the end (tip)
- the "root" value of a ``SplitEnd`` is fixed and cannot be "snipped"
- different mutable split ends can safely share the same "tail"
- each ``SplitEnd`` sees itself as a singularly linked list
- bush-like datastructures can be formed using multiple ``SplitEnds``
- the ``SplitEnd`` copy method and ``len`` are O(1)
- in boolean context returns true if the ``SplitEnd`` is not just a "root"

This PyPI project is part of of the grscheller
`pythonic-fp namespace projects <https://github.com/grscheller/pythonic-fp/blob/main/README.md>`_

**Warning:** This PyPI project is Alpha level software and subject to
change.

Documentation
-------------

Documentation for this project is hosted on
`GitHub Pages
<https://grscheller.github.io/pythonic-fp/splitends/development/build/html>`_.

Copyright and License
---------------------

Copyright (c) 2023-2025 Geoffrey R. Scheller. Licensed under the Apache
License, Version 2.0. See the LICENSE file for details.
