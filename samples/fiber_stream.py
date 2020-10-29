from modext.fiber_stream import FiberChannel, FiberStream
from modext.fiber_stream.stream_util import (
    FiberStreamIO_file_input_writer,
    FiberStreamIO_readline_reader,
)


def sample():

    fc = FiberChannel()  # optional
    fs = FiberStream(channel=fc)  # if no channel given, a default is created
    fiw = FiberStreamIO_file_input_writer("../boot.py", blksize=32)
    fiw.open()
    fs.writer(fiw)

    cnt = 0

    # write to channel, steal away every 3rd line
    while fs.write():
        cnt += 1
        if cnt % 3 == 0:
            # read raw data chunk, default for stream
            print(fs.read())

    print("-" * 37)
    print("read until end with readline")
    print("-" * 37)

    rlr = FiberStreamIO_readline_reader()
    fs.reader(rlr)

    while True:
        # read uses readline io reader to read from channel
        data = fs.read()
        if data == None:
            print(">dense")
            continue
        if len(data) == 0:
            break
        print(data)
