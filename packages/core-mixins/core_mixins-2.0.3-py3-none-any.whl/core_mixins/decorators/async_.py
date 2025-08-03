# -*- coding: utf-8 -*-

import asyncio
import inspect
import threading
from functools import wraps


class SyncWrapper:
    """
    It provides an interface (mechanism) to execute async code from
    sync apps via a background thread that keeps a single event
    loop alive, avoiding `asyncio.run()` which creates and
    destroys an event loop each time and becomes
    expensive for many method calls.

    .. code-block:: python

        class Test:
            def sync_method(self) -> str:
                return self.__class__.__name__

            async def testing(self) -> bool:
                await sleep(0)
                return True

        sync_instance = SyncWrapper(instance)
        assert Test.__name__, sync_instance.sync_method()
        assert sync_instance.testing(), True
        sync_instance.close()
    ..
    """

    def __init__(self, async_instance):
        self._async_instance = async_instance
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, name):
        attr = getattr(self._async_instance, name)
        if inspect.iscoroutinefunction(attr):
            @wraps(attr)
            def sync_method(*args, **kwargs):
                coro = attr(*args, **kwargs)
                future = asyncio.run_coroutine_threadsafe(coro, self._loop)
                return future.result()
            return sync_method
        return attr

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def close(self):
        if hasattr(self._async_instance, "close") and inspect.iscoroutinefunction(self._async_instance.close):
            fut = asyncio.run_coroutine_threadsafe(self._async_instance.close(), self._loop)
            fut.result()

        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self._loop.close()
