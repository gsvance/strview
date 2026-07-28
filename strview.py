"""strview.py
"""

import dataclasses
from typing import Self


@dataclasses.dataclass(
    init=False,
    repr=False,
    eq=False,
    frozen=True,
    match_args=False,
    slots=True,
)
class StrView:
    data: str
    start: int
    length: int

    def __init__(
        self, data: str | Self,
        start: int | None = None,
        length: int | None = None,
    ) -> None:
        if isinstance(data, str):
            object.__setattr__(self, 'data', data)
            if start is None:
                object.__setattr__(self, 'start', 0)
            else:
                object.__setattr__(self, 'start', int(start))
            if length is None:
                object.__setattr__(self, 'length', len(data))
            else:
                object.__setattr__(self, 'length', int(length))
        elif isinstance(data, StrView):
            object.__setattr__(self, 'data', data.data)
            if start is None:
                object.__setattr__(self, 'start', data.start)
            else:
                object.__setattr__(self, 'start', data.start + int(start))
            if length is None:
                object.__setattr__(self, 'length', data.length)
            else:
                object.__setattr__(self, 'length', int(length))
        else:
            raise TypeError(
                f'cannot create {self.__class__.__name__} from {type(s)}'
            )
        self.__post_init__()

    @property
    def end(self) -> int:
        return self.start + self.length

    def __post_init__(self) -> None:
        if self.start > len(self.data):
            raise IndexError('start index too big')
        if self.start < -len(self.data):
            raise IndexError('start index too small')
        if self.length < 0:
            raise IndexError('length is too small')
        if self.end > len(self.data):
            raise IndexError('length is too big')

    def __str__(self) -> str:
        return self.data[self.start:self.end]

    def __repr__(self) -> str:
        return ''.join([
            self.__class__.__name__,
            '(',
            repr(self.data),
            ', ',
            f'start={self.start!r}',
            ', ',
            f'length={self.length!r}',
            ')',
        ])
