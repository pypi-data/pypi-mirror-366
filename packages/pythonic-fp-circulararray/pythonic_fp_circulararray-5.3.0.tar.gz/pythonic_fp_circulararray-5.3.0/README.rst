PPythonic FP - Circular Array
=============================

PyPI project
`pythonic-fp.circulararray
<https://pypi.org/project/pythonic-fp.circulararray>`_.

Python module implementing stateful circular array data structures.

- O(1) pops either end 
- O(1) amortized pushes either end 
- O(1) indexing, fully supports slicing
- Auto-resizing larger when necessary, manually compatible
- iterable, can safely mutate while iterators continue iterating over previous state
- comparisons compare identity before equality, like builtins
- in boolean context returns true when not empty, false when empty

This PyPI project is part of of the grscheller
`pythonic-fp namespace projects
<https://github.com/grscheller/pythonic-fp/blob/main/README.md>`_

Documentation
-------------

Documentation for this project is hosted on
`GitHub Pages
<https://grscheller.github.io/pythonic-fp/circulararray/development/build/html>`_.

Copyright and License
---------------------

Copyright (c) 2023-2025 Geoffrey R. Scheller. Licensed under the Apache
License, Version 2.0. See the LICENSE file for details.
