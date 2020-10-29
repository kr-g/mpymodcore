from modext.fiber.fiber_worker import FiberWorker, FiberWorkerLoop, time


"""
this is not a real world sample, but shows how it works
"""


def sample():

    from modext.testrecorder import TestRecorder, tid

    #    with TestRecorder("fiber-worker-sample",record=False,nil=True,\
    #                      dest_dir = "./") as tr:

    # a fiber class
    class w1func(FiberWorker):
        def init(self):
            print("args", self.kwargs)

        def __fiber__(self):
            c = 0
            while True:
                c += 1
                if c > 100:
                    break
                print("w1", c, self.kwargs, tid(self))
                yield

    # a fiber function
    def w2subfunc(self):
        c = 50
        while True:
            c += 1
            if c > 52:
                break
            print("w2sub", c, tid(self))
            yield

        print("w2sub done", tid(self))
        # un/comment exception to test
        raise Exception("w2sub done with error", tid(self))
        # return value in rc
        yield 153

    fl_outer = FiberWorkerLoop(react_time_ms=250, name="!!!!loop2!!!!")

    def w2func(self):

        self.soft_sleep = 0

        try:
            print("spawn to w2subfunc", tid(self))
            # this spawns to an other workerloop, suspends this one and resumes after done
            # in case the worker errors an exception is raised here!
            rc = yield from self.spawn(func=w2subfunc, workerloop=fl_outer)
            print("return from w2subfunc", rc, tid(self))
        except Exception as ex:
            print("excep in w2subfunc", ex, tid(self))

        print("sleep", time.time(), self._switch_time)

        # block this fiber !!!
        time.sleep_ms(300)  # decrease this to see switch control below

        print("wake")

        # this switches to another fiber depending of time consumed so far
        sw = yield from self.switch()
        print("switched", sw)

        c = 1
        stat = None
        while True:
            print("w2", c, self.kwargs, tid(self))
            c += c

            print("sleeping softly")
            yield from self.sleep_ms(100)
            self.soft_sleep += 1
            print("smooth wake up", self.soft_sleep)

            # wait for w1 with timeout 250 ms
            if self.soft_sleep > 5 and stat == None:
                print("waiting for w1 to end")
                stat, rc, err = yield from self.waitfor_ms(self.wait_var_w1, 250)
                print("w1 waiting result", stat, rc, err)

            # yield

    global fl
    fl = FiberWorkerLoop(name="main", react_time_ms=250)

    # fiber class and function usage
    w1 = w1func(workerloop=fl, a=5, b=6)
    w2 = FiberWorker(func=w2func, workerloop=fl, a=15, c=7)

    w2.wait_var_w1 = w1

    w1.start()
    w2.start()

    next(fl)
    next(fl)
    next(fl)

    w1.suspend()
    print("suspend")

    print("hop1")
    next(fl)
    print("hop2")
    next(fl)

    w1.resume()
    print("resume")

    next(fl)
    next(fl)

    w1.reset()
    w1.start()

    print("reset")

    next(fl)
    next(fl)
    next(fl)
    next(fl)

    # this is not really recommendet
    # checking inner state of w2, and stop after 12 iterations
    while w2.done == None and w2.soft_sleep < 12:
        next(fl)
        # execute both loops
        next(fl_outer)

    # print(fl)
    print(fl_outer)


# from samples.fiber_worker import sample
