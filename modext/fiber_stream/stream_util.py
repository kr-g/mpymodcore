"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""


from .channel import fc_readline
from .stream import FiberStreamIO


class FiberStreamIO_file_input_writer(FiberStreamIO):
    def __init__(self, fnam, blksize=128, lineno=False):
        self.fnam = fnam
        self.blksize = blksize
        self.done = False
        self.lineno = lineno

    def open(self):
        self.file = open(self.fnam, "rb")
        self.cnt = 0

    def write(self, fchan):
        self.cnt += 1

        if self.done == False:

            rc = self.file.read(self.blksize)
            if len(rc) > 0:
                fchan.put(rc)

            self.done = len(rc) == 0
            if self.done:
                fchan.hangup()

        return self.done != True

    def close(self):
        self.file.close()


class FiberStreamIO_readline_reader(FiberStreamIO):
    def read(self, fchan):
        return fc_readline(fchan)
