"""
    fiber
    https://en.wikipedia.org/wiki/Fiber_(computer_science)
    
    yield
    https://en.wikipedia.org/wiki/Cooperative_multitasking
    
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from modcore.log import LogSupport

from .timer import time, TimerSupport


class FiberWorkerLoop(LogSupport, TimerSupport):
    def __init__(self, name=None, react_time_ms=None, timer=True):
        LogSupport.__init__(self)
        TimerSupport.__init__(self)
        self.name = name
        self.timer = timer
        self.worker = []
        self.react_time = react_time_ms / 1000 if react_time_ms != None else None

    def append(self, worker):
        worker.floop = self
        self.worker.append(worker)

    def remove(self, worker):
        self.worker.remove(worker)

    def kill(self, reason="kill"):
        for w in self.worker:
            w.kill(reason)

    def close(self):
        for w in self.worker:
            w.kill("close")

    def release(self):

        if len(self.worker) == 0:
            return

        for w in self.worker:
            if w.done != None:
                w.close()

        self.worker = list(filter(lambda x: x.done == None, self.worker))

    def _schedule(self, react_time=None, max=None):
        react_time = self.react_time if react_time == None else react_time
        try:
            time_p_fbr = react_time / (len(self) if max == None else max)
            return time_p_fbr * 1000
        except:
            # division by zero
            return None

    def __len__(self):
        return len(self.worker)

    def __iter__(self):
        return self

    def __call__(self):
        next(self)

    def __next__(self):

        tpf = self._schedule()  # time per fiber
        unused_tpf = 0

        self.timer and self.start_timer()

        for w in self.worker:

            if tpf != None:
                trfts = tpf + unused_tpf  # this round fiber time slot

            # unused_tpf>0 and self.debug and print( "!-", "tpf", tpf, "unused", unused_tpf )

            w._switch_time = (
                time.ticks_add(trfts, time.ticks_ms()) if tpf != None else None
            )
            unused_tpf = 0

            try:
                self.timer and self.measure_timer()
                # next(w)
                w()

            except StopIteration as ex:
                self.debug(repr(w), ex)
                pass

            except Exception as ex:
                self.excep(ex, repr(w))
                pass

            finally:
                if self.timer:
                    self.measure_timer(False)
                    if tpf != None:
                        diff = trfts - self.lastcall_time
                        if diff > 0:
                            unused_tpf = diff

        self.timer and self.stop_timer()


class FiberWaitTimeout(Exception):
    pass


class FiberWorker(LogSupport):
    def __init__(self, func=None, workerloop=None, parent=None, **kwargs):
        LogSupport.__init__(self)
        self.func = func
        self.floop = workerloop
        self.parent = parent
        self._run = False
        self.kwargs = kwargs
        self._switch_time = None

        if self.floop:
            self.floop.append(self)

        self.reset("init")

    def _floop_name(self):
        return "" if self.floop == None else self.floop.name

    def reset(self, reason="reset"):
        self.kill(reason)
        self.info("reset", reason, repr(self), self._floop_name())
        self.rc = None
        self.err = None
        self.done = None
        self._inner = self.__fiber__()
        self.init()

    def __fiber__(self):
        if self.func == None:
            raise Exception("no fiber defined, or __fiber__ overloaded")
        return self.func(self)

    def init(self):
        pass

    def start(self):
        self.resume("start")

    def resume(self, reason="resume"):
        self.info("resume", reason, repr(self), self._floop_name())
        try:
            if self._run or self.floop == None:
                return
            self.floop.append(self)
        finally:
            self._run = True

    def suspend(self, reason="suspend"):
        self.info("suspend", reason, repr(self), self._floop_name())
        try:
            if not self._run or self.floop == None:
                return
            self.floop.remove(self)
        finally:
            self._run = False

    def kill(self, reason="kill"):
        self.info("kill", reason, repr(self), self._floop_name())
        self.suspend(reason)
        self._inner = None
        # untested
        if self.parent != None:
            self.parent.kill(reason)
            self.parent = None

    def close(self):
        self.kill("close")

    def sleep_ms(self, msec=None):
        if msec == None or msec == 0:
            # switch to next fiber
            yield
            return
        now = time.ticks_ms()
        stop = time.ticks_add(now, msec)
        while True:
            if time.ticks_diff(stop, time.ticks_ms()) < 0:
                break
            yield

    def switch(self):
        if self._switch_time == None:
            return
        if time.ticks_diff(self._switch_time, time.ticks_ms()) > 0:
            return False
        self.debug("switch", repr(self), self.floop.name)
        # switch to next fiber
        yield
        return True

    def waitfor_ms(self, worker, timeout_ms=-1, raise_ex=False):
        if worker == None:
            return
        now = time.ticks_ms()
        stop = time.ticks_add(now, timeout_ms)
        while True:
            if worker.done != None:
                return worker.done, worker.rc, worker.err
            if time.ticks_diff(stop, time.ticks_ms()) < 0:
                if raise_ex:
                    ##todo behaviour ?
                    raise FiberWaitTimeout()
                return worker.done, None, None
            yield

    def spawn_fiber(self, worker):
        self.suspend("spawn")
        worker.parent = self
        worker.resume("spawn-start")

        # switch to next fiber
        # exactly once!
        yield
        # return here after resume
        # from _done_revoke_parent()

        if worker.err != None:
            raise worker.err
        if worker.rc != None:
            return worker.rc

        return 1234567890

    def spawn(self, func, workerloop=None, **kwargs):
        if workerloop == None:
            workerloop = self.floop
        worker = FiberWorker(func=func, workerloop=workerloop, **kwargs)
        return self.spawn_fiber(worker)

    def _done_revoke_parent(self, reason="worker-done"):
        self.suspend(reason)
        if self.parent != None:
            self.parent.resume("spawn-return")

    def __call__(self):
        next(self)

    def __next__(self):

        try:
            self.rc = next(self._inner)
            return self.rc

        except StopIteration as ex:
            self.debug("stop", repr(self))
            self.done = time.ticks_ms()
            self._done_revoke_parent()
            raise ex

        except Exception as ex:
            self.excep(ex, repr(self))
            self.err = ex
            self.done = time.ticks_ms()
            self._done_revoke_parent("exception")
            raise ex

    def __iter__(self):
        return self
