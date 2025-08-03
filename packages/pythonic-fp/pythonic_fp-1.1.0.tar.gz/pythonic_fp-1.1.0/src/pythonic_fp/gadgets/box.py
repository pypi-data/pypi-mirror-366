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

"""Class for a stateful container that can hold at most one item."""

from __future__ import annotations

__all__ = ['Box']

from collections.abc import Callable, Iterator
from typing import cast, Final, Never, overload, TypeVar
from pythonic_fp.singletons.sentinel import Sentinel

D = TypeVar('D')

_sentinel: Final[Sentinel] = Sentinel('Box')

class Box[D]:
    """Container holding at most one item of a given type

    - where ``Box(item)`` contains at most one item of type ``D``

      - ``Box[T]()`` creates empty container

        - where ``T`` is some definite type
        - which could be ``None`` or even ``Never``

    - Box objects can be used in Python ``match`` statements

    """
    __slots__ = ('_item',)
    __match_args__ = ('_item',)

    T = TypeVar('T')

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: D) -> None: ...

    def __init__(self, value: D | Sentinel = Sentinel('Box')) -> None:
        """Initialize Box with an "optional" initial value.

           :param value: an "optional" initial value for Box.

        """
        self._item: D | Sentinel = value

    def __bool__(self) -> bool:
        return self._item is not Sentinel('Box')

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._item)

    def __repr__(self) -> str:
        if self:
            return 'Box(' + repr(self._item) + ')'
        return 'Box()'

    def __len__(self) -> int:
        return 1 if self else 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._item is other._item:
            return True
        if self._item == other._item:
            return True
        return False

    @overload
    def get(self) -> D | Never: ...
    @overload
    def get(self, alt: D) -> D: ...

    def get(self, alt: D | Sentinel = Sentinel('Box')) -> D | Never:
        """Return the contained value if it exists, otherwise an alternate value.

        :param alt: an "optional" value to return if Box is empty
        :return: contents of Box, or an alternate value if given and Box empty
        :raises ValueError: when an alt value is not provided but needed

        """
        if self._item is not _sentinel:
            return cast(D, self._item)
        if alt is _sentinel:
            msg = 'Box: get from empty Box with no alternate return value provided'
            raise ValueError(msg)
        return cast(D, alt)

    def pop(self) -> D | Never:
        """Pop the value if Box is not empty.

        :return: value contained in Box
        :raises ValueError: if Box is empty

        """
        if self._item is _sentinel:
            msg = 'Box: Trying to pop an item from an empty Box'
            raise ValueError(msg)
        popped = cast(D, self._item)
        self._item = _sentinel
        return popped

    def push(self, item: D) -> None | Never:
        """Push an item in an empty Box.

        :raises ValueError: if Box is not empty

        """
        if self._item is Sentinel('Box'):
            self._item = item
        else:
            msg = 'Box: Trying to push an item in a non-empty Box'
            raise ValueError(msg)
        return None

    def put(self, item: D) -> None:
        """Put an item in the Box. Discard any previous contents."""
        self._item = item

    def exchange(self, new_item: D) -> D | Never:
        """Exchange an item with what is in the Box.

        :raises ValueError: if Box is empty

        """
        if self._item is _sentinel:
            msg = 'Box: Trying to exchange items from an empty Box'
            raise ValueError(msg)
        popped = cast(D, self._item)
        self._item = new_item
        return popped

    def map[T](self, f: Callable[[D], T]) -> Box[T]:
        """Map function ``f`` over contents. We need to return a new
        instance since the type of Box can change.

        :param f: mapping function
        :return: a new instance

        """
        if self._item is Sentinel('Box'):
            return Box()
        return Box(f(cast(D, self._item)))

    def bind[T](self, f: Callable[[D], Box[T]]) -> Box[T]:
        """Flatmap ``Box`` with function ``f``.

        :param f: binding function
        :return: a new instance

        """
        if self._item is _sentinel:
            return Box()
        return f(cast(D, self._item))
