from __future__ import annotations

_cdn_endpoint = "https://cdn.discordapp.com/"


from ..obj.client import Client
from typing import Range, TYPE_CHECKING, Literal

if TYPE_CHECKING:
    CDNAssetForm = Literal['PNG', "JPEG", "WebP", "GIF"]
from ..core.http.request import RequestInformation


class Asset:
    def __init__(
            self,
            cdn_url: str,
            bot: Client):
        assert cdn_url.startswith(_cdn_endpoint), "Invalid CDN URL"
        self.cdn_url = cdn_url
        self.bot = bot

    def _url_factory(self, desired_size: Range[16, 4096] = 4096):
        return self.cdn_url + f"?size={desired_size}"

    async def save(self, desired_size: Range[16, 4096], filename: str = "download.png"):
        r = RequestInformation(
                method="GET",
                route=self._url_factory(desired_size),  # type: ignore
                rather_than_discord=True,
            )
        x = await self.bot._http_client.request(r)

        with open(filename, "wb") as f:
            f.write(x)




        


