from __future__ import annotations


class Snowflake:
    """
    Objects that can be used if you only needs the ID.
    """
    id: int

    def __init__(self, id: int):
        self.id: int = id
    
    def __int__(self) -> int:
        return self.id


