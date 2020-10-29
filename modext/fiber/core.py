"""
    fiber
    https://en.wikipedia.org/wiki/Fiber_(computer_science)
    
    yield
    https://en.wikipedia.org/wiki/Cooperative_multitasking
    
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

print("\n" * 3)
print("-" * 37)
print("fiber version 1 is deprecated.")
print("-" * 37)
print("\n" * 3)


import math

from modcore.log import LogSupport

from .timer import TimerSupport


## todo
# in addition to fiber loop
# create class fiber stack
# execution in floop is done as "execute all fiber in the list"
# execution in fstack is done as "execute only the fiber on the top"
#  and remove it from the stack when done,
#  continue with next top fiber until stack is empty
#  -> all_done()==True, otherwise False


class FiberLoop(LogSupport, TimerSupport):
    def __init__(self, timer=False):
        LogSupport.__init__(self)
        TimerSupport.__init__(self)
        self.fiber = []
        self._prep()
        self.timer = timer

    def _prep(self):
        self.done = []
        self.err = []

    def _clean_up(self):
        for f in self.done:
            f.close()
        for f in self.err:
            f.close()
        self._prep()

    def add(self, fbr):
        self.fiber.append(fbr)

    def close(self):
        ## todo,
        ## call close of all fibers
        ## kill directly vs extra __close__ func ?
        self._clean_up()

    def kill(self, fbr, reason=None):
        self.fiber.remove(fbr)
        fbr.kill(reason)

    def kill_all(self, reason=None):
        for f in self.fiber:
            f.kill(reason)

    def kill_expire_ms(self, timeout, reason=None):
        for f in self.fiber:
            if f.run_time_diff_ms() >= timeout:
                f.kill(reason)

    def status(self):
        if len(self.done) > 0 or len(self.err) > 0:
            return (self.done, self.err)

    def all_done(self):
        return len(self.fiber) == 0

    def loop(self):
        try:
            next(self)
        except StopIteration:
            pass
        return len(self) > 0

    def __next__(self):
        self._clean_up()
        self.timer and self.measure_timer()
        for f in self.fiber:
            try:
                r = next(f)
                # throw away r, and continue with next fiber
            except StopIteration as ex:
                # this one is finished, remove it
                self.fiber.remove(f)
                self.done.append(f)
            except Exception as ex:
                self.fiber.remove(f)
                self.err.append(f)
                self.excep(ex, "fiber failed")
        self.timer and self.measure_timer(False)
        if self.all_done():
            self.timer and self.stop_timer()
            raise StopIteration
        return self.status()

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.fiber)


class Fiber(LogSupport, TimerSupport):
    def __init__(self, func, ctx=None, timer=False):
        LogSupport.__init__(self)
        TimerSupport.__init__(self)
        # save the generator object
        self.func = func
        self.timer = timer
        self.ctx = None if ctx == None else ctx.spin_off()
        if self.func.__class__.__name__ != "generator":
            raise Exception("no generator provided, got", type(self.func))

        self.rc = None
        self.err = None

        # trace performance younter accordigly to the log level
        ## todo
        # change later to debug
        self._perf_counter = self.info()

    def close(self):
        if self.ctx != None:
            self.ctx.close()
            self.ctx = None

    def spin_off(self):
        try:
            return self.ctx.spin_off()
        finally:
            self.ctx = None

    def kill(self, reason=None):
        self.close()
        self.func = None
        ## todo usage together with close?
        self.__kill__(reason)

    def __kill__(self, reason=None):
        pass

    def __next__(self):
        try:
            if self.timer and self._perf_counter:
                self.measure_timer()

            self.rc = next(self.func)

            if self.timer and self._perf_counter:
                self.measure_timer(False)

            return self.rc
        except StopIteration as ex:
            # here we are done
            self.close()
            raise ex
        except Exception as ex:
            self.err = ex
            self.excep(ex)
            self.close()
            raise ex
        finally:
            self.timer and self.stop_timer()

    def __iter__(self):
        return self

    def __repr__(self):
        return (
            self.__class__.__name__
            + "( rc: "
            + str(self.rc)
            + ("," if self.err == None else repr(self.err))
            + ") "
            + TimerSupport.__repr__(self)
        )


class FiberTimeoutException(Exception):
    pass


class FiberWatchdog(Fiber):

    # default timeout is math.e
    # first i wanted to use math.pi,
    # but i fear the math.tau discussion
    def __init__(self, func, timer=False, max_time_auto_kill_ms=1000 * math.e):
        Fiber.__init__(self, func, timer=timer)
        self.max_time_auto_kill_ms = max_time_auto_kill_ms

    def __next__(self):
        if self.run_time_diff_ms() >= self.max_time_auto_kill_ms:
            raise FiberTimeoutException()
        return super().__next__()


class Guard(object):
    def __init__(self, guard, debug=False):
        self._guard = guard
        self.debug = debug

    def close(self):
        self.debug and print(">close", self.__class__.__name__)
        if self._guard != None:
            self.debug and print(">close-guard", self.__class__.__name__)
            self._guard.close()
            self._guard = None

    def __enter__(self):
        self.debug and print(">enter", self.__class__.__name__)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.debug and print(">exit", self.__class__.__name__)
        try:
            self.__on_exit__(exc_type, exc_value, traceback)
        finally:
            self.close()

    # use this to enhance your code
    def __on_exit__(self, exc_type, exc_value, traceback):
        self.debug and print(">onexit", self.__class__.__name__)
        pass

    def __call__(self):
        return self._guard

    def __repr__(self):
        return repr(self._guard)


class Detachable(Guard):
    def spin_off(self):
        self.debug and print(">detach", self.__class__.__name__)
        try:
            return self.__class__(self._guard, self.debug)
        finally:
            self._guard = None


class FiberContext(Detachable):

    # use this to enhance your code
    def __on_exit__(self, exc_type, exc_value, traceback):
        self.debug and print(">leaving", self.__class__.__name__)
