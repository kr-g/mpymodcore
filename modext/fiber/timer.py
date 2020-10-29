# faking the platform, requires py 3.7
_python = True
try:
    import utime as _time

    print("running on micropython")
    _python = False
except:
    import time as _time


class time(object):
    @staticmethod
    def time():
        if _python:
            return _time.time()
        return _time.ticks_ms()

    @staticmethod
    def ticks_ms():
        if _python:
            # py 3.7
            return _time.time_ns() / 1000000
        return _time.ticks_ms()

    @staticmethod
    def ticks_diff(t1, t2):
        if _python:
            return t1 - t2
        return _time.ticks_diff(t1, t2)

    @staticmethod
    def ticks_add(t1, t2):
        if _python:
            return t1 + t2
        return _time.ticks_add(t1, t2)

    @staticmethod
    def sleep_ms(t):
        return _time.sleep(t / 1000)


class TimerSupport(object):
    def __init__(self):
        self.start_timer()

    def start_timer(self):
        self.start_time = time.ticks_ms()
        self.stop_time = 0
        self.cpu_time = 0
        self.lastcall_start = 0
        self.lastcall_time = 0

    def run_time(self):
        return time.ticks_diff(self.stop_time, self.start_time)

    def run_time_diff_ms(self):
        now = time.ticks_ms()
        return time.ticks_diff(now, self.start_time)

    def stop_timer(self):
        self.stop_time = time.ticks_ms()

    def measure_timer(self, start=True):
        if start:
            self.lastcall_start = time.ticks_ms()
        else:
            now = time.ticks_ms()
            self.lastcall_time = time.ticks_diff(now, self.lastcall_start)
            self.cpu_time += self.lastcall_time

    def __repr__(self):
        return (
            self.__class__.__name__
            + "(start: "
            + str(self.start_time)
            + ", stop: "
            + str(self.stop_time)
            + ", run time: "
            + str(self.run_time())
            + ", cpu time: "
            + str(self.cpu_time)
            + ")"
        )
