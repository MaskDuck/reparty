from __future__ import annotations

from reparty.core.gateway.client import WSClient
from reparty.core.http.request import Requestor
from reparty.obj.state import Cacher

from reparty.typehint import HasRepr
from typing import Generic

class Client:
    def __init__(
        self,
        *,
        token: str,
        intents: int,  # TODO: it is needed to turn this into flags
    ) -> None:
        self._token = token
        self.intents = intents
        self._ws_client = WSClient(token=token, intents=intents, bot=self)
        self._http_client = Requestor(token=token)
        # self._ws_client.bot = self
        self.cacher: Cacher = Cacher(self)

    #def send_message(
    #    self,
    #   content: Any
    #)



    def start(self):
        self._ws_client.connect()





