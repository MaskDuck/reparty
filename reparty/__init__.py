from asyncio import set_event_loop_policy

try:
    from uvloop import EventLoopPolicy

    set_event_loop_policy(EventLoopPolicy())
except ImportError:
    pass
