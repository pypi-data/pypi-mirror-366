from __future__ import annotations

import typing as tp
from abc import ABC, abstractmethod
from enum import Enum, auto

if tp.TYPE_CHECKING:
    from typing_extensions import TypeAlias

T = tp.TypeVar("T")


class _MatcherState(Enum):
    UNCOMPARED = auto()
    EQUAL_ONCE = auto()
    OTHER = auto()


class Matcher(tp.Generic[T], ABC):
    """Abstract base class for all other matchers.

    Defines the core requirements for any matcher:

    - Must be `comparable for equality`_ with anything.
    - Must have a sensible `representation`_.

    As ``__eq__`` and ``__repr__`` are defined in
    :py:class:`~joythief.core.Matcher` itself, to provide core matcher
    behaviour, this abstract base class defines two equivalent abstract methods:
    :py:meth:`~joythief.core.Matcher.compare` and
    :py:meth:`~joythief.core.Matcher.represent`. You can write custom matchers
    by implementing these methods:

    .. code-block:: python

        import typing as tp

        from joythief.core import Matcher


        class IsWelcoming(Matcher[str]):

            def compare(self, other: tp.Any) -> bool:
                return other == "hello, world"

            def represent(self) -> str:
                return super().represent()  # 'IsWelcoming()'

    .. _comparable for equality: https://docs.python.org/3/reference/datamodel.html#object.__eq__
    .. _representation: https://docs.python.org/3/reference/datamodel.html#object.__repr__
    """

    __PLACEHOLDER = object()

    _equal_to: tp.Any
    _state: _MatcherState

    def __init__(self) -> None:
        self._equal_to = self.__PLACEHOLDER
        self._state = _MatcherState.UNCOMPARED

    def __eq__(self, other: tp.Any) -> bool:
        result = self.compare(other)
        if result is NotImplemented:
            return result
        if self._state == _MatcherState.UNCOMPARED and result:
            self._state = _MatcherState.EQUAL_ONCE
            self._equal_to = other
        elif other is not self._equal_to:
            self._equal_to = self.__PLACEHOLDER
            self._state = _MatcherState.OTHER
        return result

    def __repr__(self) -> str:
        if self._state == _MatcherState.EQUAL_ONCE:
            return repr(self._equal_to)
        return self.represent()

    @abstractmethod
    def compare(self, other: tp.Any) -> bool:
        """Equivalent to  `__eq__`__.

        .. __: https://docs.python.org/3/reference/datamodel.html#object.__eq__
        """
        raise NotImplementedError

    @abstractmethod
    def represent(self) -> str:
        """Equivalent to `__repr__`__.

        .. __: https://docs.python.org/3/reference/datamodel.html#object.__repr__
        """
        return f"{type(self).__name__}()"


MaybeMatcher: TypeAlias = tp.Union[T, Matcher[T]]
"""Either ``T`` or a matcher of ``T``."""
