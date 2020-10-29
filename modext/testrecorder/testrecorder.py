"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import os
import sys


__test_ids = {}
__test_id_cnt = 0


def _reset():
    global __test_ids
    global __test_id_cnt
    __test_ids = {}
    __test_id_cnt = 0


#
# use this to create trackable id() based identifiers,
# see example at the end of this file
#


def tid(obj):
    global __test_ids
    global __test_id_cnt
    oid = id(obj)
    rid = None
    if oid in __test_ids:
        rid = __test_ids[oid]
    else:
        __test_id_cnt += 1
        rid = __test_id_cnt
        __test_ids[oid] = __test_id_cnt
    return "{testid:" + str(rid) + "}"


class TestRecorder(object):

    IGNORE = "!-"
    _platform_hint = True

    # the folder MUST exist, no automatic creation!
    dest_dir = "~/testrecorder/"
    fallback_dir = "./"

    # testname: defaults to "default" if not specified
    # record
    # - True: recording the test output in of testname.trec.txt
    # - False: capturing test output in testname.trun.txt and check against testname.trec.txt
    #
    # nil: True for ignore everything
    # reset: reset internal counter and obj cache
    # capture_all: True for redirecting stdout - does not work on all platforms
    def __init__(
        self,
        testname=None,
        record=False,
        nil=False,
        dest_dir=None,
        reset=True,
        capture_all=False,
    ):

        if reset:
            _reset()

        if dest_dir == None:
            dest_dir = TestRecorder.dest_dir

        if dest_dir.find("~") == 0:
            try:
                dest_dir = os.path.expanduser(dest_dir)
            except:
                print("no user path expanded")
                dest_dir = dest_dir.replace("~", TestRecorder.fallback_dir)

        if testname == None or len(testname.strip()) == 0:
            testname = "default"

        self.testname = testname
        self.dest_dir = dest_dir

        self.fnam_record = dest_dir + testname + ".trec.txt"
        self.fnam_run = dest_dir + testname + ".trun.txt"

        self.record = record
        self.nil = nil
        self.capture_all = capture_all

        if self.record:
            try:
                os.remove(self.fnam_record)
            except:
                pass
        try:
            os.remove(self.fnam_run)
        except:
            pass

        try:
            self.open_platform_specific()
        except:
            if TestRecorder._platform_hint:
                TestRecorder._platform_hint = False
                print(
                    "on this plattform calling print is not recorded. "
                    "use testrecorder.print() instead"
                )

    # platform specific handling

    def open_platform_specific(self):
        ## todo -> dupterm, problem. will not work because eg thonny
        ## todo -> unix port plus mocking
        self.stdout = sys.stdout
        if self.capture_all:
            # fails on micropython
            # this will redirect all output to self.write
            sys.stdout = self

    def close_platform_specific(self):
        ## todo
        # this will fail on micropython
        try:
            if self.capture_all:
                sys.stdout = sys.__stdout__
        except:
            pass

    # end of platform specific handling

    def write(self, by):
        if not self.nil:
            if self.record:
                with open(self.fnam_record, "a+") as f:
                    f.write(by)
            else:
                with open(self.fnam_run, "a+") as f:
                    f.write(by)

        return print(by, file=self.stdout, end="")

    #

    def print(self, *args):
        if not self.nil:
            if self.record:
                with open(self.fnam_record, "a+") as f:
                    print(*args, file=f)
            else:
                with open(self.fnam_run, "a+") as f:
                    print(*args, file=f)

        return print(*args, file=self.stdout)

    #

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.close_platform_specific()

        if exc_type == None:
            self._assert()

    def _assert(self):
        if not self.record and not self.nil:
            with open(self.fnam_record) as f:
                tr = f.readlines()
            with open(self.fnam_run) as f:
                trun = f.readlines()
            cnt = 1
            while True:
                if len(tr) == 0:
                    break
                t1 = tr.pop(0)
                if len(trun) == 0:
                    raise Exception(
                        self.__class__.__name__, "failed, missing line", cnt
                    )
                t2 = trun.pop(0)

                if len(t1) >= 2 and t1.startswith(TestRecorder.IGNORE):
                    if t2.startswith(TestRecorder.IGNORE):
                        continue

                if t1 != t2:
                    raise Exception(self.__class__.__name__, "failed, line", cnt)

                cnt += 1
            if len(trun) > 0:
                raise Exception(self.__class__.__name__, "failed, overflow line", cnt)

            print("-" * 37)
            print(self.__class__.__name__, "test ok [" + self.testname + "]")
            print("-" * 37)


def sample():

    print()
    print("*** testing TestRecorder itself ***")
    print()

    nil = False

    testnam = "testrecorder"

    # ignore this since already in git
    if False:
        # no name, or blank name default to 'default'
        # create the recording
        # to use the same code later as test case
        # use set record to False, then output will
        # be compared against former recording
        with TestRecorder(testnam, record=True, nil=nil, dest_dir="./") as tr:
            tr.print("test recorder beispiel", tid(tr))
            tr.print(TestRecorder.IGNORE, "ignore this text")
            tr.print("one line")

    # check against recording, this will result in ok
    with TestRecorder(testnam, record=False, nil=nil, dest_dir="./") as tr:
        tr.print("test recorder beispiel", tid(tr))
        tr.print(TestRecorder.IGNORE, "ignore this too 2")
        tr.print("one line")

    print()
    print("--- from here onwards only fails ---")
    print()

    try:
        # check against recording, this will fail
        with TestRecorder(testnam, record=False, nil=nil, dest_dir="./") as tr:
            tr.print("test recorder beispiel", tid(tr))
            tr.print(TestRecorder.IGNORE, "ignore this too 3")
            # missing line here
    except Exception as ex:
        print(ex)

    try:
        # check against recording, this will fail
        with TestRecorder(testnam, record=False, nil=nil, dest_dir="./") as tr:
            # additional text
            tr.print("test recorder beispiel", tid(tr) + "stupid")
            tr.print(TestRecorder.IGNORE, "ignore this too 4")
            tr.print("one line")
    except Exception as ex:
        print(ex)

    try:
        # print one additional line, this will result in exception
        with TestRecorder(testnam, record=False, nil=nil, dest_dir="./") as tr:
            tr.print("test recorder beispiel", tid(tr))
            tr.print(TestRecorder.IGNORE, "ignore this too 5")
            tr.print("one line")
            # one more line
            tr.print("bullshit")
    except Exception as ex:
        print(ex)


if __name__ == "__main__":

    sample()
