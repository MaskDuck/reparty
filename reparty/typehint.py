from __future__ import annotations

from typing import Type


class HasRepr:
    def __repr__(self):
        ...


class _EmptyField:
    def __str__(self):
        return ""

    def __int__(self):
        return 0

    def __bool__(self):
        return False

    def __repr__(self):
        return ""


Empty = _EmptyField()

Undefined = Type[_EmptyField]
