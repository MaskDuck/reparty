from __future__ import annotations

from asyncio import sleep
from logging import getLogger
from typing import TYPE_CHECKING

from reparty.__init__ import __version__ as _version
from aiohttp import ClientResponse, ClientSession

from .ratelimiter import Ratelimiter, RatelimitBucket

from datetime import datetime
logger = getLogger("reparty")

if TYPE_CHECKING:
    from typing import Any, Dict, Optional
__all__ = (
    "RequestInformation",
    "Requestor"
)

class T(str):
    pass

class RequestInformation:
    def __init__(
        self,
        method: str,
        route: str,
        headers: Dict[str, Any] = {},
        json: Optional[Dict[str, Any]] = {},
        reason: Optional[str] = None,
        rather_than_discord: bool = False
    ):
        self.headers = headers
        self.json = json
        if reason:
            self.headers["X-Audit-Log-Reason"] = reason
        if rather_than_discord:
            self.route = route
        else:
            self.route = "https://discord.com/api/v10" + route
        self.bare_route = route
        self.method = method
        



class ResponseInformation:
    def __init__(self, *, json: Optional[dict] = None, status_code, ok: bool, headers: Optional[dict] = None) -> None:
        self.json = json
        self.status_code = status_code
        self.ok = ok
        self.headers = headers

    def __repr__(self):
        return f"<ResponseInformation json={self.json}, status_code={self.status_code}. ok={self.ok}, headers={self.headers}>"


class Requestor:
    def __init__(self, token: str, session: Optional[ClientSession] = None):
        self._user_agent = (
            f"reparty (https://github.com/reparty-org/reparty, v{_version})"
        )
        self._token: str = token
        self._session: Optional[ClientSession] = session
        self._ratelimiter = Ratelimiter()

    @classmethod
    def _create_override_user_agent(
        cls, token: str, user_agent: str, session: Optional[ClientSession] = None
    ):
        o = cls(token, session=session)
        o._user_agent = user_agent  # type: ignore
        return o

    async def request(self, r: RequestInformation):
        # async with request(r.)
        if self._ratelimiter.is_globally_ratelimited:

            await sleep(
                self._ratelimiter.is_still_globally_being_ratelimited_for.seconds
            )
            # return await self.request(r)
        if bucket := self._ratelimiter._bucket_ratelimits.get(T(r.route)):  # type: ignore
            bucket: RatelimitBucket
            if bucket.remaining == 0:
                x = bucket.reset - datetime.now()
                await sleep(x.seconds)
        if self._session is None:
            self._session = ClientSession()
        r.headers["Authorization"] = f"Bot {self._token}"
        r.headers["User-Agent"] = self._user_agent
        async with self._session.request(
            method=r.method, url=r.route, headers=r.headers, json=r.json
        ) as i:
            i: ClientResponse
            h: dict = i.headers
            self._ratelimiter._bucket_ratelimits[T(r.route)] = RatelimitBucket(h)

            # if self._ratelimiter._bucket_ratelimits.get(h['X-RateLimit-Bucket']):
            #   self._ratelimiter._bucket_ratelimits.get(h['X-RateLimit-Bucket'])
            if i.status == 200:
                j = await i.json()
                return ResponseInformation(headers=h, json=j, status_code=i.status, ok=True)

            if i.status == 204:
                return ResponseInformation(headers=h, json=None, status_code=i.status, ok=True)

            if i.status == 429:
                logger.debug("Congrats! You got ratelimited!\n" f"Endpoint: {r.route}")
                j = await i.json()
                if h.get("x-ratelimit-global"):  # this will cover both False and None
                    self._ratelimiter.toggle_global_ratelimit(h['x-ratelimit-reset'])

                return ResponseInformation(headers=h, json=j, status_code=i.status, ok=False)
            ok = 200 < i.status < 300
            return ResponseInformation(headers=h, json=None, status_code=i.status, ok=ok)

                # TODO: implement ratelimit
