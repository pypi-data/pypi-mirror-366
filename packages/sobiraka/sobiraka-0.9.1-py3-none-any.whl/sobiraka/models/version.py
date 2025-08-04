from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True, eq=True, order=True)
class Version:
    major: int
    minor: int

    def __str__(self):
        return f'{self.major}.{self.minor}'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self}>'

    @classmethod
    def parse(cls, text: str) -> Version:
        m = re.match(r'^ (\d+) (?: \.(\d+) )? $', text, re.VERBOSE)
        major = int(m.group(1))
        minor = int(m.group(2) or 0)
        return Version(major, minor)


class TranslationStatus(Enum):
    UPTODATE = auto()
    MODIFIED = auto()
    OUTDATED = auto()
