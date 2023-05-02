from asyncio import set_event_loop_policy
from logging import NullHandler, getLogger

__version__ = "0.0.1"
from reparty import core


# Linux only, this is an extension to improve performance
try:
    from uvloop import EventLoopPolicy

    set_event_loop_policy(EventLoopPolicy())
except ImportError:
    pass

getLogger("reparty").addHandler(NullHandler())
