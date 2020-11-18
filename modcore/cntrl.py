"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

"""
try:
    import uasyncio
    print( "modcore running micropython", __name__ )
except:
    import asyncio
"""
from .lifecycle import LifeCycle
from .events import EventData, EventQueue
from .mod import Module
from .log import LogSupport


class ModuleController(LogSupport):
    def __init__(self):
        LogSupport.__init__(self)
        self.modules = {}
        self._modules = []
        self.events = {}
        self.config = {}

    def _reg_event_listener(self, mod, remove=False):
        watching = mod.watching_events()
        if watching != None:
            for e in watching:
                if e == None:
                    continue
                e = e.strip()
                if len(e) == 0:
                    continue
                e = e.lower()
                if e not in self.events:
                    self.events[e] = set()
                if remove:
                    self.events[e].remove(mod)
                else:
                    self.events[e].add(mod)

    def add(self, mod):
        if mod.id in self.modules:
            raise Exception("module id already registered.", mod.id)
        mod._controller = self
        self.modules[mod.id] = mod
        self._modules.append(mod)
        self._reg_event_listener(mod)
        mod.on_add()
        self.info("add", mod.id)
        return self

    def remove(self, mod):
        del self.modules[mod.id]
        self._reg_event_listener(mod, remove=True)
        mod.on_remove()

    def fire_event(self, event, data=None, src=None):
        event = event.strip().lower()
        if event not in self.events:
            self.warn("unknown", event, src)
            return

        for m in self.events[event]:
            if m == src:
                continue

            ed = EventData(event, data, sender=src)
            m._add_event(ed)

    def run_loop_hooks(self, before=True):
        self.info("loop hooks", before)
        for m in self._modules:
            try:
                m.call_hooks(LifeCycle.LOOP, before_call=before)
            except Exception as ex:
                self.excep(ex, "hook", m.id, before)

    def run_loop(self, config=None):
        aws = []
        for m in self._modules:
            try:
                aw = m.run(config)
                if aw != None:
                    aws.append(aw)
                    self.debug(aw)
            except Exception as ex:
                self.excep(ex, "run", m.id)

        if len(aws) > 0:
            return aws

    def run_loop_g(self, config=None, ha_mode=True):

        while True:
            aws = []
            for m in self._modules:
                try:
                    aw = m.run(config)
                    if aw != None:
                        aws.append(aw)
                        self.debug(aw)
                    if ha_mode == True:
                        yield
                except Exception as ex:
                    self.excep(ex, "run", m.id)

            if len(aws) > 0:
                yield aws
            else:
                yield

    def startup(self, config=None):
        for m in self._modules:
            try:
                m.startup(config)
            except Exception as ex:
                self.excep(ex)

    def shutdown(self):
        for m in reversed(self._modules):
            try:
                m.shutdown()
                m._events.reset()
            except Exception as ex:
                self.excep(ex)

    def reconfigure(self, config=None):
        self.shutdown()
        self.startup(config=config)

    def change_log_level(self, level=None):
        self.log_level(level)
        for m in self._modules:
            m.log_level(level)


modc = ModuleController()

_modg = None


def get_ha_g(cfg):
    global _modg
    if _modg == None:
        _modg = modc.run_loop_g(cfg)
    return _modg


def reset_ha_g():
    global _modg
    _modg = None
