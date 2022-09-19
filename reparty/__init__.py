from asyncio import set_event_loop_policy
from logging import NullHandler, getLogger

try:
    from uvloop import EventLoopPolicy

    set_event_loop_policy(EventLoopPolicy())
except ImportError:
    pass

getLogger('reparty').addHandler(NullHandler())