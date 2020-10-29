"""

WARNING
-------
this is nothing to use in productive code !!!

this is a complex scenario because it deals with fiber
on a very low level because of using normal data types
with no further handshake 

always keep in mind that yield causes others getting processed

this is therefore _not_ comparable with async await in python !!!

fiber is on a lower system architectural level than async await.

this demo shows how a master sends data to a slave via a simple list
and get the data back as echo into another list

"""

from modext.fiber import *


#
# this will be part of fiber package later...
# but shown here to explain the magic of exception propagation
#
def run(fbr):
    if fbr.err != None:
        raise fbr.err
    if fbr.rc != None:
        return fbr.rc
    yield


def slave(inqueue, outqueue, use_excep):
    while True:
        if len(inqueue) > 0:
            # echo back
            outqueue.extend(inqueue)
            # we clear here and check later the output (for this demo)
            inqueue.clear()

            # this depends how the sample is configured, raise at 150
            if use_excep and outqueue[-2] == 150:
                #
                # raise this to surrounding/ own fiber -> fiber loop -> run -> master
                # in console output is shown how exception is pushed forward
                #
                raise Exception("something went wrong")

            # not really nice...
            # and _not_ recommended to do so ...
            if outqueue[-1] == None:
                # stop signal
                print("done")
                break
        else:
            print("no input")

        # dont yield only in the else above !!!
        # otherwise it will block
        # dont yield a calculated value here since it might get overwritten
        # before getting processed by the master ...
        # or even not processed at all since the fiber might be wiped out
        # by fiberloop before ... but this could only happen if the master
        # yields more often than the slave - it's possible
        yield


def master(use_excep, less_yields, floop):

    # this one deals with normal types,
    # no lock, or atom write, or etc required since fiber ensures this by concept
    # between 2 yield statements no other processing takes place
    # since there is no other "outer scheduler" which can interrupt
    # the data is always syncronized between the different fiber
    # the sending and receiving lists
    a2b_q = []
    b2a_q = []

    slave_f = Fiber(slave(a2b_q, b2a_q, use_excep), timer=True)
    # add to fiber loop
    floop.add(slave_f)

    try:
        for i in range(0, 200, 10):

            # send data in the queue
            a2b_q.extend([i, i + 1])

            # see wants in incoming there...
            if len(b2a_q) > 0:
                print(b2a_q)
                # do something or keep it...
                b2a_q.clear()
            else:
                # this should appear only once
                print("nothing processed")

            # call slave indirectly, and receive exceptions !!!
            rc = yield from run(slave_f)
            # alternative check slave_f.rc and slave_f.err

            if not less_yields:
                # why not ... slave will get more often called
                yield  # yield always, no exception from slave !!!
                yield from run(slave_f)  # yield depending on slave with exception

        # send stop signal
        a2b_q.append(None)

        # clear queue, to see if the slave continues sending data
        b2a_q.clear()

        # let message from slave be printed together with received data
        # here a None might apear since this is the stop signal
        print("hop1", b2a_q)
        yield
        print("hop2", b2a_q)
        yield
        print("hop3", b2a_q)
        yield

        # last turn...
    except Exception as ex:
        print("ups...", ex)


def sample(use_excep=False, less_yields=False):

    fl = FiberLoop(timer=True)

    fl.add(Fiber(master(use_excep, less_yields, fl), timer=True))

    for status_change in fl:
        if status_change:
            print(status_change)

    last_status = fl.status()
    print(last_status)

    print(fl)


# try
# from sample.fiber_master_slave import sample
# sample(False,False)
# sample(True,False)
# sample(False,True)
# sample(True,True)
# watch the output
# when set 1st arg to True the slave will raise an exception during run
# when set 2nd arg to True the master will less yield
