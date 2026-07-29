"""strview.py
"""

from collections.abc import Iterable
import string
import sys
import typing
from typing import Any, Callable, SupportsIndex, Self


class StrView:

    __slots__ = ('_data', '_start', '_length')

    def __init__(
        self,
        data: str | Self,
        *,
        start: int = 0,
        length: int | None = None,
    ) -> None:
        if isinstance(data, str):
            self._data: str = str(data)
            self._start: int = int(start)
            if length is None:
                length = len(self.data) - self.start
            self._length: int = int(length)
        elif isinstance(data, self.__class__):
            self._data: str = data.data
            self._start: int = data.start + int(start)
            if length is None:
                length = data.length - (self.start - data.start)
            self._length: int = int(length)
        else:
            raise TypeError(
                f'{self.__class__.__name__} data must be either '
                + f'str or {self.__class__.__name__}, not {type(data)!s}'
            )
        self._validate()

    @property
    def data(self) -> str:
        return self._data

    @property
    def start(self) -> int:
        return self._start

    @property
    def length(self) -> int:
        return self._length

    @property
    def end(self) -> int:
        return self.start + self.length

    def _validate(self) -> None:
        if self.start > len(self.data):
            raise IndexError('start index is beyond end of data')
        if self.start < -len(self.data):
            raise IndexError('negative start index is before start of data')
        if self.length < 0:
            raise IndexError('length is less than zero')
        if self.end > len(self.data):
            raise IndexError('length extends beyond the end of data')

    def __str__(self) -> str:
        return self.data[self.start:self.end]

    def __repr__(self) -> str:
        return ''.join([
            self.__class__.__name__,
            '(',
            repr(self.data),
            ', start=',
            repr(self.start),
            ', length=',
            repr(self.length),
            ')',
        ])

    def lchop(self, n: int) -> tuple[Self, Self]:
        n = min(n, self.length)
        return self.__class__(self, length=n), self.__class__(self, start=n)

    def rchop(self, n: int) -> tuple[Self, Self]:
        n = min(n, self.length)
        return (
            self.__class__(self, length=self.length - n),
            self.__class__(self, start=self.length - n),
        )

    def lchop_by_delim(self, delim: Self | str) -> tuple[Self, Self]:
        i = self.find(delim)
        if i == -1:
            return self, self.__class__(self, start=self.length)
        return (
            self.__class__(self, length=i),
            self.__class__(self, start=i + len(delim)),
        )

    def lchop_int(self) -> tuple[int, Self]:
        signs = self.__class__('-+')
        i = 0
        while i < self.length:
            self_i = self[i]
            if self_i.isdigit() or (i == 0 and self_i in signs):
                i += 1
            else:
                break
        return (
            int(self.__class__(self, length=i)),
            self.__class__(self, start=i),
        )

    def lchop_while(
        self, predicate: Callable[[Self], bool],
    ) -> tuple[Self, Self]:
        i = 0
        while i < self.length and predicate(self[i]):
            i += 1
        return self.lchop(i)

    def ltake_while(
        self, predicate: Callable[[Self], bool],
    ) -> tuple[Self, Self]:
        i = 0
        while i < self.length and predicate(self[i]):
            i += 1
        return self.__class__(self, length=i), self.__class__(self, start=i)

    # These methods are the same as those on Python's str class, but there's
    # something a little more sensible we should do when we have a view.

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, self.__class__):
            if self.length != other.length:
                return False
            if self.data is other.data:
                return (
                    self.start == other.start and self.length == other.length
                )
            return str(self) == str(other)
        return str(self) == other

    # There's no need to define __ne__() since object has a default
    # implementation that just negates whatever __eq__() returns.

    def find(
        self,
        sub: Self | str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> int:
        sub = _ensure_str(sub)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        i = self.data.find(sub, self.start + start, min(self.end, end))
        return -1 if i == -1 else i - self.start

    def index(
        self,
        sub: Self | str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> int:
        sub = _ensure_str(sub)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        i = self.data.index(sub, self.start + start, min(self.end, end))
        return i - self.start

    def rfind(
        self,
        sub: Self | str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> int:
        sub = _ensure_str(sub)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        i = self.data.rfind(sub, self.start + start, min(self.end, end))
        return -1 if i == -1 else i - self.start

    def rindex(
        self,
        sub: Self | str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> int:
        sub = _ensure_str(sub)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        i = self.data.rindex(sub, self.start + start, min(self.end, end))
        return i - self.start

    def count(
        self,
        sub: Self | str,
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> int:
        sub = _ensure_str(sub)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        return self.data.count(sub, self.start + start, min(self.end, end))

    def __contains__(self, sub: Self | str, /) -> bool:
        return self.find(sub) != -1

    def startswith(
        self,
        prefix: Self | str | tuple[Self | str, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        if not isinstance(prefix, tuple):
            prefix = _ensure_str(prefix)
        else:
            prefix = tuple(_ensure_str(x) for x in prefix)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        return self.data.startswith(
            prefix, self.start + start, min(self.end, end),
        )

    def endswith(
        self,
        suffix: Self | str | tuple[Self | str, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        if not isinstance(suffix, tuple):
            suffix = _ensure_str(suffix)
        else:
            suffix = tuple(_ensure_str(x) for x in suffix)
        start = 0 if start is None else start.__index__()
        end = sys.maxsize if end is None else end.__index__()
        return self.data.endswith(
            suffix, self.start + start, min(self.end, end),
        )

    def removeprefix(self, prefix: Self | str, /) -> Self:
        if isinstance(prefix, self.__class__):
            prefix = str(prefix)
        if not self.startswith(prefix):
            return self
        return self.__class__(self, start=len(prefix))

    def removesuffix(self, suffix: Self | str, /) -> Self:
        if isinstance(suffix, self.__class__):
            suffix = str(suffix)
        if not self.endswith(suffix):
            return self
        return self.__class__(self, length=self.length - len(suffix))

    def lstrip(self, chars: Self | str | None = None, /) -> Self:
        if chars is None:
            chars = self.__class__(string.whitespace)
        elif isinstance(chars, str):
            chars = self.__class__(chars)
        new_start = 0
        while new_start < self.length and self[new_start] in chars:
            new_start += 1
        return self.__class__(self, start=new_start)

    def rstrip(self, chars: Self | str | None = None, /) -> Self:
        if chars is None:
            chars = self.__class__(string.whitespace)
        elif isinstance(chars, str):
            chars = self.__class__(chars)
        new_length = self.length
        while new_length > 0 and self[new_length - 1] in chars:
            new_length -= 1
        return self.__class__(self, length=new_length)

    def partition(self, sep: Self | str, /) -> tuple[Self, Self, Self]:
        i = self.find(sep)
        if i == -1:
            empty_at_end = self.__class__(self, start=self.length)
            return self, empty_at_end, empty_at_end
        return (
            self.__class__(self, length=i),
            self.__class__(self, start=i, length=len(sep)),
            self.__class__(self, start=i + len(sep)),
        )

    def rpartition(self, sep: Self | str, /) -> tuple[Self, Self, Self]:
        i = self.rfind(sep)
        if i == -1:
            empty_at_start = self.__class__(self, length=0)
            return empty_at_start, empty_at_start, self
        return (
            self.__class__(self, length=i),
            self.__class__(self, start=i, length=len(sep)),
            self.__class__(self, start=i + len(sep)),
        )

    def split(
        self, sep: Self | str | None = None, maxsplit: SupportsIndex = -1,
    ) -> list[Self]:
        maxsplit = maxsplit.__index__()

        if sep is None:
            whitespace = self.__class__(string.whitespace)
            parts: list[Self] = []
            rest = self
            while True:
                i = 0
                while i < rest.length and rest[i] in whitespace:
                    i += 1
                if i == rest.length:
                    return parts
                if len(parts) == maxsplit:
                    parts.append(self.__class__(rest, start=i))
                    return parts
                j = i + 1
                while j < rest.length and rest[j] not in whitespace:
                    j += 1
                parts.append(self.__class__(self, start=i, length=j - i))
                rest = self.__class__(self, start=j)

        elif isinstance(sep, self.__class__):
            sep = str(sep)

        parts: list[Self] = []
        rest = self
        while True:
            first, found_sep, rest = rest.partition(sep)
            parts.append(first)
            if found_sep.length == 0:
                return parts
            if len(parts) == maxsplit:
                parts.append(rest)
                return parts

    def rsplit(
        self, sep: Self | str | None = None, maxsplit: SupportsIndex = -1,
    ) -> list[Self]:
        maxsplit = maxsplit.__index__()

        if sep is None:
            whitespace = self.__class__(string.whitespace)
            parts: list[Self] = []
            rest = self
            while True:
                i = rest.length - 1
                while i >= 0 and rest[i] in whitespace:
                    i -= 1
                if i == -1:
                    return list(reversed(parts))
                if len(parts) == maxsplit:
                    parts.append(self.__class__(rest, length=i + 1))
                    return list(reversed(parts))
                j = i - 1
                while j >= 0 and rest[j] not in whitespace:
                    j -= 1
                parts.append(self.__class__(self, start=j + 1, length=i - j))
                rest = self.__class__(self, length=j + 1)

        elif isinstance(sep, self.__class__):
            sep = str(sep)

        parts: list[Self] = []
        rest = self
        while True:
            rest, found_sep, last = rest.rpartition(sep)
            parts.append(last)
            if found_sep.length == 0:
                return list(reversed(parts))
            if len(parts) == maxsplit:
                parts.append(rest)
                return list(reversed(parts))

    def splitlines(self, keepends: bool = False) -> list[Self]:
        # TODO: update this to handle other types of newlines
        lines = self.split('\n')
        if not keepends:
            return lines
        lines_with_ends: list[Self] = []
        for i, line in enumerate(lines):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                lines_with_ends.append(
                    self.__class__(line, length=next_line.start - line.start)
                )
            else:
                lines_with_ends.append(line)
        return lines_with_ends

    def strip(self, chars: Self | str | None = None, /) -> Self:
        return self.lstrip(chars).rstrip(chars)

    # The methods below implement Python's str interface by just converting the
    # view to an str and then forwarding to the appropriate str method.

    def __int__(self) -> int:
        return int(str(self))

    def __float__(self) -> float:
        return float(str(self))

    def __complex__(self) -> complex:
        return complex(str(self))

    def __hash__(self) -> int:
        return hash(str(self))

    def __lt__(self, other: Self | str, /) -> bool:
        if isinstance(other, self.__class__):
            return str(self) < str(other)
        return str(self) < other

    def __le__(self, other: Self | str, /) -> bool:
        if isinstance(other, self.__class__):
            return str(self) <= str(other)
        return str(self) <= other

    def __gt__(self, other: Self | str, /) -> bool:
        if isinstance(other, self.__class__):
            return str(self) > str(other)
        return str(self) > other

    def __ge__(self, other: Self | str, /) -> bool:
        if isinstance(other, self.__class__):
            return str(self) >= str(other)
        return str(self) >= other

    def __len__(self) -> int:
        return self.length

    @typing.overload
    def __getitem__(self, key: SupportsIndex, /) -> Self:
        ...

    @typing.overload
    def __getitem__(self, key: slice, /) -> Self | str:
        ...

    def __getitem__(self, key, /):
        try:
            key = key.__index__()
        except AttributeError:
            pass
        else:
            return self.__class__(self, start=key, length=1)

        if (
            isinstance(key, slice)
            and (key.step is None or key.step.__index__() == 1)
        ):
            return self.__class__(
                self,
                start=key.start.__index__(),
                length=key.stop.__index__() - key.start.__index__(),
            )
        return str(self)[key]

    def __add__(self, other: Self | str, /) -> str:
        if isinstance(other, self.__class__):
            return str(self) + str(other)
        return str(self) + other

    def __radd__(self, other: str, /) -> str:
        # If __radd__() gets called, the only valid case will be when other is
        # an str. If other was a view, then __add__() would have been called.
        return other + str(self)

    def __mul__(self, other: SupportsIndex, /) -> str:
        return str(self) * other.__index__()

    __rmul__ = __mul__  # Multiplication is commutative for str

    def __mod__(self, args: Any, /) -> str:
        return str(self) % args

    def __rmod__(self, template: Any, /) -> str:
        return template % str(self)

    def capitalize(self) -> str:
        return str(self).capitalize()

    def casefold(self) -> str:
        return str(self).casefold()

    def lower(self) -> str:
        return str(self).lower()

    def swapcase(self) -> str:
        return str(self).swapcase()

    def title(self) -> str:
        return str(self).title()

    def upper(self) -> str:
        return str(self).upper()

    def center(self, width: SupportsIndex, fillchar: str = ' ', /) -> str:
        return str(self).center(width.__index__(), fillchar)

    def expandtabs(self, tabsize: SupportsIndex = 8) -> str:
        return str(self).expandtabs(tabsize.__index__())

    def ljust(self, width: SupportsIndex, fillchar: str = ' ', /) -> str:
        return str(self).ljust(width.__index__(), fillchar)

    def rjust(self, width: SupportsIndex, fillchar: str = ' ', /) -> str:
        return str(self).rjust(width.__index__(), fillchar)

    def zfill(self, width: SupportsIndex, /) -> str:
        return str(self).zfill(width.__index__())

    def join(self, iterable: Iterable[Self | str], /) -> str:
        return str(self).join(_ensure_str(x) for x in iterable)

    def isalpha(self) -> bool:
        return str(self).isalpha()

    def isalnum(self) -> bool:
        return str(self).isalnum()

    def isascii(self) -> bool:
        return str(self).isascii()

    def isdecimal(self) -> bool:
        return str(self).isdecimal()

    def isdigit(self) -> bool:
        return str(self).isdigit()

    def isidentifier(self) -> bool:
        return str(self).isidentifier()

    def islower(self) -> bool:
        return str(self).islower()

    def isnumeric(self) -> bool:
        return str(self).isnumeric()

    def isprintable(self) -> bool:
        return str(self).isprintable()

    def isspace(self) -> bool:
        return str(self).isspace()

    def istitle(self) -> bool:
        return str(self).istitle()

    def isupper(self) -> bool:
        return str(self).isupper()

    maketrans = str.maketrans  # This one is a static method on str

    def translate(self, table: Any, /) -> str:
        return str(self).translate(table)

    def replace(
        self, old: Self | str, new: Self | str, /, count: SupportsIndex = -1,
    ) -> str:
        old = _ensure_str(old)
        new = _ensure_str(new)
        count = count.__index__()
        return str(self).replace(old, new, count)

    def format(self, *args: Any, **kwargs: Any) -> str:
        return str(self).format(*args, **kwargs)

    def format_map(self, mapping: Any, /) -> str:
        return str(self).format_map(mapping)

    def encode(
        self,
        encoding: str | None = 'utf-8',
        errors: str | None = 'strict',
    ) -> bytes:
        encoding = 'utf-8' if encoding is None else encoding
        errors = 'strict' if errors is None else errors
        return str(self).encode(encoding, errors)


def _ensure_str(s_or_sv: str | StrView) -> str:
    if type(s_or_sv) is str:
        return s_or_sv
    if isinstance(s_or_sv, (StrView, str)):
        return str(s_or_sv)
    raise TypeError(f'expected str or str view, but got {type(s_or_sv)}')
