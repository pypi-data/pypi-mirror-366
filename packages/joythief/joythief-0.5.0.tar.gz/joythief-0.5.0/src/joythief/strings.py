"""Matchers for the `text sequence type`_ (:py:class:`str`).

.. _text sequence type: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
"""

import json
import re
import typing as tp
from collections.abc import Mapping, Sequence
from urllib.parse import parse_qs, urlparse

from joythief.core import Matcher, MaybeMatcher


class JsonString(Matcher[str]):
    """Matches any :py:class:`str` instance representing JSON.

    :param expected: What the result of parsing the JSON should be.
      If omitted, any valid JSON string is matched.

    """

    __ANYTHING = object()

    _expected: tp.Any

    def __init__(self, expected: tp.Any = __ANYTHING):
        super().__init__()
        self._expected = expected

    def compare(self, other: tp.Any) -> bool:
        if not isinstance(other, str):
            return tp.cast(bool, NotImplemented)
        try:
            parsed = json.loads(other)
        except json.decoder.JSONDecodeError:
            return False
        return self._expected is self.__ANYTHING or parsed == self._expected

    def represent(self) -> str:
        if self._expected is self.__ANYTHING:
            return super().represent()
        return f"JsonString({self._expected!r})"


class StringMatching(Matcher[str]):
    """Matches any :py:class:`str` instance matching a regular expression.

    :param pattern: Regex pattern to match, as a string or compiled pattern.

    :param flags: Any `flags`_ to compile a :py:class:`str` pattern with

    :raises ValueError: if flags are provided with a pre-compiled pattern.

    .. _flags: https://docs.python.org/3/library/re.html#flags

    """

    _pattern: re.Pattern[str]

    @classmethod
    def iso8601(cls) -> Matcher[str]:
        """Create a matcher for strings representing `ISO 8601`_ timestamps.

        .. versionadded:: 0.4.0

        Matches the ``%Y-%m-%dT%H:%M:%S.%f`` format as created by e.g.
        :py:meth:`datetime.datetime.isoformat`:

        .. code-block:: python

            '2025-07-22T14:16:48.708298'

        **Note** the match is only on structure, it does not attempt to validate
        the actual datetime represented by the string.

        .. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
        """
        date = r"\d{4}-\d{2}-\d{2}"
        time = r"\d{2}:\d{2}:\d{2}(?:.\d{3,6})?"
        offset = r"[+\-]\d{2}:?\d{2}|Z"
        return StringMatching(
            rf"^{date}[T ]{time}(?:{offset})?$",
            flags=re.IGNORECASE,
        )

    @classmethod
    def uuid(cls) -> Matcher[str]:
        """Create a matcher for strings representing `UUIDs`_.

        .. versionadded:: 0.4.0

        Matches the 8-4-4-4-12 hexadecimal format as created by e.g.
        stringifying :py:class:`~uuid.UUID`:

        .. code-block:: python

            '36962eb6-d198-4661-9d97-437796e5146b'

        .. _UUIDs: https://en.wikipedia.org/wiki/Universally_unique_identifier
        """
        return cls(
            r"^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$",
            flags=re.IGNORECASE,
        )

    @tp.overload
    def __init__(self, pattern: re.Pattern[str]): ...

    @tp.overload
    def __init__(self, pattern: str, *, flags: int = 0): ...

    def __init__(
        self,
        pattern: tp.Union[str, re.Pattern[str]],
        *,
        flags: int = 0,
    ):
        super().__init__()
        self._pattern = re.compile(pattern, flags=flags)

    def compare(self, other: tp.Any) -> bool:
        if not isinstance(other, str):
            return tp.cast(bool, NotImplemented)
        return self._pattern.match(other) is not None

    def represent(self) -> str:
        return f"StringMatching({self._pattern!r})"


class UrlString(Matcher[str]):
    """Matches any :py:class:`str` instance representing a URL.

    The string is parsed with :py:func:`~urllib.parse.urlparse` and
    compared attribute-by-attribute.
    Any attributes not provided are ignored.

    :param scheme: the scheme (e.g. ``"https"``)
    :param hostname: the hostname (e.g. ``"example.com"``)
    :param path: the path (e.g. ``"/some/path"``)
    :param query: the result of parsing the query string with
      :py:func:`~urllib.parse.parse_qs`

    :raises TypeError: if no arguments are provided.

    """

    _hostname: tp.Optional[MaybeMatcher[str]]
    _path: tp.Optional[MaybeMatcher[str]]
    _query: tp.Optional[Mapping[str, Sequence[str]]]
    _scheme: tp.Optional[MaybeMatcher[str]]

    def __init__(
        self,
        *,
        scheme: tp.Optional[MaybeMatcher[str]] = None,
        hostname: tp.Optional[MaybeMatcher[str]] = None,
        path: tp.Optional[MaybeMatcher[str]] = None,
        query: tp.Optional[Mapping[str, Sequence[str]]] = None,
    ):
        super().__init__()
        self._hostname = hostname
        self._path = path
        self._query = query
        self._scheme = scheme
        if all(
            getattr(self, attr) is None
            for attr in ["_hostname", "_path", "_query", "_scheme"]
        ):
            raise TypeError("A UrlString with no arguments matches any string")

    def compare(self, other: tp.Any) -> bool:
        if not isinstance(other, str):
            return tp.cast(bool, NotImplemented)
        parsed = urlparse(other)
        for attribute in ["hostname", "path", "scheme"]:
            if (expected := getattr(self, f"_{attribute}")) is not None and getattr(
                parsed, attribute
            ) != expected:
                return False
        if (expected := self._query) is not None and parse_qs(
            parsed.query, keep_blank_values=True
        ) != expected:
            return False
        return True

    def represent(self) -> str:
        parameters = [
            f"{name}={value!r}"
            for name in ["scheme", "hostname", "path", "query"]
            if (value := getattr(self, f"_{name}")) is not None
        ]
        return f"UrlString({', '.join(parameters)})"
