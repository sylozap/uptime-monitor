import asyncio
import threading

_loop = None


def get_loop():
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        thread = threading.Thread(target=_run_loop, args=(_loop,), daemon=True)
        thread.start()
    return _loop


def _run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, get_loop()).result()
