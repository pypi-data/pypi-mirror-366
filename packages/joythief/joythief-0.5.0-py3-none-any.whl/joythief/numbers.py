"""Matchers for `numeric types`_ (e.g. :py:class:`float`).

.. _numeric types: https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex

"""

import math
import typing as tp
from numbers import Real

from joythief.core import Matcher


class NaN(Matcher[Real]):
    """Matches any :py:class:`float` instance representing NaN.

    `IEEE 754`_ NaN (*"not a number"*) instances are, by definition, not
    equal to each other. This matcher compares equal to e.g.
    :py:data:`math.nan` or :code:`float("nan")` using
    :py:func:`math.isnan`.

    Originally formulated for `this answer`_.

    .. _IEEE 754: https://en.wikipedia.org/wiki/IEEE_754
    .. _this answer: https://stackoverflow.com/a/79699116/3001761

    """

    def compare(self, other: tp.Any) -> bool:
        if not isinstance(other, Real):
            return tp.cast(bool, NotImplemented)
        return math.isnan(other)

    def represent(self) -> str:
        return super().represent()
