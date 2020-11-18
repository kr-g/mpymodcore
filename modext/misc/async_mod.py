try:
    import uasyncio as asyncio

    print("using micropython asyncio", __name__)
except:
    import asyncio

from modcore import modc, Module, LifeCycle, logger

from modext.misc.main_async import keyboard_c


class AsyncSkeletonModule(Module):
    def init(self):
        self.stop_sig = asyncio.Event()
        self.atask = None

    def start(self):
        self.stop_sig.clear()

    def loop(self, config=None, event=None):
        if keyboard_c.is_set():
            self.stop_sig.set()

    def stop(self):
        self.stop_sig.set()

    def create_task(self, func):
        self.stop_sig.clear()
        # this passes the module as self instance to the async coroutine
        self.atask = asyncio.create_task(func(self))

    def cancel_task(self):
        self.stop_sig.set()
        self.atask.cancel()
        self.atask = None


class AsyncModule(AsyncSkeletonModule):
    pass
