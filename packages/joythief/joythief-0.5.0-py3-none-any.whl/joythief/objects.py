"""Matchers for general object types."""

import typing as tp

from joythief.core import Matcher

T = tp.TypeVar("T")

Type = tp.Union[type[T], tuple[type[T], ...]]


class Anything(Matcher[T]):
    """Matches anything at all.

    .. versionadded:: 0.5.0

    The JoyThief version of :py:data:`unittest.mock.ANY`.

    """

    def compare(self, _: tp.Any) -> bool:
        return True

    def represent(self) -> str:
        return super().represent()


class InstanceOf(Matcher[T]):
    """Matches any instance of the specified type(s).

    This matcher compares the received value using
    :py:func:`isinstance`, so accepts either a single type or a tuple
    of types. With :code:`nullable` set to :py:const:`True`, the
    received value can also be :py:const:`None`.

    Originally formulated for `this answer`_.

    .. _this answer: https://stackoverflow.com/a/64973325/3001761

    """

    _nullable: bool
    _type: Type[T]

    def __init__(self, type_: Type[T], *, nullable: bool = False):
        super().__init__()
        self._nullable = nullable
        self._type = type_

    def compare(self, other: tp.Any) -> bool:
        type_: tuple[type[tp.Any], ...] = (
            self._type if isinstance(self._type, tuple) else (self._type,)
        )
        if self._nullable:
            type_ = type_ + (type(None),)
        return isinstance(other, type_)

    def represent(self) -> str:
        return (
            f"InstanceOf({self._type!r}"
            f"{', nullable=True' if self._nullable else ''})"
        )
