# PyPI Pythonic FP Namespace Projects

Collection of Functional Programming (FP) oriented Python libraries.
While taking a functional programming approach, these packages endeavor
to remain Pythonic.

Pythonic FP is a hobby project, but the maintainer is serious about its quality.

## Pythonic FP

The overall project's name is **Pythonic FP** and consists of PyPI Python projects
all under the `pythonic-fp` namespace.

| Name | PyPI | GitHub | Docs | Python Package |
|:---- |:----:|:------:|:----:|:-------------- |
| Gadgets | [pythonic-fp][100] | [gh][200] | [gh_pages][300] |  pythonic_f.gadgets |
| Circular Array | [pythonic-fp-circulararray][101] | [gh][201] | [gh_pages][301] |  pythonic_f.circulararray |
| Containers | [pythonic-fp-containers][102] | [gh][202] | [gh_pages][302] |  pythonic_f.containers |
| FP Tools | [pythonic-fp-fptools][103] | [gh][203] | [gh_pages][303] |  pythonic_f.fptools |
| Iterables | [pythonic-fp-iterables][104] | [gh][204] | [gh_pages][304] |  pythonic_f.iterables |
| Splitends | [pythonic-fp-splitends][105] | [gh][205] | [gh_pages][305] |  pythonic_f.splitends |

## Namespace Projects

### Pythonic Functional Programming: pythonic-fp

The PyPI `pythonic-fp` project has three purposes. The first is to claim
the project name `pythonic-fp` on PyPI. The second is to host the python
package `pythonic_fp.gadgets`. The third is to host the Sphinx
based documentation on GH-Pages for all the pythonic-fp namespace
projects.

The gadgets package is intended for **simple tools** with minimal
dependencies that may have multiple locations, or no good location,
to where they can go.

This project is now installable, but is not necessarily required to use
other `pythonic_fp` namespace packages.

______________________________________________________________________

### Circular Array: pythonic-fp-circulararray

Stateful circular array data structures each with

- O(1) pops either end
- comparisons compare identity before equality, like builtins
- in boolean context returns true when not empty, false when empty
- iterable and reverse iterable, can safely be mutated
  - while previous iterators leisurely iterate over their previous state

Two types

- fixed storage capacity
  - O(1) pushes either end
  - O(1) indexing, does not support slicing
- variable storage capacity
  - O(1) amortized pushes either end
  - O(1) indexing, fully supports slicing
  - Auto-resizing larger storage capacity when necessary
  - manually compatible

______________________________________________________________________

### Containers: pythonic-fp-containers

Python package of container like data structures.

- **FTuple:** tuple-like object with a more FP interface
- **IList:** immutable list where hashability is enforced at runtime

______________________________________________________________________

### FP Tools: pythonic-fp-fptools

A Functional programming library for Python.

This library implements tools to aid in Python functional programming
in a way which endeavors to remain Pythonic.

______________________________________________________________________

### pythonic-fp-iterables

Tools for creating iterators from iterables.

- Concatenating and merging iterables
- Dropping and taking values from iterables
- Reducing and accumulating iterables

______________________________________________________________________

### pythonic-fp-singletons

Singleton classes representing

- missing values (actually missing, not potentially missing)
- sentinel values
- failed calculations

Also a class to implement subtypeable Boolean values.

- Python bool cannot be subclassed, this one can

______________________________________________________________________

### pythonic-fp-splitends

The splitends package implements a singularly linked LIFO queue called
a ``SplitEnd``. These data structures can safely share data nodes
between themselves and form branching *hair-like* data structures.

______________________________________________________________________

[100]: https://pypi.org/project/pythonic-fp
[101]: https://pypi.org/project/pythonic-fp-circulararray
[102]: https://pypi.org/project/pythonic-fp-containers
[103]: https://pypi.org/project/pythonic-fp-fptools
[104]: https://pypi.org/project/pythonic-fp-iterables
[105]: https://pypi.org/project/pythonic-fp-splitends
[200]: https://github.com/grscheller/pythonic-fp
[201]: https://github.com/grscheller/pythonic-fp-circulararray
[202]: https://github.com/grscheller/pythonic-fp-containers
[203]: https://github.com/grscheller/pythonic-fp-fptools
[204]: https://github.com/grscheller/pythonic-fp-iterables
[205]: https://github.com/grscheller/pythonic-fp-splitends
[300]: https://grscheller.github.io/pythonic-fp/gadgets/development/build/html
[301]: https://grscheller.github.io/pythonic-fp/circulararray/development/build/html
[302]: https://grscheller.github.io/pythonic-fp/containers/development/build/html
[303]: https://grscheller.github.io/pythonic-fp/fptools/development/build/html
[304]: https://grscheller.github.io/pythonic-fp/iterables/development/build/html
[305]: https://grscheller.github.io/pythonic-fp/splitends/development/build/html
