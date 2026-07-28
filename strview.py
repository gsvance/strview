"""strview.py
"""

import string
import sys
import typing
from typing import Any, Callable, Self


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
        return self.__class__(self, length=i), self.__class__(self, start=i)

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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            if self.data is other.data:
                return (
                    self.start == other.start and self.length == other.length
                )
            return str(self) == str(other)
        return str(self) == other

    def find(self, sub: Any, start: int = 0, end: int = sys.maxsize) -> int:
        if isinstance(sub, self.__class__):
            sub = str(sub)
        return self.data.find(sub, self.start + start, min(self.end, end))

    def index(self, sub: Any, start: int = 0, end: int = sys.maxsize) -> int:
        if isinstance(sub, self.__class__):
            sub = str(sub)
        return self.data.index(sub, self.start + start, min(self.end, end))

    def rfind(self, sub: Any, start: int = 0, end: int = sys.maxsize) -> int:
        if isinstance(sub, self.__class__):
            sub = str(sub)
        return self.data.rfind(sub, self.start + start, min(self.end, end))

    def rindex(self, sub: Any, start: int = 0, end: int = sys.maxsize) -> int:
        if isinstance(sub, self.__class__):
            sub = str(sub)
        return self.data.rindex(sub, self.start + start, min(self.end, end))

    def __contains__(self, sub: Any) -> bool:
        return self.find(sub) != -1

    def count(self, sub: Any, start: int = 0, end: int = sys.maxsize) -> int:
        if isinstance(sub, self.__class__):
            sub = str(sub)
        return self.data.count(sub, self.start + start, min(self.end, end))

    def startswith(
        self, prefix: Any, start: int = 0, end: int = sys.maxsize,
    ) -> bool:
        if isinstance(prefix, self.__class__):
            prefix = str(prefix)
        return self.data.startswith(
            prefix, self.start + start, min(self.end, end),
        )

    def endswith(
        self, suffix: Any, start: int = 0, end: int = sys.maxsize,
    ) -> bool:
        if isinstance(suffix, self.__class__):
            suffix = str(suffix)
        return self.data.endswith(
            suffix, self.start + start, min(self.end, end),
        )

    def removeprefix(self, prefix: Any, /) -> Self:
        if isinstance(prefix, self.__class__):
            prefix = str(prefix)
        if not self.startswith(prefix):
            return self
        return self.__class__(self, start=len(prefix))

    def removesuffix(self, suffix, /) -> Self:
        if isinstance(suffix, self.__class__):
            suffix = str(suffix)
        if not self.endswith(suffix):
            return self
        return self.__class__(self, length=self.length - len(suffix))

    def lstrip(self, chars: Self | str | None = None) -> Self:
        if chars is None:
            chars = self.__class__(string.whitespace)
        elif isinstance(chars, str):
            chars = self.__class__(chars)
        new_start = 0
        while new_start < self.length and self[new_start] in chars:
            new_start += 1
        return self.__class__(self, start=new_start)

    def rstrip(self, chars: Self | str | None = None) -> Self:
        if chars is None:
            chars = self.__class__(string.whitespace)
        elif isinstance(chars, str):
            chars = self.__class__(chars)
        new_length = self.length
        while new_length > 0 and self[new_length - 1] in chars:
            new_length -= 1
        return self.__class__(self, length=new_length)

    def partition(self, sep: Any) -> tuple[Self, Self, Self]:
        i = self.find(sep)
        if i == -1:
            empty = self.__class__(self, start=self.length)
            return self, empty, empty
        return (
            self.__class__(self, length=i),
            self.__class__(self, start=i, length=len(sep)),
            self.__class__(self, start=i + len(sep)),
        )

    def rpartition(self, sep: Any) -> tuple[Self, Self, Self]:
        i = self.rfind(sep)
        if i == -1:
            empty = self.__class__(self, length=0)
            return empty, empty, self
        return (
            self.__class__(self, length=i),
            self.__class__(self, start=i, length=len(sep)),
            self.__class__(self, start=i + len(sep)),
        )

    def split(
        self, sep: Self | str | None = None, maxsplit: int = -1,
    ) -> list[Self]:
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
        self, sep: Self | str | None = None, maxsplit: int = -1,
    ) -> list[Self]:
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
        lines = self.split('\n')
        if not keepends:
            return lines
        lines_with_ends: list[Self] = []
        for line in lines:
            try:
                line_with_end = self.__class__(line, length=line.length + 1)
            except IndexError:
                lines_with_ends.append(line)
            else:
                lines_with_ends.append(line_with_end)
        return lines_with_ends

    def strip(self, chars: Self | str | None = None) -> Self:
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

    def __lt__(self, other: Any):
        if isinstance(other, self.__class__):
            return str(self) < str(other)
        return str(self) < other

    def __le__(self, other: Any):
        if isinstance(other, self.__class__):
            return str(self) <= str(other)
        return str(self) <= other

    def __gt__(self, other: Any):
        if isinstance(other, self.__class__):
            return str(self) > str(other)
        return str(self) > other

    def __ge__(self, other: Any):
        if isinstance(other, self.__class__):
            return str(self) >= str(other)
        return str(self) >= other

    def __len__(self) -> int:
        return self.length

    @typing.overload
    def __getitem__(self, index: int) -> Self:
        ...

    @typing.overload
    def __getitem__(self, index: slice) -> Self | str:
        ...

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.__class__(self, start=index, length=1)
        if isinstance(index, slice) and index.step == 1:
            return self.__class__(
                self, start=index.start, length=index.stop - index.start,
            )
        return str(self)[index]

    def __add__(self, other: Any) -> str:
        if isinstance(other, self.__class__):
            return str(self) + str(other)
        return str(self) + other

    def __radd__(self, other: Any) -> str:
        return other + str(self)

    def __mul__(self, other: int) -> str:
        return str(self) * other

    __rmul__ = __mul__

    def __mod__(self, args: Any) -> str:
        return str(self) % args

    def __rmod__(self, template: Any) -> str:
        return template % str(self)

    def capitalize(self) -> str:
        return str(self).capitalize()

    def casefold(self) -> str:
        return str(self).casefold()

    def center(self, width: int, *args: Any) -> str:
        return str(self).center(width, *args)

    def encode(
        self,
        encoding: str | None = 'utf-8',
        errors: str | None = 'strict',
    ) -> bytes:
        encoding = 'utf-8' if encoding is None else encoding
        errors = 'strict' if errors is None else errors
        return str(self).encode(encoding, errors)

    def expandtabs(self, tabsize: int = 8) -> str:
        return str(self).expandtabs(tabsize)

    def format(self, /, *args: Any, **kwargs: Any) -> str:
        return str(self).format(*args, **kwargs)

    def format_map(self, mapping: Any) -> str:
        return str(self).format_map(mapping)

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

    def join(self, seq: Any) -> str:
        return str(self).join(seq)

    def ljust(self, width: int, *args: Any) -> str:
        return str(self).ljust(width, *args)

    def lower(self) -> str:
        return str(self).lower()

    maketrans = str.maketrans

    def replace(self, old: Any, new: Any, /, count: int = -1) -> str:
        if isinstance(old, self.__class__):
            old = str(old)
        if isinstance(new, self.__class__):
            new = str(new)
        return str(self).replace(old, new, count)

    def rjust(self, width: int, *args: Any) -> str:
        return str(self).rjust(width, *args)

    def swapcase(self) -> str:
        return str(self).swapcase()

    def title(self) -> str:
        return str(self).title()

    def translate(self, *args: Any) -> str:
        return str(self).translate(*args)

    def upper(self) -> str:
        return str(self).upper()

    def zfill(self, width: int) -> str:
        return str(self).zfill(width)
