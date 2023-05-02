from __future__ import annotations

import weakref
from typing import Optional

from datetime import datetime, timedelta

class T(str):
    pass

class RatelimitBucket:
    def __init__(self, headers):
        self.limit = headers['x-ratelimit-limit']
        self.bucket = headers['x-ratelimit-bucket']
        self.remaining = headers['x-ratelimit-remaining']
        self.reset = datetime.fromtimestamp(float(headers['x-ratelimit-reset']))

class Ratelimiter:
    def __init__(self) -> None:
        self._is_globally_ratelimited: bool = False
        self._ratelimited_until: Optional[datetime] = None
        self._bucket_ratelimits = weakref.WeakKeyDictionary()

    @property
    def is_globally_ratelimited(self):
        return self._is_globally_ratelimited

    @property
    def is_globally_ratelimited_until(self) -> Optional[datetime]:
        return self._ratelimited_until

    @property
    def is_still_globally_being_ratelimited_for(self) -> Optional[timedelta]:
        if self._ratelimited_until:
            return self._ratelimited_until - datetime.now()
        else:
            return timedelta(0)

    def toggle_global_ratelimit(self, until: float):
        self._is_globally_ratelimited = True
        self._ratelimited_until = datetime.fromtimestamp(until)





