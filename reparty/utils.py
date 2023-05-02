from __future__ import annotations
from aiohttp import WSMessage  # , ClientResponse
import zlib

from json import loads

_decompresser = zlib.decompressobj()
_zlib_suffix: bytes = b"\x00\x00\xff\xff"
_buffer = bytearray()


def zjson_from_msg(resp: WSMessage):
    # this code is literally taken from discord docs lol
    global _buffer
    r = resp.data
    _buffer.extend(r)
    if len(r) < 4 or r[-4:] != _zlib_suffix:
        return
    else:
        o = _decompresser.decompress(_buffer)
        _buffer = bytearray()
        return loads(o)


